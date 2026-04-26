"""Support for SmartThings Cloud."""

from __future__ import annotations

from collections.abc import Callable
import contextlib
from dataclasses import dataclass
from http import HTTPStatus
import logging
from typing import TYPE_CHECKING, Any, cast

from aiohttp import ClientResponseError
from pysmartthings import (
    Attribute,
    Capability,
    Category,
    ComponentStatus,
    Device,
    DeviceEvent,
    Lifecycle,
    Scene,
    SmartThings,
    SmartThingsAuthenticationFailedError,
    SmartThingsConnectionError,
    SmartThingsSinkError,
    Status,
)
from pysmartthings.models import HealthStatus

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_CONNECTIONS,
    ATTR_HW_VERSION,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_MODEL_ID,
    ATTR_SERIAL_NUMBER,
    ATTR_SUGGESTED_AREA,
    ATTR_SW_VERSION,
    ATTR_VIA_DEVICE,
    CONF_ACCESS_TOKEN,
    CONF_TOKEN,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import (
    ImplementationUnavailableError,
    OAuth2Session,
    async_get_config_entry_implementation,
)

from .const import (
    CAPABILITIES_WITH_PROGRAMS,
    CAVITY_LOWER,
    CAVITY_SECOND,
    CAVITY_SINGLE,
    CAVITY_UPPER,
    CONF_INSTALLED_APP_ID,
    CONF_LOCATION_ID,
    CONF_SUBSCRIPTION_ID,
    DOMAIN,
    EVENT_BUTTON,
    MAIN,
    PROGRAM_COURSE_NAME,
    PROGRAM_CYCLE,
    PROGRAM_CYCLE_TYPE,
    PROGRAM_MODE,
    PROGRAM_OPTION_DEFAULT,
    PROGRAM_OPTION_MAX,
    PROGRAM_OPTION_MIN,
    PROGRAM_OPTION_OPTIONS,
    PROGRAM_OPTION_RAW,
    PROGRAM_OPTION_SETTABLE,
    PROGRAM_OPTION_STEP,
    PROGRAM_SUPPORTED_OPERATIONS,
    PROGRAM_SUPPORTED_OPTIONS,
)
from .models import CavityMode, CavityType, Program, ProgramOptions, SupportedOption
from .util import (
    get_temperature_unit,
    time_to_minutes,
    translate_oven_mode,
    translate_program_course,
)

_LOGGER = logging.getLogger(__name__)


def format_zigbee_address(address: str) -> str:
    """Format a zigbee address to be more readable."""
    return ":".join(address.lower()[i : i + 2] for i in range(0, 16, 2))


@dataclass
class SmartThingsData:
    """Define an object to hold SmartThings data."""

    devices: dict[str, FullDevice]
    scenes: dict[str, Scene]
    rooms: dict[str, str]
    client: SmartThings


@dataclass
class FullDevice:
    """Define an object to hold device data."""

    device: Device
    status: dict[str, ComponentStatus]
    programs: dict[str, Program]
    modes: dict[CavityType | str, CavityMode]
    online: bool


type SmartThingsConfigEntry = ConfigEntry[SmartThingsData]

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.EVENT,
    Platform.FAN,
    Platform.LIGHT,
    Platform.LOCK,
    Platform.MEDIA_PLAYER,
    Platform.NUMBER,
    Platform.SCENE,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TIME,
    Platform.UPDATE,
    Platform.VACUUM,
    Platform.VALVE,
    Platform.WATER_HEATER,
]


