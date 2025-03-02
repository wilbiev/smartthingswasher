"""Support for switches through the SmartThings cloud API."""

from __future__ import annotations

from typing import Any

from pysmartthings import Attribute, Capability, Command

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SmartThingsConfigEntry
from .const import MAIN
from .entity import SmartThingsEntity

CAPABILITIES = (
    Capability.SWITCH_LEVEL,
    Capability.COLOR_CONTROL,
    Capability.COLOR_TEMPERATURE,
    Capability.FAN_SPEED,
)

AC_CAPABILITIES = (
    Capability.AIR_CONDITIONER_MODE,
    Capability.AIR_CONDITIONER_FAN_MODE,
    Capability.TEMPERATURE_MEASUREMENT,
    Capability.THERMOSTAT_COOLING_SETPOINT,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartThingsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add switches for a config entry."""
    entry_data = entry.runtime_data
    async_add_entities(
        SmartThingsSwitch(entry_data.client, device, {Capability.SWITCH})
        for device in entry_data.devices.values()
        if Capability.SWITCH in device.status[MAIN]
        and not any(capability in device.status[MAIN] for capability in CAPABILITIES)
        and not all(capability in device.status[MAIN] for capability in AC_CAPABILITIES)
    )
    async_add_entities(
        SmartThingsBubbleSoak(entry_data.client, device, {Capability.SAMSUNG_CE_WASHER_BUBBLE_SOAK})
        for device in entry_data.devices.values()
        if Capability.SAMSUNG_CE_WASHER_BUBBLE_SOAK in device.status[MAIN]
        and not any(capability in device.status[MAIN] for capability in CAPABILITIES)
        and not all(capability in device.status[MAIN] for capability in AC_CAPABILITIES)
    )


class SmartThingsSwitch(SmartThingsEntity, SwitchEntity):
    """Define a SmartThings switch."""

    _attr_name = None

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.execute_device_command(
            Capability.SWITCH,
            Command.OFF,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.execute_device_command(
            Capability.SWITCH,
            Command.ON,
        )

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.get_attribute_value(Capability.SWITCH, Attribute.SWITCH) == "on"


class SmartThingsBubbleSoak(SmartThingsEntity, SwitchEntity):
    """Define a SmartThings BubbleSoak switch."""

    _attr_name = None

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.execute_device_command(
            Capability.SAMSUNG_CE_WASHER_BUBBLE_SOAK,
            Command.OFF,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.execute_device_command(
            Capability.SAMSUNG_CE_WASHER_BUBBLE_SOAK,
            Command.ON,
        )

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.get_attribute_value(Capability.SAMSUNG_CE_WASHER_BUBBLE_SOAK, Attribute.STATUS) == "on"
