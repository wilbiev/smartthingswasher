"""Support for numbers through the SmartThings cloud API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, SmartThingsConfigEntry
from .const import MAIN
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
                native_max_value=240,
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
                native_max_value=240,
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
                native_max_value=240,
                native_step=5,
                int_type=STType.INTEGER,
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

    @property
    def native_value(self) -> str | float | datetime | int | None:
        """Return the state of the number."""
        if self._number is None:
            return None

        return self.get_attribute_value(self.capability, self._attribute)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self._number is None:
            raise RuntimeError("Cannot set value, device doesn't provide type data")

        if self._number is STType.INTEGER:
            await self.execute_device_command(
                self.capability,
                self.command,
                int(value),
            )
        else:
            await self.execute_device_command(
                self.capability,
                self.command,
                str(int(value)),
            )