async def async_setup_entry(hass: HomeAssistant, entry: SmartThingsConfigEntry) -> bool:
    """Initialize config entry which represents an installed SmartApp."""
    # The oauth smartthings entry will have a token, older ones are version 3
    # after migration but still require reauthentication
    if CONF_TOKEN not in entry.data:
        raise ConfigEntryAuthFailed("Config entry missing token")
    try:
        implementation = await async_get_config_entry_implementation(hass, entry)
    except ImplementationUnavailableError as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="oauth2_implementation_unavailable",
        ) from err
    session = OAuth2Session(hass, entry, implementation)

    try:
        await session.async_ensure_token_valid()
    except ClientResponseError as err:
        if err.status == HTTPStatus.BAD_REQUEST:
            raise ConfigEntryAuthFailed("Token not valid, trigger renewal") from err
        raise ConfigEntryNotReady from err

    client = SmartThings(session=async_get_clientsession(hass))

    async def _refresh_token() -> str:
        await session.async_ensure_token_valid()
        token = session.token[CONF_ACCESS_TOKEN]
        if TYPE_CHECKING:
            assert isinstance(token, str)
        return token

    client.refresh_token_function = _refresh_token

    def _handle_max_connections() -> None:
        _LOGGER.debug(
            "We hit the limit of max connections or we could not remove the old one, so retrying"
        )
        hass.config_entries.async_schedule_reload(entry.entry_id)

    client.max_connections_reached_callback = _handle_max_connections

    def _handle_new_subscription_identifier(identifier: str | None) -> None:
        """Handle a new subscription identifier."""
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_SUBSCRIPTION_ID: identifier,
            },
        )
        if identifier is not None:
            _LOGGER.debug("Updating subscription ID to %s", identifier)
        else:
            _LOGGER.debug("Removing subscription ID")

    client.new_subscription_id_callback = _handle_new_subscription_identifier

    if (old_identifier := entry.data.get(CONF_SUBSCRIPTION_ID)) is not None:
        _LOGGER.debug("Trying to delete old subscription %s", old_identifier)
        try:
            await client.delete_subscription(old_identifier)
        except SmartThingsConnectionError as err:
            raise ConfigEntryNotReady("Could not delete old subscription") from err

    _LOGGER.debug("Trying to create a new subscription")
    try:
        subscription = await client.create_subscription(
            entry.data[CONF_LOCATION_ID],
            entry.data[CONF_TOKEN][CONF_INSTALLED_APP_ID],
        )
    except SmartThingsSinkError as err:
        _LOGGER.exception("Couldn't create a new subscription")
        raise ConfigEntryNotReady from err
    subscription_id = subscription.subscription_id
    _handle_new_subscription_identifier(subscription_id)

    entry.async_create_background_task(
        hass,
        client.subscribe(
            entry.data[CONF_LOCATION_ID],
            entry.data[CONF_TOKEN][CONF_INSTALLED_APP_ID],
            subscription,
        ),
        "smartthings_socket",
    )

    device_status: dict[str, FullDevice] = {}
    try:
        rooms = {
            room.room_id: room.name
            for room in await client.get_rooms(location_id=entry.data[CONF_LOCATION_ID])
        }
        devices = await client.get_devices()
        for device in devices:
            if (
                (main_component := device.components.get(MAIN)) is not None
                and main_component.manufacturer_category is Category.BLUETOOTH_TRACKER
            ):
                device_status[device.device_id] = FullDevice(
                    device=device,
                    status={},
                    programs={},
                    modes={},
                    online=True,
                )
                continue
            status = process_status(await client.get_device_status(device.device_id))
            programs = process_programs(status)
            oven_modes = set_oven_modes(status)
            online = await client.get_device_health(device.device_id)
            device_status[device.device_id] = FullDevice(
                device=device,
                status=status,
                programs=programs,
                modes=oven_modes,
                online=online.state == HealthStatus.ONLINE,
            )
    except SmartThingsAuthenticationFailedError as err:
        raise ConfigEntryAuthFailed from err

    device_registry = dr.async_get(hass)
    create_devices(device_registry, device_status, entry, rooms)

    scenes = {
        scene.scene_id: scene
        for scene in await client.get_scenes(location_id=entry.data[CONF_LOCATION_ID])
    }

    def handle_deleted_device(device_id: str) -> None:
        """Handle a deleted device."""
        dev_entry = device_registry.async_get_device(
            identifiers={(DOMAIN, device_id)},
        )
        if dev_entry is not None:
            device_registry.async_update_device(
                dev_entry.id, remove_config_entry_id=entry.entry_id
            )

    entry.async_on_unload(
        client.add_device_lifecycle_event_listener(
            Lifecycle.DELETE, handle_deleted_device
        )
    )

    entry.runtime_data = SmartThingsData(
        devices={
            device_id: device
            for device_id, device in device_status.items()
            if MAIN in device.status
        },
        client=client,
        scenes=scenes,
        rooms=rooms,
    )

    # Events are deprecated and will be removed in 2025.10
    def handle_button_press(event: DeviceEvent) -> None:
        """Handle a button press."""
        if (
            event.capability is Capability.BUTTON
            and event.attribute is Attribute.BUTTON
        ):
            hass.bus.async_fire(
                EVENT_BUTTON,
                {
                    "component_id": event.component_id,
                    "device_id": event.device_id,
                    "location_id": event.location_id,
                    "value": event.value,
                    "name": entry.runtime_data.devices[event.device_id].device.label,
                    "data": event.data,
                },
            )

    entry.async_on_unload(
        client.add_unspecified_device_event_listener(handle_button_press)
    )

    async def _handle_shutdown(_: Event) -> None:
        """Handle shutdown."""
        await client.delete_subscription(subscription_id)

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _handle_shutdown)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    device_entries = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    for device_entry in device_entries:
        device_id = next(
            identifier[1]
            for identifier in device_entry.identifiers
            if identifier[0] == DOMAIN
        )
        if any(
            device_id.startswith(device_identifier)
            for device_identifier in device_status
        ):
            continue
        device_registry.async_update_device(
            device_entry.id, remove_config_entry_id=entry.entry_id
        )

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SmartThingsConfigEntry
) -> bool:
    """Unload a config entry."""
    client = entry.runtime_data.client
    if (subscription_id := entry.data.get(CONF_SUBSCRIPTION_ID)) is not None:
        with contextlib.suppress(SmartThingsConnectionError):
            await client.delete_subscription(subscription_id)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def create_devices(
    device_registry: dr.DeviceRegistry,
    devices: dict[str, FullDevice],
    entry: SmartThingsConfigEntry,
    rooms: dict[str, str],
) -> None:
    """Create devices in the device registry."""
    for device in sorted(
        devices.values(), key=lambda d: d.device.parent_device_id or ""
    ):
        kwargs: dict[str, Any] = {}
        if device.device.hub is not None:
            kwargs = {
                ATTR_SW_VERSION: device.device.hub.firmware_version,
                ATTR_MODEL: device.device.hub.hardware_type,
            }
            if device.device.hub.mac_address:
                kwargs[ATTR_CONNECTIONS] = {
                    (dr.CONNECTION_NETWORK_MAC, device.device.hub.mac_address)
                }
            if device.device.hub.hub_eui:
                connections = kwargs.setdefault(ATTR_CONNECTIONS, set())
                connections.add(
                    (
                        dr.CONNECTION_ZIGBEE,
                        format_zigbee_address(device.device.hub.hub_eui),
                    )
                )
        if device.device.parent_device_id and device.device.parent_device_id in devices:
            kwargs[ATTR_VIA_DEVICE] = (DOMAIN, device.device.parent_device_id)
        if (ocf := device.device.ocf) is not None:
            kwargs.update(
                {
                    ATTR_MANUFACTURER: ocf.manufacturer_name,
                    ATTR_MODEL_ID: ocf.model_code,
                    ATTR_MODEL: (
                        (ocf.model_number.split("|")[0]) if ocf.model_number else None
                    ),
                    ATTR_HW_VERSION: ocf.hardware_version,
                    ATTR_SW_VERSION: ocf.firmware_version,
                }
            )
        if (viper := device.device.viper) is not None:
            kwargs.update(
                {
                    ATTR_MANUFACTURER: viper.manufacturer_name,
                    ATTR_MODEL: viper.model_name,
                    ATTR_HW_VERSION: viper.hardware_version,
                    ATTR_SW_VERSION: viper.software_version,
                }
            )
        if (zigbee := device.device.zigbee) is not None:
            kwargs[ATTR_CONNECTIONS] = {
                (dr.CONNECTION_ZIGBEE, format_zigbee_address(zigbee.eui))
            }
        if (matter := device.device.matter) is not None:
            kwargs.update(
                {
                    ATTR_HW_VERSION: matter.hardware_version,
                    ATTR_SW_VERSION: matter.software_version,
                    ATTR_SERIAL_NUMBER: matter.serial_number,
                }
            )
        if (main_component := device.status.get(MAIN)) is not None:
            if (
                device_identification := main_component.get(
                    Capability.SAMSUNG_CE_DEVICE_IDENTIFICATION
                )
            ) is not None:
                new_kwargs = {
                    ATTR_SERIAL_NUMBER: device_identification[
                        Attribute.SERIAL_NUMBER
                    ].value
                }
                if ATTR_MODEL_ID not in kwargs:
                    new_kwargs[ATTR_MODEL_ID] = device_identification[
                        Attribute.MODEL_NAME
                    ].value
                kwargs.update(new_kwargs)
            if (
                device_status := main_component.get(Capability.SAMSUNG_IM_DEVICESTATUS)
            ) is not None:
                mac_connections: set[tuple[str, str]] = set()
                status = cast(dict[str, str], device_status[Attribute.STATUS].value)
                if wifi_mac := status.get("wifiMac"):
                    mac_connections.add((dr.CONNECTION_NETWORK_MAC, wifi_mac))
                if bluetooth_address := status.get("btAddr"):
                    mac_connections.add(
                        (dr.CONNECTION_BLUETOOTH, bluetooth_address.lower())
                    )
                if mac_connections:
                    kwargs.setdefault(ATTR_CONNECTIONS, set()).update(mac_connections)
        if (
            device_registry.async_get_device({(DOMAIN, device.device.device_id)})
            is None
        ):
            kwargs.update(
                {
                    ATTR_SUGGESTED_AREA: (
                        rooms.get(device.device.room_id)
                        if device.device.room_id
                        else None
                    )
                }
            )
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device.device.device_id)},
            configuration_url="https://account.smartthings.com",
            name=device.device.label,
            **kwargs,
        )


