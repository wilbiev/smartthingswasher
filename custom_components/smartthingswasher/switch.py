"""Support for switches through the SmartThings cloud API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FullDevice, Program, SmartThingsConfigEntry
from .const import CAPABILITY_COMMANDS, CAPABILITY_COURSES, MAIN
from .entity import SmartThingsEntity
from .util import command_program_course, get_program_table_id, translate_program_course

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
    on_key: str | bool = "on"
    off_key: str | bool = "off"
    on_command: Command = Command.ON
    off_command: Command = Command.OFF
    check_capability: Capability | None = None


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
                check_capability=Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE,
            )
        ]
    },
    Capability.SAMSUNG_CE_STEAM_CLOSET_SANITIZE_MODE: {
        Attribute.STATUS: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_STEAM_CLOSET_SANITIZE_MODE,
                translation_key="steam_closet_sanitize_mode",
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE,
            )
        ]
    },
    Capability.SAMSUNG_CE_WASHER_BUBBLE_SOAK: {
        Attribute.STATUS: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_WASHER_BUBBLE_SOAK,
                translation_key="bubble_soak",
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_WASHER_CYCLE,
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
    Capability.SAMSUNG_CE_AUTO_OPEN_DOOR: {
        Attribute.AUTO_OPEN_DOOR: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_AUTO_OPEN_DOOR,
                translation_key="auto_open_door",
                on_key="on",
                on_command=Command.ON,
                off_command=Command.OFF,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.CUSTOM_DO_NOT_DISTURB_MODE: {
        Attribute.DO_NOT_DISTURB: [
            SmartThingsSwitchEntityDescription(
                key=Capability.CUSTOM_DO_NOT_DISTURB_MODE,
                translation_key="do_not_disturb",
                entity_category=EntityCategory.CONFIG,
                on_command=Command.DO_NOT_DISTURB_ON,
                off_command=Command.DO_NOT_DISTURB_OFF,
            )
        ],
    },
    Capability.SOUND_DETECTION: {
        Attribute.SOUND_DETECTION_STATE: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SOUND_DETECTION,
                translation_key="sound_detection",
                entity_category=EntityCategory.CONFIG,
                on_key="enabled",
                on_command=Command.ENABLE_SOUND_DETECTION,
                off_command=Command.DISABLE_SOUND_DETECTION,
            )
        ]
    },
    Capability.SAMSUNG_CE_MICROFIBER_FILTER_SETTINGS: {
        Attribute.BYPASS_MODE: [
            SmartThingsSwitchEntityDescription(
                key=Capability.SAMSUNG_CE_MICROFIBER_FILTER_SETTINGS,
                translation_key="bypass_mode",
                entity_category=EntityCategory.CONFIG,
                on_key="enabled",
                off_key="disabled",
                command=Command.SET_BYPASS_MODE,
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

DISHWASHER_WASHING_OPTIONS_TO_SWITCHES: dict[
    Capability, dict[Attribute, list[SmartThingsSwitchEntityDescription]]
] = {
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_OPTIONS: {
        Attribute.ADD_RINSE: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.ADD_RINSE,
                translation_key="add_rinse",
                command=Command.SET_ADD_RINSE,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.DRY_PLUS: [
            SmartThingsSwitchEntityDescription(
            key=Attribute.DRY_PLUS,
                translation_key="dry_plus",
                command=Command.SET_DRY_PLUS,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.HEATED_DRY: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.HEATED_DRY,
                translation_key="heated_dry",
                command=Command.SET_HEATED_DRY,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.HIGH_TEMP_WASH: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.HIGH_TEMP_WASH,
                translation_key="high_temp_wash",
                command=Command.SET_HIGH_TEMP_WASH,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.HOT_AIR_DRY: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.HOT_AIR_DRY,
                translation_key="hot_air_dry",
                command=Command.SET_HOT_AIR_DRY,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.MULTI_TAB: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.MULTI_TAB,
                translation_key="multi_tab",
                command=Command.SET_MULTI_TAB,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.RINSE_PLUS: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.RINSE_PLUS,
                translation_key="rinse_plus",
                command=Command.SET_RINSE_PLUS,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.SANITIZE: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.SANITIZE,
                translation_key="sanitize",
                command=Command.SET_SANITIZE,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.SANITIZING_WASH: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.SANITIZING_WASH,
                translation_key="sanitizing_wash",
                command=Command.SET_SANITIZING_WASH,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.SPEED_BOOSTER: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.SPEED_BOOSTER,
                translation_key="speed_booster",
                command=Command.SET_SPEED_BOOSTER,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.STEAM_SOAK: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.STEAM_SOAK,
                translation_key="steam_soak",
                command=Command.SET_STEAM_SOAK,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
        Attribute.STORM_WASH: [
            SmartThingsSwitchEntityDescription(
                key=Attribute.STORM_WASH,
                translation_key="storm_wash",
                command=Command.SET_STORM_WASH,
                on_key=True,
                off_key=False,
                entity_category=EntityCategory.CONFIG,
                check_capability=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            )
        ],
    }
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
        for component, capabilities in device.status.items()
        if not any(c in capabilities for c in CAPABILITIES)
        if not all(c in capabilities for c in AC_CAPABILITIES)
        for capability, attributes in CAPABILITY_TO_SWITCHES.items()
        if capability in capabilities
        for attribute, descriptions in attributes.items()
        for description in descriptions
    )

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
        for capability, attributes in DISHWASHER_WASHING_OPTIONS_TO_SWITCHES.items()
        for component in device.status
        if capability in device.status[component]
        for supported_attr in [device.status[component][capability].get(Attribute.SUPPORTED_LIST)]
        if supported_attr and supported_attr.value
        for attribute, descriptions in attributes.items()
        if attribute in cast(list[str], supported_attr.value)
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
        for component, capabilities in device.status.items()
        for capability, attribute in CAPABILITY_COURSES.items()
        if capability in capabilities and capabilities[capability].get(attribute) is not None
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
        capabilities = {capability}
        if entity_description.check_capability is not None:
            capabilities.add(entity_description.check_capability)
        capabilities.add(Capability.REMOTE_CONTROL_STATUS)
        super().__init__(client, device, capabilities, component=component)
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{entity_description.key}"
        self._attribute = attribute
        self.capability = capability
        if self.capability == Capability.SWITCH:
            self._attr_name = None
        self.entity_description = entity_description
        self.command = self.entity_description.command

    def _validate_before_execute(self) -> None:
        """Validate that the switch command can be executed."""
        if self.entity_description.check_capability is not None:
            if (attribute_course := CAPABILITY_COURSES.get(self.entity_description.check_capability)) is None:
                raise ServiceValidationError("Option is not supported by selected course/cycle")

            if (current_course_raw := self.get_attribute_value(self.entity_description.check_capability, attribute_course)) is None:
                raise ServiceValidationError("Option is not supported by selected course/cycle")

            current_course = translate_program_course(current_course_raw)
            if not self.device.programs or current_course not in self.device.programs:
                raise ServiceValidationError("Option is not supported by selected course/cycle")

            program = self.device.programs[current_course]
            if (opt := program.supportedoptions.get(self.entity_description.key)) is not None:
                if len(opt.options) > 1:
                    return

            raise ServiceValidationError("Option is not supported by selected course/cycle")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._validate_before_execute()
        if self.command:
            await self.execute_device_command(
                self.capability,
                self.command,
                self.entity_description.off_key,
            )
        else:
            await self.execute_device_command(
                self.capability,
                self.entity_description.off_command,
            )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._validate_before_execute()
        if self.command:
            await self.execute_device_command(
                self.capability,
                self.command,
                self.entity_description.on_key,
            )
        else:
            await self.execute_device_command(
                self.capability,
                self.entity_description.on_command,
            )

    def _current_state(self) -> Any:
        return self.get_attribute_value(
            self.capability, self._attribute
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
        program_course = program.program_id
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
        self._attr_is_on = False

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.command is not None and self.program is not None:
            await self.execute_device_command(
                self.capability, self.command, command_program_course(self.program.program_id)
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
