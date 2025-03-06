"""Support for switches through the SmartThings cloud API."""

from __future__ import annotations

from typing import Any

from pysmartthings import Capability, Command, SmartThings

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, SmartThingsConfigEntry
from .const import MAIN
from .entity import SmartThingsEntity


CAPABILITY_TO_BUTTONS: dict[
    Capability, dict[Command, list[ButtonEntityDescription]]
] = {
    Capability.SAMSUNG_CE_WASHER_OPERATING_STATE: {
        Command.START: [
            ButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
                icon="mdi:play-circle",
            )
        ],
        Command.CANCEL: [
            ButtonEntityDescription(
                key=Command.CANCEL,
                translation_key="state_cancel",
                icon="mdi:stop-circle",
            )
        ],
        Command.PAUSE: [
            ButtonEntityDescription(
                key=Command.PAUSE,
                translation_key="state_pause",
                icon="mdi:pause-circle",
            )
        ],
        Command.RESUME: [
            ButtonEntityDescription(
                key=Command.RESUME,
                translation_key="state_resume",
                icon="mdi:play-pause",
            )
        ],
        Command.ESTIMATE_OPERATION_TIME: [
            ButtonEntityDescription(
                key=Command.ESTIMATE_OPERATION_TIME,
                translation_key="estimate_operation_time",
                icon="mdi:clock-end",
            )
        ],
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartThingsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add buttons for a config entry."""
    entry_data = entry.runtime_data
    async_add_entities(
        SmartThingsButton(entry_data.client, device, description, capability, command)
        for device in entry_data.devices.values()
        for capability, commands in CAPABILITY_TO_BUTTONS.items()
        if capability in device.status[MAIN]
        for command, descriptions in commands.items()
        for description in descriptions
    )


class SmartThingsButton(SmartThingsEntity, ButtonEntity):
    """Define a SmartThings button."""

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        description: ButtonEntityDescription,
        capability: Capability,
        command: Command,
    ) -> None:
        """Init the class."""
        super().__init__(client, device, {capability})
        self._attr_unique_id = (
            f"{super().unique_id}{device.device.device_id}{description.key}"
        )
        self.command = command
        self.capability = capability
        self.entity_description = description

    async def press(self) -> None:
        """Press the button."""
        await self.execute_device_command(
            self.capability,
            self.command,
        )
