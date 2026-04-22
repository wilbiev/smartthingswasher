"""Support for numbers through the SmartThings cloud API."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, SmartThingsConfigEntry
from .const import MAIN, UNIT_MAP
from .entity import SmartThingsEntity
from .models import ProgramOptions, STType, SupportedOption
from .util import (
    get_current_cavity_id,
    get_temperature_unit,
    time_to_minutes,
    translate_oven_mode,
)


@dataclass(frozen=True, kw_only=True)
class SmartThingsNumberEntityDescription(NumberEntityDescription):
    """Describe a SmartThings select entity."""

    unique_id_separator: str = "."
    options_attribute: Attribute | None = None
    command: Command | None = None
    except_if_state_none: bool = False
    int_type: STType | None = None
    min_attribute: Attribute | None = None
    max_attribute: Attribute | None = None
    range_attribute: Attribute | None = None
    use_temperature_unit: bool = False
    capability_ignore_list: list[set[Capability]] | None = None
    component_fn: Callable[[str], bool] | None = None
    component_translation_key: dict[str, str] | None = None
    value_fn: Callable[[Any], float | int | None] | None = None
    action_fn: Callable[[float], Any] | None = None
    supported_option: SupportedOption | None = None


CAPABILITY_TO_NUMBERS: dict[
    Capability, dict[Attribute, list[SmartThingsNumberEntityDescription]]
] = {
    Capability.SAMSUNG_CE_DRYER_DELAY_END: {
        Attribute.REMAINING_TIME: [
            SmartThingsNumberEntityDescription(
                key=Capability.SAMSUNG_CE_DRYER_DELAY_END,
                translation_key="delay_time",
                entity_category=EntityCategory.CONFIG,
                native_unit_of_measurement=UnitOfTime.MINUTES,
                command=Command.SET_DELAY_TIME,
                native_min_value=0,
                native_max_value=1440,
                native_step=5,
                int_type=STType.INTEGER,
            )
        ]
    },
    Capability.SAMSUNG_CE_STEAM_CLOSET_DELAY_END: {
        Attribute.REMAINING_TIME: [
            SmartThingsNumberEntityDescription(
                key=Capability.SAMSUNG_CE_STEAM_CLOSET_DELAY_END,
                translation_key="delay_time",
                entity_category=EntityCategory.CONFIG,
                native_unit_of_measurement=UnitOfTime.MINUTES,
                command=Command.SET_DELAY_TIME,
                native_min_value=0,
                native_max_value=1440,
                native_step=5,
                int_type=STType.INTEGER,
            )
        ]
    },
    Capability.SAMSUNG_CE_WASHER_DELAY_END: {
        Attribute.REMAINING_TIME: [
            SmartThingsNumberEntityDescription(
                key=Capability.SAMSUNG_CE_WASHER_DELAY_END,
                translation_key="delay_time",
                entity_category=EntityCategory.CONFIG,
                native_unit_of_measurement=UnitOfTime.MINUTES,
                command=Command.SET_DELAY_TIME,
                native_min_value=0,
                native_max_value=1440,
                native_step=5,
                int_type=STType.INTEGER,
            )
        ]
    },
    Capability.CUSTOM_DISHWASHER_DELAY_START_TIME: {
        Attribute.DISHWASHER_DELAY_START_TIME: [
            SmartThingsNumberEntityDescription(
                key=Capability.CUSTOM_DISHWASHER_DELAY_START_TIME,
                translation_key="delay_time",
                entity_category=EntityCategory.CONFIG,
                native_unit_of_measurement=UnitOfTime.MINUTES,
                command=Command.SET_DISHWASHER_DELAY_START_TIME,
                native_min_value=0,
                native_max_value=1440,
                native_step=30,
                value_fn=lambda val: (
                    time_to_minutes(val)
                    if isinstance(val, str)
                    else (float(val) if isinstance(val, (int, float)) else None)
                ),
                action_fn=lambda val: f"{int(val) // 60:02d}:{int(val) % 60:02d}:00",
                int_type=STType.INTEGER,
            )
        ]
    },
    Capability.THERMOSTAT_COOLING_SETPOINT: {
        Attribute.COOLING_SETPOINT: [
            SmartThingsNumberEntityDescription(
                key=Capability.THERMOSTAT_COOLING_SETPOINT,
                entity_category=EntityCategory.CONFIG,
                device_class=NumberDeviceClass.TEMPERATURE,
                component_fn=lambda component: component
                in {"freezer", "cooler", "onedoor"},
                component_translation_key={
                    "freezer": "freezer_temperature",
                    "cooler": "cooler_temperature",
                    "onedoor": "target_temperature",
                },
                use_temperature_unit=True,
                command=Command.SET_COOLING_SETPOINT,
                range_attribute=Attribute.COOLING_SETPOINT_RANGE,
                int_type=STType.INTEGER,
            )
        ]
    },
    Capability.SAMSUNG_CE_HOOD_FAN_SPEED: {
        Attribute.HOOD_FAN_SPEED: [
            SmartThingsNumberEntityDescription(
                key=Capability.SAMSUNG_CE_HOOD_FAN_SPEED,
                translation_key="hood_fan_speed",
                entity_category=EntityCategory.CONFIG,
                command=Command.SET_HOOD_FAN_SPEED,
                min_attribute=Attribute.SETTABLE_MIN_FAN_SPEED,
                max_attribute=Attribute.SETTABLE_MAX_FAN_SPEED,
                native_step=1.0,
                int_type=STType.FLOAT,
            )
        ]
    },
}

OVEN_OPTIONS_TO_NUMBERS: dict[
    Capability, dict[Attribute, list[SmartThingsNumberEntityDescription]]
] = {
    Capability.OVEN_SETPOINT: {
        Attribute.OVEN_SETPOINT: [
            SmartThingsNumberEntityDescription(
                key=Attribute.OVEN_SETPOINT,
                translation_key="oven_temperature",
                entity_category=EntityCategory.CONFIG,
                device_class=NumberDeviceClass.TEMPERATURE,
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "oven_temperature_cavity_01",
                    "cavity-02": "oven_temperature_cavity_02",
                },
                use_temperature_unit=True,
                supported_option=SupportedOption.TEMPERATURE,
                command=Command.SET_OVEN_SETPOINT,
                int_type=STType.INTEGER,
            )
        ],
    },
    Capability.SAMSUNG_CE_OVEN_OPERATING_STATE: {
        Attribute.OPERATION_TIME: [
            SmartThingsNumberEntityDescription(
                key=SupportedOption.OPERATION_TIME,
                translation_key="oven_operation_time",
                entity_category=EntityCategory.CONFIG,
                device_class=NumberDeviceClass.DURATION,
                native_unit_of_measurement=UnitOfTime.MINUTES,
                value_fn=lambda val: (
                    time_to_minutes(val)
                    if isinstance(val, str)
                    else (float(val) if isinstance(val, (int, float)) else None)
                ),
                action_fn=lambda val: f"{int(val) // 60:02d}:{int(val) % 60:02d}:00",
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "oven_operation_time_cavity_01",
                    "cavity-02": "oven_operation_time_cavity_02",
                },
                supported_option=SupportedOption.OPERATION_TIME,
                command=Command.SET_OPERATION_TIME,
            )
        ],
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartThingsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add switches for a config entry."""
    entry_data = entry.runtime_data
    async_add_entities(
        SmartThingsNumber(
            entry_data.client,
            device,
            description,
            capability,
            attribute,
            component,
        )
        for device in entry_data.devices.values()
        for capability, attributes in CAPABILITY_TO_NUMBERS.items()
        for component in device.status
        if capability in device.status[component]
        for attribute, descriptions in attributes.items()
        for description in descriptions
    )
    async_add_entities(
        SmartThingsOvenOptionNumber(
            entry_data.client,
            device,
            description,
            capability,
            attribute,
            component,
        )
        for device in entry_data.devices.values()
        if device.programs is not None
        for capability, support_options in OVEN_OPTIONS_TO_NUMBERS.items()
        for component, capabilities in device.status.items()
        if capability in capabilities
        for attribute, descriptions in support_options.items()
        for description in descriptions
        if (
            component == MAIN
            or (
                description.component_fn is not None
                and description.component_fn(component)
            )
        )
        and not (
            description.capability_ignore_list
            and any(
                all(ignore_cap in capabilities for ignore_cap in ignore_cap_list)
                for ignore_cap_list in description.capability_ignore_list
            )
        )
    )


