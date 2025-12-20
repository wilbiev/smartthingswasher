"""Support for numbers through the SmartThings cloud API."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, SmartThingsConfigEntry
from .const import MAIN, UNIT_MAP
from .entity import SmartThingsEntity
from .models import STType


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
    component_fn: Callable[[str], bool] | None = None
    component_translation_key: dict[str, str] | None = None


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
    Capability.THERMOSTAT_COOLING_SETPOINT: {
        Attribute.COOLING_SETPOINT: [
            SmartThingsNumberEntityDescription(
                key=Capability.THERMOSTAT_COOLING_SETPOINT,
                entity_category=EntityCategory.CONFIG,
                device_class = NumberDeviceClass.TEMPERATURE,
                component_fn=lambda component: component in {"freezer", "cooler", "onedoor"},
                component_translation_key={
                    "freezer": "freezer_temperature",
                    "cooler": "cooler_temperature",
                    "onedoor": "target_temperature",
                },
                use_temperature_unit=True,
                command=Command.SET_COOLING_SETPOINT,
                range_attribute=Attribute.COOLING_SETPOINT_RANGE,
                int_type=STType.FLOAT,
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
        if self.entity_description.min_attribute and self.entity_description.max_attribute:
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
        if self.entity_description.min_attribute and self.entity_description.max_attribute:
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
        if self.entity_description.min_attribute and self.entity_description.max_attribute:
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
        if self.entity_description.use_temperature_unit:
            if (unit := self._internal_state[self.capability][self._attribute].unit) is not None:
                return UNIT_MAP[unit]
        return self.entity_description.native_unit_of_measurement


    @property
    def native_value(self) -> str | float | datetime | int | None:
        """Return the state of the number."""
        if self._number is None:
            return None

        return self.get_attribute_value(self.capability, self._attribute)


    async def async_set_native_value(self, value: float) -> int | float | str | None:
        """Set new value."""
        if self._number is None:
            raise RuntimeError("Cannot set value, device doesn't provide type data")

        if self.command is not None and value is not None:
            if self._number is STType.INTEGER:
                await self.execute_device_command(
                    self.capability,
                    self.command,
                    int(value),
                )
            elif self._number is STType.FLOAT:
                await self.execute_device_command(
                    self.capability,
                    self.command,
                    str(value),
                )
            else:
                await self.execute_device_command(
                    self.capability,
                    self.command,
                    str(int(value)),
                )
