"""Support for buttons through the SmartThings cloud API."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, SmartThingsConfigEntry
from .const import MAIN
from .entity import SmartThingsEntity


@dataclass(frozen=True, kw_only=True)
class SmartThingsButtonEntityDescription(ButtonEntityDescription):
    """Describe a SmartThings binary sensor entity."""

    command_list: list[Command] | None = None
    argument: int | str | list[Any] | dict[str, Any] | None = None
    argument_fn: Callable[[SmartThingsEntity], list[Any] | None] | None = None
    extra_capabilities: list[Capability] | None = None
    component_fn: Callable[[str], bool] | None = None
    component_translation_key: dict[str, str] | None = None
    capability_ignore_list: list[set[Capability]] | None = None

CAPABILITY_TO_BUTTONS: dict[
    Capability, dict[Command, list[SmartThingsButtonEntityDescription]]
] = {
    Capability.SAMSUNG_CE_WASHER_OPERATING_STATE: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
            )
        ],
        Command.CANCEL: [
            SmartThingsButtonEntityDescription(
                key=Command.CANCEL,
                translation_key="state_cancel",
            )
        ],
        Command.RESUME: [
            SmartThingsButtonEntityDescription(
                key="pause_resume",
                translation_key="state_pause_resume",
                command_list=[Command.PAUSE, Command.RESUME],
            )
        ],
        Command.ESTIMATE_OPERATION_TIME: [
            SmartThingsButtonEntityDescription(
                key=Command.ESTIMATE_OPERATION_TIME,
                translation_key="estimate_operation_time",
            )
        ],
    },
    Capability.SAMSUNG_CE_DISHWASHER_OPERATION: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
            )
        ],
        Command.CANCEL: [
            SmartThingsButtonEntityDescription(
                key=Command.CANCEL,
                translation_key="state_cancel",
            )
        ],
        Command.RESUME: [
            SmartThingsButtonEntityDescription(
                key="pause_resume",
                translation_key="state_pause_resume",
                command_list=[Command.PAUSE, Command.RESUME],
            )
        ],
        Command.START_LATER: [
            SmartThingsButtonEntityDescription(
                key=Command.START_LATER,
                translation_key="state_start_later",
                extra_capabilities=[Capability.CUSTOM_DISHWASHER_DELAY_START_TIME],
                argument_fn=lambda ent: (
                    int(parts[0]) * 60 + int(parts[1])
                    if isinstance(val := ent.get_attribute_value(
                        Capability.CUSTOM_DISHWASHER_DELAY_START_TIME,
                        Attribute.DISHWASHER_DELAY_START_TIME,
                    ), str) and len(parts := val.split(":")) >= 2
                    else 60
                ),
            )
        ],
    },
    Capability.SAMSUNG_CE_DRYER_OPERATING_STATE: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
            )
        ],
        Command.CANCEL: [
            SmartThingsButtonEntityDescription(
                key=Command.CANCEL,
                translation_key="state_cancel",
            )
        ],
        Command.RESUME: [
            SmartThingsButtonEntityDescription(
                key="pause_resume",
                translation_key="state_pause_resume",
                command_list=[Command.PAUSE, Command.RESUME],
            )
        ],
    },
    Capability.OVEN_OPERATING_STATE: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
                capability_ignore_list=[Capability.SAMSUNG_CE_OVEN_OPERATING_STATE],
                component_fn=lambda component: component in ("cavity-01", "cavity-02"),
                component_translation_key={
                    "cavity-01": "state_start_cavity_01",
                    "cavity-02": "state_start_cavity_02",
                },
            ),
        ],
        Command.STOP: [
            SmartThingsButtonEntityDescription(
                key=Command.STOP,
                translation_key="state_stop",
                capability_ignore_list=[Capability.SAMSUNG_CE_OVEN_OPERATING_STATE],
                component_fn=lambda component: component in ("cavity-01", "cavity-02"),
                component_translation_key={
                    "cavity-01": "state_stop_cavity_01",
                    "cavity-02": "state_stop_cavity_02",
                },
            ),
        ],
    },
    Capability.SAMSUNG_CE_OVEN_OPERATING_STATE: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
                component_fn=lambda component: component in ("cavity-01", "cavity-02"),
                component_translation_key={
                    "cavity-01": "state_start_cavity_01",
                    "cavity-02": "state_start_cavity_02",
                },
            ),
        ],
        Command.STOP: [
            SmartThingsButtonEntityDescription(
                key=Command.STOP,
                translation_key="state_stop",
                component_fn=lambda component: component in ("cavity-01", "cavity-02"),
                component_translation_key={
                    "cavity-01": "state_stop_cavity_01",
                    "cavity-02": "state_stop_cavity_02",
                },
            ),
        ],
        Command.PAUSE: [
            SmartThingsButtonEntityDescription(
                key=Command.PAUSE,
                translation_key="state_pause",
                component_fn=lambda component: component in ("cavity-01", "cavity-02"),
                component_translation_key={
                    "cavity-01": "state_pause_cavity_01",
                    "cavity-02": "state_pause_cavity_02",
                },
            ),
        ],
    },
    Capability.CUSTOM_WATER_FILTER: {
        Command.RESET_WATER_FILTER: [
            SmartThingsButtonEntityDescription(
                key=Command.RESET_WATER_FILTER,
                translation_key="reset_water_filter",
            ),
        ]
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
            component,
        )
        for device in entry_data.devices.values()
        for capability, commands in CAPABILITY_TO_BUTTONS.items()
        for component in device.status
        if capability in device.status[component]
        for command, descriptions in commands.items()
        for description in descriptions
            if (not description.component_fn or description.component_fn(component)) and
               not (description.capability_ignore_list and any(
                   all(c in device.status[MAIN] for c in cl)
                   for cl in description.capability_ignore_list
               ))
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
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        capabilities = {capability}
        if entity_description.extra_capabilities:
            capabilities.update(entity_description.extra_capabilities)
        super().__init__(client, device, capabilities, component=component)
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{entity_description.key}"
        self.command = command
        self.capability = capability
        self.entity_description = entity_description
        if self.entity_description.component_translation_key and component != MAIN:
            self._attr_translation_key = (
                self.entity_description.component_translation_key[component]
            )

    async def async_press(self) -> None:
        """Press the button."""
        if self.entity_description.argument_fn:
            argument = self.entity_description.argument_fn(self)
        else:
            argument = self.entity_description.argument
        if self.command == Command.START_LATER and argument is not None:
            try:
                argument = int(float(argument))
            except (ValueError, TypeError):
                argument = 60
        if self.entity_description.command_list:
            item = self.entity_description.command_list.index(self.command)
            if item == (len(self.entity_description.command_list) - 1):
                self.command = self.entity_description.command_list[0]
            else:
                self.command = self.entity_description.command_list[item + 1]
        await self.execute_device_command(
            self.capability,
            self.command,
            argument,
        )