class SmartThingsNumber(SmartThingsEntity, NumberEntity):
    """Define a SmartThings select."""

    entity_description: SmartThingsNumberEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsNumberEntityDescription,
        capability: Capability,
        attribute: Attribute,
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        super().__init__(client, device, {capability}, component=component)
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{entity_description.key}"
        self._attribute = attribute
        self.capability = capability
        self.entity_description = entity_description
        self.command = self.entity_description.command
        self._number = self.entity_description.int_type
        if self.entity_description.component_translation_key and component != MAIN:
            self._attr_translation_key = (
                self.entity_description.component_translation_key[component]
            )

    @property
    def options(self) -> list[int] | None:
        """Return the list of options."""
        if (
            self.entity_description.min_attribute
            and self.entity_description.max_attribute
        ):
            min_value_list = self.get_attribute_value(
                self.capability, self.entity_description.min_attribute
            )
            max_value_list = self.get_attribute_value(
                self.capability, self.entity_description.max_attribute
            )
            return list(range(min_value_list, max_value_list + 1))
        return None

    @property
    def range(self) -> dict[str, int] | None:
        """Return the range."""
        if self.entity_description.range_attribute:
            return self.get_attribute_value(
                self.capability,
                self.entity_description.range_attribute,
            )
        return None

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        if (
            self.entity_description.min_attribute
            and self.entity_description.max_attribute
        ):
            if self.options is None:
                return 0
            return min(self.options)
        if self.entity_description.range_attribute:
            if self.range is None:
                return 0
            return self.range["minimum"]
        if self.entity_description.min_attribute:
            return self.get_attribute_value(
                self.capability, self.entity_description.min_attribute
            )
        if self.entity_description.native_min_value is None:
            return 0
        return self.entity_description.native_min_value

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        if (
            self.entity_description.min_attribute
            and self.entity_description.max_attribute
        ):
            if self.options is None:
                return 0
            return max(self.options)
        if self.entity_description.range_attribute:
            if self.range is None:
                return 0
            return self.range["maximum"]
        if self.entity_description.max_attribute:
            return self.get_attribute_value(
                self.capability, self.entity_description.max_attribute
            )
        if self.entity_description.native_max_value is None:
            return 0
        return self.entity_description.native_max_value

    @property
    def native_step(self) -> float:
        """Return the step value."""
        if self.entity_description.range_attribute:
            if self.range is None:
                return 1.0
            return self.range["step"]
        if self.entity_description.native_step is None:
            return 1.0
        return self.entity_description.native_step

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit this state is expressed in."""
        unit = None
        if self.entity_description.use_temperature_unit:
            state_attr = self._internal_state[self.capability][self._attribute]
            unit = getattr(state_attr, "unit", None)
            if unit is None:
                unit = get_temperature_unit(self.device.status)
        if unit:
            return UNIT_MAP.get(unit)
        return self.entity_description.native_unit_of_measurement

    @property
    def native_value(self) -> float | int | None:
        """Return the state of the number."""
        if self._number is None:
            return None

        raw_val = self.get_attribute_value(self.capability, self._attribute)
        if raw_val is None:
            return None

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(raw_val)

        return raw_val

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self.command is None or value is None:
            return

        if self.entity_description.action_fn:
            command_value = self.entity_description.action_fn(value)
        elif self._number is STType.INTEGER:
            command_value = int(value)
        elif self._number is STType.FLOAT:
            command_value = str(value)
        else:
            command_value = str(int(value))

        await self.execute_device_command(
            self.capability,
            self.command,
            command_value,
        )


class SmartThingsOvenOptionNumber(SmartThingsEntity, NumberEntity):
    """Defines a number entity for oven options."""

    entity_description: SmartThingsNumberEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsNumberEntityDescription,
        capability: Capability,
        attribute: Attribute,
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        capabilities = {capability}
        capabilities.add(Capability.SAMSUNG_CE_OVEN_MODE)
        capabilities.add(Capability.SAMSUNG_CE_KITCHEN_MODE_SPECIFICATION)
        capabilities.add(Capability.CUSTOM_OVEN_CAVITY_STATUS)
        capabilities.add(Capability.REMOTE_CONTROL_STATUS)
        super().__init__(client, device, capabilities, component=component)
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{entity_description.key}"
        self._attribute = attribute
        self.capability = capability
        self.entity_description = entity_description
        self.command = self.entity_description.command
        self._number = self.entity_description.int_type
        if (
            self.entity_description.component_translation_key
            and component in self.entity_description.component_translation_key
        ):
            self._attr_translation_key = (
                self.entity_description.component_translation_key[component]
            )
        if entity_description.key == SupportedOption.OPERATION_TIME:
            self._attr_mode = NumberMode.BOX
        else:
            self._attr_mode = NumberMode.SLIDER

    @property
    def _active_option(self) -> ProgramOptions | None:
        """Helper to find the ProgramOptions for the current mode."""
        if self.device.programs is None:
            return None
        cavity_key = get_current_cavity_id(self.device.status, self.component)
        current_mode = self.get_attribute_value(
            Capability.SAMSUNG_CE_OVEN_MODE,
            Attribute.OVEN_MODE,
            component=self.component,
        )
        if not current_mode:
            return None
        lookup_id = translate_oven_mode(current_mode, cavity_key)
        if program := self.device.programs.get(lookup_id):
            if (
                self.entity_description.supported_option
                and self.entity_description.supported_option in program.supportedoptions
            ):
                return program.supportedoptions[
                    self.entity_description.supported_option
                ]
        return None

    @property
    def native_value(self) -> float | None:
        """Get the selected value from the program model."""
        if self._number is None:
            return None

        raw_val = self.get_attribute_value(self.capability, self._attribute)
        if raw_val is None:
            return None

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(raw_val)

        return raw_val

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        if (option := self._active_option) and option.min_value is not None:
            return option.min_value
        return 0.0

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        if (option := self._active_option) and option.max_value is not None:
            return option.max_value
        return 100.0

    @property
    def native_step(self) -> float:
        """Return the increment step."""
        if (option := self._active_option) and option.step_value is not None:
            return option.step_value
        return 1.0

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit this state is expressed in."""
        if self.entity_description.use_temperature_unit:
            if option := self._active_option:
                if option.unit is not None:
                    return UNIT_MAP[option.unit]
        return self.entity_description.native_unit_of_measurement

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self.command is None or value is None:
            return

        if self.entity_description.action_fn:
            command_value = self.entity_description.action_fn(value)
        elif self._number is STType.INTEGER:
            command_value = int(value)
        elif self._number is STType.FLOAT:
            command_value = str(value)
        else:
            command_value = str(int(value))

        await self.execute_device_command(
            self.capability,
            self.command,
            command_value,
        )

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def update_state(new_mode: str) -> None:
            """Update the entity when the oven mode changes."""
            self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"smartthings_oven_mode_changed_{self.device.device.device_id}",
                update_state,
            )
        )