KEEP_CAPABILITY_QUIRK: dict[
    Capability | str, Callable[[dict[Attribute | str, Status]], bool]
] = {
    Capability.DRYER_OPERATING_STATE: (
        lambda status: status[Attribute.SUPPORTED_MACHINE_STATES].value is not None
    ),
    Capability.WASHER_OPERATING_STATE: (
        lambda status: status[Attribute.SUPPORTED_MACHINE_STATES].value is not None
    ),
    Capability.DEMAND_RESPONSE_LOAD_CONTROL: lambda _: True,
    Capability.SAMSUNG_CE_AIR_CONDITIONER_LIGHTING: (
        lambda status: status[Attribute.LIGHTING].value is not None
    ),
    Capability.SAMSUNG_CE_AIR_CONDITIONER_BEEP: (
        lambda status: status[Attribute.BEEP].value is not None
    ),
}


def process_status(status: dict[str, ComponentStatus]) -> dict[str, ComponentStatus]:
    """Remove disabled capabilities from status."""
    if (main_component := status.get(MAIN)) is None:
        return status
    if (
        disabled_components_capability := main_component.get(
            Capability.CUSTOM_DISABLED_COMPONENTS
        )
    ) is not None:
        disabled_components = cast(
            list[str],
            disabled_components_capability[Attribute.DISABLED_COMPONENTS].value,
        )
        if disabled_components is not None:
            for component in disabled_components:
                # Burner components are named burner-06
                # but disabledComponents contain burner-6
                if "burner" in component:
                    burner_id = int(component.split("-")[-1])
                    component = f"burner-0{burner_id}"
                if component in status:
                    del status[component]
    for component_status in status.values():
        process_component_status(component_status)
    return status


