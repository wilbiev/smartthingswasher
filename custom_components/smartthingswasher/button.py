"""Support for buttons through the SmartThings cloud API."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import _LOGGER, HomeAssistant, ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, SmartThingsConfigEntry
from .const import CAVITY_01, CAVITY_SINGLE, MAIN
from .entity import SmartThingsEntity
from .models import SupportedOption
from .util import command_oven_mode, get_current_cavity_id


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
    capability_include_list: list[set[Capability]] | None = None
    requires_remote_control_status: bool = False


CAPABILITY_TO_BUTTONS: dict[
    Capability, dict[Command, list[SmartThingsButtonEntityDescription]]
] = {
    Capability.SAMSUNG_CE_WASHER_OPERATING_STATE: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
                requires_remote_control_status=True,
            )
        ],
        Command.CANCEL: [
            SmartThingsButtonEntityDescription(
                key=Command.CANCEL,
                translation_key="state_cancel",
                requires_remote_control_status=True,
            )
        ],
        Command.RESUME: [
            SmartThingsButtonEntityDescription(
                key="pause_resume",
                translation_key="state_pause_resume",
                command_list=[Command.PAUSE, Command.RESUME],
                requires_remote_control_status=True,
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
                requires_remote_control_status=True,
            )
        ],
        Command.CANCEL: [
            SmartThingsButtonEntityDescription(
                key=Command.CANCEL,
                translation_key="state_cancel",
                requires_remote_control_status=True,
            )
        ],
        Command.RESUME: [
            SmartThingsButtonEntityDescription(
                key="pause_resume",
                translation_key="state_pause_resume",
                command_list=[Command.PAUSE, Command.RESUME],
                requires_remote_control_status=True,
            )
        ],
        Command.START_LATER: [
            SmartThingsButtonEntityDescription(
                key=Command.START_LATER,
                translation_key="state_start_later",
                extra_capabilities=[Capability.CUSTOM_DISHWASHER_DELAY_START_TIME],
                argument_fn=lambda ent: [
                    int(parts[0]) * 60 + int(parts[1])
                    if isinstance(
                        val := ent.get_attribute_value(
                            Capability.CUSTOM_DISHWASHER_DELAY_START_TIME,
                            Attribute.DISHWASHER_DELAY_START_TIME,
                        ),
                        str,
                    )
                    and len(parts := val.split(":")) >= 2
                    else 60
                ],
                requires_remote_control_status=True,
            )
        ],
    },
    Capability.SAMSUNG_CE_DRYER_OPERATING_STATE: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
                requires_remote_control_status=True,
            )
        ],
        Command.CANCEL: [
            SmartThingsButtonEntityDescription(
                key=Command.CANCEL,
                translation_key="state_cancel",
                requires_remote_control_status=True,
            )
        ],
        Command.RESUME: [
            SmartThingsButtonEntityDescription(
                key="pause_resume",
                translation_key="state_pause_resume",
                command_list=[Command.PAUSE, Command.RESUME],
                requires_remote_control_status=True,
            )
        ],
    },
    Capability.OVEN_OPERATING_STATE: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
                extra_capabilities=[
                    Capability.CUSTOM_OVEN_CAVITY_STATUS,
                    Capability.SAMSUNG_CE_KITCHEN_MODE_SPECIFICATION,
                ],
                capability_ignore_list=[{Capability.SAMSUNG_CE_OVEN_OPERATING_STATE}],
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "state_start_cavity_01",
                    "cavity-02": "state_start_cavity_02",
                },
                requires_remote_control_status=True,
            ),
        ],
        Command.STOP: [
            SmartThingsButtonEntityDescription(
                key=Command.STOP,
                translation_key="state_stop",
                capability_ignore_list=[{Capability.SAMSUNG_CE_OVEN_OPERATING_STATE}],
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "state_stop_cavity_01",
                    "cavity-02": "state_stop_cavity_02",
                },
                requires_remote_control_status=True,
            ),
        ],
        Command.SET_MACHINE_STATE: [
            SmartThingsButtonEntityDescription(
                key=Command.SET_MACHINE_STATE,
                translation_key="state_pause",
                argument="pause",
                capability_ignore_list=[{Capability.SAMSUNG_CE_OVEN_OPERATING_STATE}],
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "state_pause_cavity_01",
                    "cavity-02": "state_pause_cavity_02",
                },
                requires_remote_control_status=True,
            ),
        ],
    },
    Capability.SAMSUNG_CE_OVEN_OPERATING_STATE: {
        Command.START: [
            SmartThingsButtonEntityDescription(
                key=Command.START,
                translation_key="state_start",
                extra_capabilities=[
                    Capability.CUSTOM_OVEN_CAVITY_STATUS,
                    Capability.SAMSUNG_CE_KITCHEN_MODE_SPECIFICATION,
                    Capability.SAMSUNG_CE_OVEN_MODE,
                    Capability.OVEN_SETPOINT,
                    Capability.OVEN_OPERATING_STATE,
                ],
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "state_start_cavity_01",
                    "cavity-02": "state_start_cavity_02",
                },
                requires_remote_control_status=True,
            ),
        ],
        Command.STOP: [
            SmartThingsButtonEntityDescription(
                key=Command.STOP,
                translation_key="state_stop",
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "state_stop_cavity_01",
                    "cavity-02": "state_stop_cavity_02",
                },
                requires_remote_control_status=True,
            ),
        ],
        Command.PAUSE: [
            SmartThingsButtonEntityDescription(
                key=Command.PAUSE,
                translation_key="state_pause",
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "state_pause_cavity_01",
                    "cavity-02": "state_pause_cavity_02",
                },
                requires_remote_control_status=True,
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
    Capability.EXECUTE: {
        Command.EXECUTE: [
            SmartThingsButtonEntityDescription(
                key="time_sync",
                translation_key="time_sync",
                capability_include_list=[
                    {Capability.OVEN_MODE},
                    {Capability.SAMSUNG_CE_OVEN_MODE},
                ],
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
        for component, capabilities in device.status.items()
        if capability in capabilities
        for command, descriptions in commands.items()
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
        and (
            not description.capability_include_list
            or any(
                all(include_cap in capabilities for include_cap in include_cap_list)
                for include_cap_list in description.capability_include_list
            )
        )
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
        capabilities.add(Capability.REMOTE_CONTROL_STATUS)
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
        """Collect the values from the model and start the oven."""

        if (
            self.entity_description.requires_remote_control_status
            and self.get_attribute_value(
                Capability.REMOTE_CONTROL_STATUS, Attribute.REMOTE_CONTROL_ENABLED
            )
            == "false"
        ):
            raise ServiceValidationError(
                "Can only be used when remote control is enabled"
            )
        argument = None
        if self.capability in {
            Capability.OVEN_OPERATING_STATE,
            Capability.SAMSUNG_CE_OVEN_OPERATING_STATE,
        }:
            raw_mode = None
            current_mode = None
            cavity_key = get_current_cavity_id(self.device.status, self.component)
            if self.component == CAVITY_01 and cavity_key == CAVITY_SINGLE:
                raise ServiceValidationError(
                    "Cannot perform action for lower oven in single cavity mode"
                )
            if self.command == Command.START:
                if self.device.modes and cavity_key in self.device.modes:
                    if self.device.modes[cavity_key].active_mode != "no_operation":
                        if raw_mode := self.device.modes[cavity_key].active_mode:
                            current_mode = command_oven_mode(raw_mode)
                if not raw_mode or not current_mode:
                    raise ServiceValidationError("No active oven mode found")

                lookup_id = f"{cavity_key}_{raw_mode}"
                program = self.device.programs.get(lookup_id)
                if not program:
                    raise ServiceValidationError(
                        f"Program not found for {current_mode}"
                    )
                current_temp = 0
                if temp_opt := program.supportedoptions.get(
                    SupportedOption.TEMPERATURE
                ):
                    current_temp = int(temp_opt.selected_value or temp_opt.default or 0)
                if current_temp == 0:
                    raise ServiceValidationError(
                        "Cannot start oven session with zero temperature"
                    )
                operation_time = None
                if time_opt := program.supportedoptions.get(
                    SupportedOption.OPERATION_TIME
                ):
                    time_minutes = int(time_opt.selected_value or time_opt.default or 0)
                    operation_time = (
                        f"{time_minutes // 60:02d}:{time_minutes % 60:02d}:00"
                    )
                if not operation_time or operation_time in {0, "00:00:00"}:
                    raise ServiceValidationError(
                        "Cannot start oven session with zero operation time"
                    )
                _LOGGER.debug(
                    "Staging oven session: Mode=%s, Time=%s, Temp=%s",
                    current_mode,
                    operation_time,
                    current_temp,
                )
                if self.capability == Capability.OVEN_OPERATING_STATE:
                    argument = [
                        current_mode,
                        time_minutes * 60,
                        current_temp,
                    ]
                else:
                    await self.execute_device_command(
                        Capability.SAMSUNG_CE_OVEN_MODE,
                        Command.SET_OVEN_MODE,
                        current_mode,
                    )
                    await self.execute_device_command(
                        Capability.SAMSUNG_CE_OVEN_OPERATING_STATE,
                        Command.SET_OPERATION_TIME,
                        operation_time,
                    )
                    await self.execute_device_command(
                        Capability.OVEN_SETPOINT,
                        Command.SET_OVEN_SETPOINT,
                        current_temp,
                    )
                if not program.supports_start:
                    await self.execute_device_command(
                        self.capability,
                        self.command,
                        argument,
                    )
                await self.execute_device_command(
                    Capability.OVEN_OPERATING_STATE,
                    Command.SET_MACHINE_STATE,
                    "run",
                )
                return
        elif self.entity_description.key == "time_sync":
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            argument = [
                "/configuration/vs/0",
                {"x.com.samsung.da.currentTime": current_time},
            ]
            _LOGGER.debug("Sending time sync command with time: %s", current_time)
        elif self.entity_description.argument_fn:
            argument = self.entity_description.argument_fn(self)
        else:
            argument = self.entity_description.argument
        if self.command == Command.START_LATER and argument is not None:
            if isinstance(argument, (int, float, str)):
                try:
                    argument = int(float(argument))
                except (ValueError, TypeError):
                    argument = 60
            else:
                argument = 60
        if self.entity_description.command_list:
            idx = self.entity_description.command_list.index(self.command)
            self.command = self.entity_description.command_list[
                (idx + 1) % len(self.entity_description.command_list)
            ]
        await self.execute_device_command(
            self.capability,
            self.command,
            argument,
        )
