"""Support for buttons through the SmartThings cloud API."""

from __future__ import annotations

from dataclasses import dataclass

from pysmartthings import Capability, Command, SmartThings

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, SmartThingsConfigEntry
from .const import MAIN
from .entity import SmartThingsEntity


@dataclass(frozen=True, kw_only=True)
class SmartThingsButtonEntityDescription(ButtonEntityDescription):
    """Describe a SmartThings binary sensor entity."""

    unique_id_separator: str = "."
    command_list: list[Command] = None


CAPABILITY_TO_BUTTONS: dict[
    Capability, dict[Command, list[SmartThingsButtonEntityDescription]]
] = {
    Capability.SAMSUNG_CE_WASHER_OPERATING_STATE: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
                icon="mdi:play-circle",
            )
        ],
        Command.CANCEL: [
            SmartThingsButtonEntityDescription(
                key=Command.CANCEL,
                translation_key="state_cancel",
                icon="mdi:stop-circle",
            )
        ],
        Command.RESUME: [
            SmartThingsButtonEntityDescription(
                key="pause_resume",
                translation_key="state_pause_resume",
                command_list=[Command.PAUSE, Command.RESUME],
                icon="mdi:pause-circle",
            )
        ],
        Command.ESTIMATE_OPERATION_TIME: [
            SmartThingsButtonEntityDescription(
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
        SmartThingsButton(
            entry_data.client,
            device,
            description,
            capability,
            command,
        )
        for device in entry_data.devices.values()
        for capability, commands in CAPABILITY_TO_BUTTONS.items()
        if capability in device.status[MAIN]
        for command, descriptions in commands.items()
        for description in descriptions
    )


class SmartThingsButton(SmartThingsEntity, ButtonEntity):
    """Define a SmartThings button."""

    entity_description: SmartThingsButtonEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsButtonEntityDescription,
        capability: Capability,
        command: Command,
    ) -> None:
        """Init the class."""
        super().__init__(client, device, {capability})
        self._attr_unique_id = f"{device.device.device_id}{entity_description.unique_id_separator}{entity_description.key}"
        self.command = command
        self.capability = capability
        self.entity_description = entity_description

    async def async_press(self) -> None:
        """Press the button."""
        if self.entity_description.command_list is not None:
            item = self.entity_description.command_list.index(self.command)
            if item == (len(self.entity_description.command_list) - 1):
                self.command = self.entity_description.command_list[0]
            else:
                self.command = self.entity_description.command_list[item + 1]
        await self.execute_device_command(
            self.capability,
            self.command,
        )