def process_component_status(status: ComponentStatus) -> None:
    """Remove disabled capabilities from component status."""
    if (
        disabled_capabilities_capability := status.get(
            Capability.CUSTOM_DISABLED_CAPABILITIES
        )
    ) is not None:
        disabled_capabilities = cast(
            list[Capability | str],
            disabled_capabilities_capability[Attribute.DISABLED_CAPABILITIES].value,
        )
        if disabled_capabilities is not None:
            for capability in disabled_capabilities:
                if capability in status and (
                    capability not in KEEP_CAPABILITY_QUIRK
                    or not KEEP_CAPABILITY_QUIRK[capability](status[capability])
                ):
                    del status[capability]


def set_oven_modes(
    status: dict[str, ComponentStatus],
) -> dict[CavityType | str, CavityMode]:
    """Set oven modes based on cavity type."""
    if (main_component := status.get(MAIN)) is None:
        return {}
    if main_component.get(Capability.SAMSUNG_CE_KITCHEN_MODE_SPECIFICATION) is None:
        return {}
    return {
        cavity: CavityMode(cavity_id=cavity, active_mode="no_operation")
        for cavity in [
            CavityType.SINGLE,
            CavityType.UPPER,
            CavityType.LOWER,
            CavityType.SECOND,
        ]
    }


