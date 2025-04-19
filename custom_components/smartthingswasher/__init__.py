"""Support for SmartThings Cloud."""

from __future__ import annotations

from collections.abc import Callable
import contextlib
from dataclasses import dataclass
from http import HTTPStatus
import logging
from typing import TYPE_CHECKING, Any, cast

from aiohttp import ClientError
from pysmartthings import (
    Attribute,
    Capability,
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

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_CONNECTIONS,
    ATTR_HW_VERSION,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
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
    OAuth2Session,
    async_get_config_entry_implementation,
)

from .const import (
    CAPABILITIES_WITH_PROGRAMS,
    CONF_INSTALLED_APP_ID,
    CONF_LOCATION_ID,
    CONF_SUBSCRIPTION_ID,
    DOMAIN,
    EVENT_BUTTON,
    MAIN,
    PROGRAM_CYCLE,
    PROGRAM_CYCLE_TYPE,
    PROGRAM_OPTION_DEFAULT,
    PROGRAM_OPTION_OPTIONS,
    PROGRAM_OPTION_RAW,
    PROGRAM_SUPPORTED_OPTIONS,
    SUPPORTEDOPTIONS_LIST,
)
from .models import Program, ProgramOptions, SupportedOption
from .utils import translate_program_course

_LOGGER = logging.getLogger(__name__)


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
    Platform.UPDATE,
    Platform.VALVE,
]


async def async_setup_entry(hass: HomeAssistant, entry: SmartThingsConfigEntry) -> bool:
    """Initialize config entry which represents an installed SmartApp."""
    # The oauth smartthings entry will have a token, older ones are version 3
    # after migration but still require reauthentication
    if CONF_TOKEN not in entry.data:
        raise ConfigEntryAuthFailed("Config entry missing token")
    implementation = await async_get_config_entry_implementation(hass, entry)
    session = OAuth2Session(hass, entry, implementation)

    try:
        await session.async_ensure_token_valid()
    except ClientError as err:
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
            status = process_status(await client.get_device_status(device.device_id))
            programs = process_programs(status)
            device_status[device.device_id] = FullDevice(
                device=device, status=status, programs=programs
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
        if device_id in device_status:
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
    for device in devices.values():
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
        if device.device.parent_device_id:
            kwargs[ATTR_VIA_DEVICE] = (DOMAIN, device.device.parent_device_id)
        if (ocf := device.device.ocf) is not None:
            kwargs.update(
                {
                    ATTR_MANUFACTURER: ocf.manufacturer_name,
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
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device.device.device_id)},
            configuration_url="https://account.smartthings.com",
            name=device.device.label,
            suggested_area=(
                rooms.get(device.device.room_id) if device.device.room_id else None
            ),
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


def process_programs(status: dict[str, ComponentStatus]) -> dict[str, Program]:
    """Build a program list from status."""
    program_list: list[dict[Any]] = {}
    programs: dict[str, Program] = {}
    supported_item: dict[Any] = {}
    supportedoption: SupportedOption
    supportedoption_list: dict[SupportedOption | str, dict[ProgramOptions]] = {}
    program_capabilities_list: dict[Any] = {}
    if (main_component := status.get(MAIN)) is not None:
        for capability in CAPABILITIES_WITH_PROGRAMS:
            if (
                program_capabilities_list := main_component.get(capability)
            ) is not None:
                break
        if not program_capabilities_list:
            if (
                program_capabilities_list := main_component.get(
                    Capability.CUSTOM_SUPPORTED_OPTIONS
                )
            ) is not None:
                program_list = program_capabilities_list[
                    Attribute.SUPPORTED_COURSES
                ].value
                for program in program_list:
                    program_id: str = translate_program_course(program)
                    programs[program_id] = Program(
                        program_id=program_id,
                        program_type="Course",
                        supportedoptions=[],
                        bubblesoak=False,
                    )
            return programs
        program_list = program_capabilities_list[Attribute.SUPPORTED_CYCLES].value
        for program in program_list:
            program_id: str = translate_program_course(program.get(PROGRAM_CYCLE))
            bubblesoak: bool = False
            supportedoption_list = {}
            for supportedoption in SUPPORTEDOPTIONS_LIST:
                support: dict[str, dict[Any]] = program.get(PROGRAM_SUPPORTED_OPTIONS)
                if (supported_item := support.get(supportedoption)) is not None:
                    raw: str = supported_item.get(PROGRAM_OPTION_RAW)
                    default: str = supported_item.get(PROGRAM_OPTION_DEFAULT)
                    options: list[Any] = supported_item.get(PROGRAM_OPTION_OPTIONS)
                    if supportedoption == SupportedOption.BUBBLE_SOAK:
                        bubblesoak = bool(raw[2] == "F")
                    elif default not in options:
                        options.append(default)
                    supportedoption_list[supportedoption] = ProgramOptions(
                        supportedoption=supportedoption,
                        raw=raw,
                        default=default,
                        options=options,
                    )
            programs[program_id] = Program(
                program_id=program_id,
                program_type=program.get(PROGRAM_CYCLE_TYPE),
                supportedoptions=supportedoption_list,
                bubblesoak=bubblesoak,
            )
    return programs
