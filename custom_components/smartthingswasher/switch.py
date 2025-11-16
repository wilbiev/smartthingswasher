"""Support for switches through the SmartThings cloud API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, Program, SmartThingsConfigEntry
from .const import CAPABILITIES_WITH_PROGRAMS, CAPABILITY_COMMANDS, MAIN
from .entity import SmartThingsEntity
from .util import get_program_table_id, translate_program_course

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


@dataclass(frozen=True, kw_only=True)
class SmartThingsSwitchEntityDescription(SwitchEntityDescription):
    """Describe a SmartThings switch entity."""

    command: Command | None = None
    on_key: str = "on"
    on_command: Command = Command.ON
    off_command: Command = Command.OFF


CAPABILITY_TO_SWITCHES: dict[
    Capability, dict[Attribute, list[SmartThingsSwitchEntityDescription]]
] = {
    Capability.CUSTOM_DRYER_WRINKLE_PREVENT: {
        Attribute.DRYER_WRINKLE_PREVENT: [
            SmartThingsSwitchEntityDescription(
                key=Capability.CUSTOM_DRYER_WRINKLE_PREVENT,
                translation_key="wrinkle_prevent",
                command=Command.SET_DRYER_WRINKLE_PREVENT,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_STEAM_CLOSET_AUTO_CYCLE_LINK: {
        Attribute.STEAM_CLOSET_AUTO_CYCLE_LINK: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_STEAM_CLOSET_AUTO_CYCLE_LINK,
                translation_key="auto_cycle_link",
                command=Command.SET_STEAM_CLOSET_AUTO_CYCLE_LINK,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.CUSTOM_STEAM_CLOSET_WRINKLE_PREVENT: {
        Attribute.STEAM_CLOSET_WRINKLE_PREVENT: [
            SmartThingsSwitchEntityDescription(
                key=Capability.CUSTOM_STEAM_CLOSET_WRINKLE_PREVENT,
                translation_key="wrinkle_prevent",
                command=Command.SET_STEAM_CLOSET_WRINKLE_PREVENT,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_SABBATH_MODE: {
        Attribute.STATUS: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_SABBATH_MODE,
                translation_key="sabbath_mode",
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_STEAM_CLOSET_KEEP_FRESH_MODE: {
        Attribute.STATUS: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_STEAM_CLOSET_KEEP_FRESH_MODE,
                translation_key="steam_closet_keep_fresh_mode",
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_STEAM_CLOSET_SANITIZE_MODE: {
        Attribute.STATUS: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_STEAM_CLOSET_SANITIZE_MODE,
                translation_key="steam_closet_sanitize_mode",
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_WASHER_BUBBLE_SOAK: {
        Attribute.STATUS: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_WASHER_BUBBLE_SOAK,
                translation_key="bubble_soak",
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_POWER_COOL: {
        Attribute.ACTIVATED: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_POWER_COOL,
                translation_key="power_cool",
                on_key="True",
                on_command=Command.ACTIVATE,
                off_command=Command.DEACTIVATE,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_POWER_FREEZE: {
        Attribute.ACTIVATED: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_POWER_FREEZE,
                translation_key="power_freeze",
                on_key="True",
                on_command=Command.ACTIVATE,
                off_command=Command.DEACTIVATE,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_AIR_CONDITIONER_BEEP: {
        Attribute.BEEP: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_AIR_CONDITIONER_BEEP,
                translation_key="sound_effect",
                on_key="on",
                on_command=Command.ON,
                off_command=Command.OFF,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_AIR_CONDITIONER_LIGHTING: {
        Attribute.LIGHTING: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_AIR_CONDITIONER_LIGHTING,
                translation_key="display_lighting",
                command=Command.SET_LIGHTING_LEVEL,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SWITCH: {
        Attribute.SWITCH: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SWITCH,
                translation_key="switch",
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
        SmartThingsSwitch(
            entry_data.client,
            device,
            description,
            capability,
            attribute,
            component,
        )
        for device in entry_data.devices.values()
        for capability, attributes in CAPABILITY_TO_SWITCHES.items()
        for component in device.status
        if capability in device.status[component]
        and not any(
            capability in device.status[component] for capability in CAPABILITIES
        )
        and not all(
            capability in device.status[component] for capability in AC_CAPABILITIES
        )
        for attribute, descriptions in attributes.items()
        for description in descriptions
    )
    async_add_entities(
        SmartThingsProgramSwitch(
            entry_data.client,
            device,
            program,
            capability,
            attribute,
            component,
        )
        for device in entry_data.devices.values()
        for program in device.programs.values()
        for capability, attribute in CAPABILITIES_WITH_PROGRAMS.items()
        for component in device.status
        if capability in device.status[component]
    )


class SmartThingsSwitch(SmartThingsEntity, SwitchEntity):
    """Define a SmartThings switch."""

    entity_description: SmartThingsSwitchEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsSwitchEntityDescription,
        capability: Capability,
        attribute: Attribute,
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        super().__init__(client, device, {capability}, component=component)
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{entity_description.key}"
        self._attribute = attribute
        self.capability = capability
        if self.capability == Capability.SWITCH:
            self._attr_name = None
        self.entity_description = entity_description

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if self.entity_description.command:
            await self.execute_device_command(
                self.capability,
                self.entity_description.command,
                "off",
            )
        else:
            await self.execute_device_command(
                self.capability,
                self.entity_description.off_command,
            )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.entity_description.command:
            await self.execute_device_command(
                self.capability,
                self.entity_description.command,
                "on",
            )
        else:
            await self.execute_device_command(
                self.capability,
                self.entity_description.on_command,
            )

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.get_attribute_value(self.capability, self._attribute) == self.entity_description.on_key


class SmartThingsProgramSwitch(SmartThingsEntity, SwitchEntity):
    """Define a SmartThings switch."""

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        program: Program,
        capability: Capability,
        attribute: Attribute,
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        program_course = program.program_id.lower()
        if (table_id := get_program_table_id(device.status)) != "":
            program_translation = f"{table_id}_{program_course}"
        else:
            program_translation = program_course
        entity_description = SwitchEntityDescription(
            key=program.program_id, translation_key=program_translation
        )
        super().__init__(
            client, device, {capability}, component=component, program=program
        )
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{program_course}"
        self._attribute = attribute
        self.capability = capability
        self.command = CAPABILITY_COMMANDS.get(capability)
        self.entity_description = entity_description

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.command is not None and self.program is not None:
            await self.execute_device_command(
                self.capability, self.command, self.program.program_id
            )

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if self.program is None:
            return False
        return (
            translate_program_course(
                self.get_attribute_value(self.capability, self._attribute)
            )
            == self.program.program_id
        )

    def update_native_value(self) -> None:
        """Update the switch's status based on if the program related to this entity is currently active."""
        res: str = translate_program_course(
            self.get_attribute_value(self.capability, self._attribute)
        )
        if self.program is not None:
            self._attr_is_on = bool(res and res == self.program.program_id)