def _parse_oven_options(
    supported_options: dict[str, Any], unit: str
) -> dict[str, ProgramOptions]:
    """Parse oven-specific options like temperature and time based on the detected unit."""
    supported_options_list = {}

    if SupportedOption.TEMPERATURE in supported_options:
        temp_spec = supported_options[SupportedOption.TEMPERATURE]
        available_units = [u for u in ["C", "F"] if u in temp_spec]
        if len(available_units) == 1:
            unit = available_units[0]
        if unit in temp_spec:
            temp_data = temp_spec[unit]
            default_val = temp_data.get(
                PROGRAM_OPTION_DEFAULT, 180 if unit == "C" else 350
            )
            min_val = float(
                temp_data.get(PROGRAM_OPTION_MIN, 30 if unit == "C" else 80)
            )
            max_val = float(
                temp_data.get(PROGRAM_OPTION_MAX, 250 if unit == "C" else 500)
            )
            supported_options_list[SupportedOption.TEMPERATURE] = ProgramOptions(
                supportedoption=SupportedOption.TEMPERATURE,
                default=default_val,
                options=[],
                selected_value=default_val,
                min_value=min_val,
                max_value=max_val,
                step_value=float(temp_data.get(PROGRAM_OPTION_STEP, 5)),
                unit=unit,
            )

    if SupportedOption.OPERATION_TIME in supported_options:
        if time_data := supported_options[SupportedOption.OPERATION_TIME]:
            supported_options_list[SupportedOption.OPERATION_TIME] = ProgramOptions(
                supportedoption=SupportedOption.OPERATION_TIME,
                default=time_to_minutes(
                    time_data.get(PROGRAM_OPTION_DEFAULT, "01:00:00")
                ),
                options=[],
                selected_value=time_to_minutes(
                    time_data.get(PROGRAM_OPTION_DEFAULT, "01:00:00")
                ),
                min_value=float(
                    time_to_minutes(time_data.get(PROGRAM_OPTION_MIN, "00:01:00"))
                ),
                max_value=float(
                    time_to_minutes(time_data.get(PROGRAM_OPTION_MAX, "23:59:00"))
                ),
                step_value=float(
                    time_to_minutes(time_data.get(PROGRAM_OPTION_STEP, "00:01:00"))
                ),
            )

    return supported_options_list


def _process_oven_programs(status: dict[str, ComponentStatus]) -> dict[str, Program]:
    """Specifieke verwerking voor Ovens (Dual Cook & Single)."""
    programs: dict[str, Program] = {}

    unit = get_temperature_unit(status)
    oven_component_mapping = {MAIN: CAVITY_SINGLE, "cavity-02": CAVITY_SECOND}
    for comp_id, target_cavity in oven_component_mapping.items():
        if (comp_status := status.get(comp_id)) is None:
            continue

        spec_status = comp_status.get(Capability.SAMSUNG_CE_KITCHEN_MODE_SPECIFICATION)
        if spec_status is None:
            continue

        spec_data = cast(dict[str, Any], spec_status[Attribute.SPECIFICATION].value)
        specification: dict[str, list[dict[str, Any]]] = {}
        if isinstance(spec_data, list):
            specification = {target_cavity: spec_data}
        elif isinstance(spec_data, dict):
            if comp_id == "cavity-02" and CAVITY_SINGLE in spec_data:
                specification = {CAVITY_SECOND: spec_data[CAVITY_SINGLE]}
            elif any(
                key in spec_data for key in [CAVITY_SINGLE, CAVITY_UPPER, CAVITY_LOWER]
            ):
                specification = cast(dict[str, list[dict[str, Any]]], spec_data)
            else:
                for key, value in spec_data.items():
                    if isinstance(value, list):
                        specification[key] = value
        for cavity_key, mode_list in specification.items():
            for mode_data in mode_list:
                if PROGRAM_MODE not in mode_data:
                    continue

                mode_name = mode_data[PROGRAM_MODE]
                program_id = translate_oven_mode(mode_name, cavity_key)
                supported_ops = mode_data.get(PROGRAM_SUPPORTED_OPERATIONS, [])
                can_start = "start" in supported_ops
                supported_options = mode_data.get(PROGRAM_SUPPORTED_OPTIONS, {})
                supported_options_list = _parse_oven_options(supported_options, unit)
                programs[program_id] = Program(
                    program_id=program_id,
                    program_type="OvenMode",
                    supportedoptions=supported_options_list,
                    supports_start=can_start,
                )
            no_operation_id = f"{cavity_key}_no_operation"
            if no_operation_id not in programs:
                programs[no_operation_id] = Program(
                    program_id=no_operation_id,
                    program_type="OvenMode",
                    supportedoptions={},
                    supports_start=False,
                )

    return programs


