"""Support for switches through the SmartThings cloud API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, SmartThingsConfigEntry
from .const import MAIN
from .entity import SmartThingsEntity


@dataclass(frozen=True, kw_only=True)
class SmartThingsSelectEntityDescription(SelectEntityDescription):
    """Describe a SmartThings select entity."""

    unique_id_separator: str = "."
    options_attribute: Attribute | None = None
    set_command: Command | None = None
    except_if_state_none: bool = False


CAPABILITY_TO_SELECTS: dict[
    Capability, dict[Attribute, list[SelectEntityDescription]]
] = {
    Capability.CUSTOM_DRYER_DRY_LEVEL: {
        Attribute.DRYER_DRY_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Attribute.DRYER_DRY_LEVEL,
                translation_key="dryer_dry_level",
                icon="mdi:waves-arrow-up",
                options_attribute=Attribute.SUPPORTED_DRYER_DRY_LEVEL,
                set_command=Command.SET_DRYER_DRY_LEVEL,
            )
        ]
    },
    Capability.CUSTOM_SUPPORTED_OPTIONS: {
        Attribute.COURSE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.COURSE,
                translation_key="course",
                icon="mdi:list-box-outline",
                options_attribute=Attribute.SUPPORTED_COURSES,
                set_command=Command.SET_COURSE,
            )
        ]
    },
    Capability.CUSTOM_WASHER_RINSE_CYCLES: {
        Attribute.WASHER_RINSE_CYCLES: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_RINSE_CYCLES,
                translation_key="washer_rinse_cycles",
                icon="mdi:water-sync",
                options_attribute=Attribute.SUPPORTED_WASHER_RINSE_CYCLES,
                set_command=Command.SET_WASHER_RINSE_CYCLES,
            )
        ]
    },
    Capability.CUSTOM_WASHER_SOIL_LEVEL: {
        Attribute.WASHER_SOIL_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_SOIL_LEVEL,
                translation_key="washer_soil_level",
                icon="mdi:brightness-7",
                options_attribute=Attribute.SUPPORTED_WASHER_SOIL_LEVEL,
                set_command=Command.SET_WASHER_SOIL_LEVEL,
            )
        ]
    },
    Capability.CUSTOM_WASHER_SPIN_LEVEL: {
        Attribute.WASHER_SPIN_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_SPIN_LEVEL,
                translation_key="washer_spin_level",
                icon="mdi:autorenew",
                options_attribute=Attribute.SUPPORTED_WASHER_SPIN_LEVEL,
                set_command=Command.SET_WASHER_SPIN_LEVEL,
            )
        ]
    },
    Capability.CUSTOM_WASHER_WATER_TEMPERATURE: {
        Attribute.WASHER_WATER_TEMPERATURE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_WATER_TEMPERATURE,
                translation_key="washer_water_temperature",
                icon="mdi:water-thermometer",
                options_attribute=Attribute.SUPPORTED_WASHER_WATER_TEMPERATURE,
                set_command=Command.SET_WASHER_WATER_TEMPERATURE,
            )
        ]
    },
    Capability.WASHER_OPERATING_STATE: {
        Attribute.MACHINE_STATE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.MACHINE_STATE,
                translation_key="machine_state",
                icon="mdi:play-speed",
                options_attribute=Attribute.SUPPORTED_MACHINE_STATES,
                set_command=Command.SET_MACHINE_STATE,
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
        SmartThingsSelect(entry_data.client, device, description, capability, attribute)
        for device in entry_data.devices.values()
        for capability, attributes in CAPABILITY_TO_SELECTS.items()
        if capability in device.status[MAIN]
        for attribute, descriptions in attributes.items()
        for description in descriptions
    )


class SmartThingsSelect(SmartThingsEntity, SelectEntity):
    """Define a SmartThings select."""

    entity_description: SmartThingsSelectEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsSelectEntityDescription,
        capability: Capability,
        attribute: Attribute,
    ) -> None:
        """Init the class."""
        super().__init__(client, device, {capability})
        self._attr_unique_id = (
            f"{super().unique_id}{device.device.device_id}{entity_description.key}"
        )
        self._attribute = attribute
        self.capability = capability
        self.entity_description = entity_description
        self.command = self.entity_description.set_command
        options: list[str] = []
        if self.entity_description.options_attribute:
            options = self.get_attribute_value(
                self.capability, self.entity_description.options_attribute
            )
            [option.lower() for option in options]
        self._attr_options: list[str] = options

    @property
    def native_value(self) -> str | float | datetime | int | None:
        """Return the state of the select."""
        return self.get_attribute_value(self.capability, self._attribute)

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        # Raw value
        value = self.get_attribute_value(self.capability, self._attribute)
        if value is None or value not in self._attr_options:
            return None

        return value

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        await self.execute_device_command(
            self.capability,
            self.command,
            option,
        )