def process_programs(status: dict[str, ComponentStatus]) -> dict[str, Program]:
    """Build a program list from status."""
    programs: dict[str, Program] = {}

    if (main_component := status.get(MAIN)) is None:
        return programs

    for capability in CAPABILITIES_WITH_PROGRAMS:
        if (program_capabilities_list := main_component.get(capability)) is not None:
            break

    if program_capabilities_list is None:
        if (
            capability_status := main_component.get(Capability.CUSTOM_SUPPORTED_OPTIONS)
        ) is not None:
            program_list = cast(
                list[str], capability_status[Attribute.SUPPORTED_COURSES].value
            )
            for program in program_list:
                program_id: str = translate_program_course(program)
                programs[program_id] = Program(
                    program_id=program_id,
                    program_type="Course",
                    supportedoptions={},
                )
        return programs

    if main_component.get(Capability.SAMSUNG_CE_KITCHEN_MODE_SPECIFICATION) is not None:
        """Build oven programs."""
        programs = _process_oven_programs(status)

    elif (
        predefined := program_capabilities_list.get(Attribute.PREDEFINED_COURSES)
    ) is not None:
        """Build dishwasher programs."""
        course_list = cast(list[dict[str, Any]], predefined.value)
        for course in course_list:
            program_id: str = translate_program_course(course.get(PROGRAM_COURSE_NAME))
            supported_options_list = {}
            supported_options = course.get(PROGRAM_OPTION_OPTIONS, {})
            for opt_key, opt_data in supported_options.items():
                default = str(opt_data.get(PROGRAM_OPTION_DEFAULT))
                options = opt_data.get(PROGRAM_OPTION_SETTABLE, [default])
                if default not in options:
                    options.append(default)
                supported_options_list[opt_key] = ProgramOptions(
                    supportedoption=opt_key,
                    raw="N/A",
                    default=default,
                    options=options,
                )
            programs[program_id] = Program(
                program_id=program_id,
                program_type="Course",
                supportedoptions=supported_options_list,
            )

    elif (
        supported := program_capabilities_list.get(Attribute.SUPPORTED_CYCLES)
    ) is not None:
        """Build dryer/washer programs."""
        cycle_list = cast(list[dict[str, Any]], supported.value)
        for cycle in cycle_list:
            program_id: str = translate_program_course(cycle.get(PROGRAM_CYCLE))
            supportedoption_list = {}
            supported_options = cycle.get(PROGRAM_SUPPORTED_OPTIONS, {})
            for opt_key, opt_data in supported_options.items():
                raw = str(opt_data.get(PROGRAM_OPTION_RAW))
                default = str(opt_data.get(PROGRAM_OPTION_DEFAULT))
                options = opt_data.get(PROGRAM_OPTION_OPTIONS, [default])
                if default not in options:
                    options.append(default)
                supportedoption_list[opt_key] = ProgramOptions(
                    supportedoption=opt_key,
                    raw=raw,
                    default=default,
                    options=options,
                )
            programs[program_id] = Program(
                program_id=program_id,
                program_type=str(cycle.get(PROGRAM_CYCLE_TYPE)),
                supportedoptions=supportedoption_list,
            )

    return programs
