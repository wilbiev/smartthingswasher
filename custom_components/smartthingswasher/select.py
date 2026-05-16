"""Support for selects through the SmartThings cloud API."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import FullDevice, SmartThingsConfigEntry
from .const import (
    CAPABILITIES_WITH_PROGRAMS,
    CLEANING_TYPE_TO_HA,
    COURSE_TO_HA,
    DISPENSE_DENSITY_TO_HA,
    DRIVING_MODE_TO_HA,
    LAMP_TO_HA,
    MAIN,
    OVEN_MODE_TO_HA,
    SOUND_MODE_TO_HA,
    WASHER_SOIL_LEVEL_TO_HA,
    WASHER_SPIN_LEVEL_TO_HA,
    WASHER_WATER_TEMPERATURE_TO_HA,
    WATER_SPRAY_LEVEL_TO_HA,
)
from .entity import SmartThingsEntity
from .models import SupportedOption
from .util import (
    command_program_course,
    get_current_cavity_id,
    get_program_options,
    get_program_table_id,
    translate_program_course,
)


@dataclass(frozen=True, kw_only=True)
class SmartThingsSelectEntityDescription(SelectEntityDescription):
    """Describe a SmartThings select entity."""

    command: Command | None = None
    options_attribute: Attribute | None = None
    supported_option: SupportedOption | None = None
    capability_ignore_list: list[set[Capability]] | None = None
    options_map: dict[str, str] | None = None
    value_is_integer: bool = False
    component_fn: Callable[[str], bool] | None = None
    component_translation_key: dict[str, str] | None = None


CAPABILITY_TO_SELECTS: dict[
    Capability, dict[Attribute, list[SmartThingsSelectEntityDescription]]
] = {
    Capability.CUSTOM_DRYER_DRY_LEVEL: {
        Attribute.DRYER_DRY_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Capability.CUSTOM_DRYER_DRY_LEVEL,
                translation_key="dryer_dry_level",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_DRYER_DRY_LEVEL,
                command=Command.SET_DRYER_DRY_LEVEL,
                supported_option=SupportedOption.DRYING_LEVEL,
            )
        ]
    },
    Capability.CUSTOM_STEAM_CLOSET_OPERATING_STATE: {
        Attribute.STEAM_CLOSET_MACHINE_STATE: [
            SmartThingsSelectEntityDescription(
                key=Capability.CUSTOM_STEAM_CLOSET_OPERATING_STATE,
                translation_key="machine_state",
                options_attribute=Attribute.SUPPORTED_STEAM_CLOSET_MACHINE_STATE,
                command=Command.SET_STEAM_CLOSET_MACHINE_STATE,
            )
        ]
    },
    Capability.CUSTOM_SUPPORTED_OPTIONS: {
        Attribute.COURSE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.COURSE,
                translation_key="course",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_COURSES,
                command=Command.SET_COURSE,
                options_map=COURSE_TO_HA,
                capability_ignore_list=[
                    *[{capability} for capability in CAPABILITIES_WITH_PROGRAMS],
                    {Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE},
                ],
            )
        ]
    },
    Capability.CUSTOM_WASHER_RINSE_CYCLES: {
        Attribute.WASHER_RINSE_CYCLES: [
            SmartThingsSelectEntityDescription(
                key=Capability.CUSTOM_WASHER_RINSE_CYCLES,
                translation_key="washer_rinse_cycles",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_WASHER_RINSE_CYCLES,
                command=Command.SET_WASHER_RINSE_CYCLES,
                supported_option=SupportedOption.RINSE_CYCLE,
            )
        ]
    },
    Capability.CUSTOM_WASHER_SOIL_LEVEL: {
        Attribute.WASHER_SOIL_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Capability.CUSTOM_WASHER_SOIL_LEVEL,
                translation_key="washer_soil_level",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_WASHER_SOIL_LEVEL,
                command=Command.SET_WASHER_SOIL_LEVEL,
                options_map=WASHER_SOIL_LEVEL_TO_HA,
                supported_option=SupportedOption.SOIL_LEVEL,
            )
        ]
    },
    Capability.CUSTOM_WASHER_SPIN_LEVEL: {
        Attribute.WASHER_SPIN_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Capability.CUSTOM_WASHER_SPIN_LEVEL,
                translation_key="washer_spin_level",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_WASHER_SPIN_LEVEL,
                command=Command.SET_WASHER_SPIN_LEVEL,
                options_map=WASHER_SPIN_LEVEL_TO_HA,
                supported_option=SupportedOption.SPIN_LEVEL,
            )
        ]
    },
    Capability.CUSTOM_WASHER_WATER_TEMPERATURE: {
        Attribute.WASHER_WATER_TEMPERATURE: [
            SmartThingsSelectEntityDescription(
                key=Capability.CUSTOM_WASHER_WATER_TEMPERATURE,
                translation_key="washer_water_temperature",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_WASHER_WATER_TEMPERATURE,
                command=Command.SET_WASHER_WATER_TEMPERATURE,
                options_map=WASHER_WATER_TEMPERATURE_TO_HA,
                supported_option=SupportedOption.WATER_TEMPERATURE,
            )
        ]
    },
    Capability.DISHWASHER_OPERATING_STATE: {
        Attribute.MACHINE_STATE: [
            SmartThingsSelectEntityDescription(
                key=Capability.DISHWASHER_OPERATING_STATE,
                translation_key="machine_state",
                options_attribute=Attribute.SUPPORTED_MACHINE_STATES,
                command=Command.SET_MACHINE_STATE,
                entity_registry_enabled_default=False,
            )
        ]
    },
    Capability.DRYER_OPERATING_STATE: {
        Attribute.MACHINE_STATE: [
            SmartThingsSelectEntityDescription(
                key=Capability.DRYER_OPERATING_STATE,
                translation_key="machine_state",
                options_attribute=Attribute.SUPPORTED_MACHINE_STATES,
                command=Command.SET_MACHINE_STATE,
            )
        ]
    },
    Capability.SAMSUNG_CE_AUTO_DISPENSE_DETERGENT: {
        Attribute.AMOUNT: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_AUTO_DISPENSE_DETERGENT,
                translation_key="auto_dispense_detergent_amount",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_AMOUNT,
                command=Command.SET_AMOUNT,
            )
        ],
        Attribute.DENSITY: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_AUTO_DISPENSE_DETERGENT,
                translation_key="auto_dispense_detergent_density",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_DENSITY,
                command=Command.SET_DENSITY,
                options_map=DISPENSE_DENSITY_TO_HA,
            )
        ],
    },
    Capability.SAMSUNG_CE_AUTO_DISPENSE_SOFTENER: {
        Attribute.AMOUNT: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_AUTO_DISPENSE_SOFTENER,
                translation_key="auto_dispense_softener_amount",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_AMOUNT,
                command=Command.SET_AMOUNT,
            )
        ],
        Attribute.DENSITY: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_AUTO_DISPENSE_DETERGENT,
                translation_key="auto_dispense_softener_density",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_DENSITY,
                command=Command.SET_DENSITY,
                options_map=DISPENSE_DENSITY_TO_HA,
            )
        ],
    },
    Capability.SAMSUNG_CE_DRYER_DRYING_TIME: {
        Attribute.DRYING_TIME: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_DRYER_DRYING_TIME,
                translation_key="dryer_drying_time",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_DRYING_TIME,
                command=Command.SET_DRYING_TIME,
            )
        ]
    },
    Capability.SAMSUNG_CE_DRYER_DRYING_TEMPERATURE: {
        Attribute.DRYING_TEMPERATURE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_DRYER_DRYING_TEMPERATURE,
                translation_key="dryer_drying_temperature",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_DRYING_TEMPERATURE,
                command=Command.SET_DRYING_TEMPERATURE,
                options_map=WASHER_WATER_TEMPERATURE_TO_HA,
                supported_option=SupportedOption.DRYING_TEMPERATURE,
            )
        ]
    },
    Capability.SAMSUNG_CE_FLEXIBLE_AUTO_DISPENSE_DETERGENT: {
        Attribute.AMOUNT: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_FLEXIBLE_AUTO_DISPENSE_DETERGENT,
                translation_key="flexible_detergent_amount",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_AMOUNT,
                command=Command.SET_AMOUNT,
            )
        ],
    },
    Capability.WASHER_OPERATING_STATE: {
        Attribute.MACHINE_STATE: [
            SmartThingsSelectEntityDescription(
                key=Capability.WASHER_OPERATING_STATE,
                translation_key="machine_state",
                options_attribute=Attribute.SUPPORTED_MACHINE_STATES,
                command=Command.SET_MACHINE_STATE,
            )
        ]
    },
    Capability.SAMSUNG_CE_LAMP: {
        Attribute.BRIGHTNESS_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_LAMP,
                translation_key="lamp",
                options_attribute=Attribute.SUPPORTED_BRIGHTNESS_LEVEL,
                command=Command.SET_BRIGHTNESS_LEVEL,
                options_map=LAMP_TO_HA,
                entity_category=EntityCategory.CONFIG,
                component_fn=lambda component: component == "hood",
                capability_ignore_list=[{Capability.SAMSUNG_CE_CONNECTION_STATE}],
            )
        ]
    },
    Capability.SAMSUNG_CE_ROBOT_CLEANER_WATER_SPRAY_LEVEL: {
        Attribute.WATER_SPRAY_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_ROBOT_CLEANER_WATER_SPRAY_LEVEL,
                translation_key="robot_cleaner_water_spray_level",
                options_attribute=Attribute.SUPPORTED_WATER_SPRAY_LEVELS,
                command=Command.SET_WATER_SPRAY_LEVEL,
                options_map=WATER_SPRAY_LEVEL_TO_HA,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_ROBOT_CLEANER_DRIVING_MODE: {
        Attribute.DRIVING_MODE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_ROBOT_CLEANER_DRIVING_MODE,
                translation_key="robot_cleaner_driving_mode",
                options_attribute=Attribute.SUPPORTED_DRIVING_MODES,
                command=Command.SET_DRIVING_MODE,
                options_map=DRIVING_MODE_TO_HA,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.SAMSUNG_CE_DUST_FILTER_ALARM: {
        Attribute.ALARM_THRESHOLD: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_DUST_FILTER_ALARM,
                translation_key="dust_filter_alarm",
                options_attribute=Attribute.SUPPORTED_ALARM_THRESHOLDS,
                command=Command.SET_ALARM_THRESHOLD,
                entity_category=EntityCategory.CONFIG,
                value_is_integer=True,
            )
        ]
    },
    Capability.SAMSUNG_CE_ROBOT_CLEANER_SYSTEM_SOUND_MODE: {
        Attribute.SOUND_MODE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_ROBOT_CLEANER_SYSTEM_SOUND_MODE,
                translation_key="robot_cleaner_sound_mode",
                options_attribute=Attribute.SUPPORTED_SOUND_MODES,
                command=Command.SET_SOUND_MODE,
                options_map=SOUND_MODE_TO_HA,
                entity_category=EntityCategory.CONFIG,
                entity_registry_enabled_default=False,
            )
        ]
    },
    Capability.SAMSUNG_CE_ROBOT_CLEANER_CLEANING_TYPE: {
        Attribute.CLEANING_TYPE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_ROBOT_CLEANER_CLEANING_TYPE,
                translation_key="robot_cleaner_cleaning_type",
                options_attribute=Attribute.SUPPORTED_CLEANING_TYPES,
                command=Command.SET_CLEANING_TYPE,
                options_map=CLEANING_TYPE_TO_HA,
                entity_category=EntityCategory.CONFIG,
            )
        ]
    },
    Capability.OVEN_MODE: {
        Attribute.OVEN_MODE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_OVEN_MODE,
                translation_key="oven_mode",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_OVEN_MODES,
                command=Command.SET_OVEN_MODE,
                options_map=OVEN_MODE_TO_HA,
                capability_ignore_list=[{Capability.SAMSUNG_CE_OVEN_MODE}],
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "oven_mode_cavity_01",
                    "cavity-02": "oven_mode_cavity_02",
                },
            )
        ],
    },
}

DISHWASHER_WASHING_OPTIONS_TO_SELECT: dict[
    Capability, dict[Attribute, list[SmartThingsSelectEntityDescription]]
] = {
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_OPTIONS: {
        Attribute.SELECTED_ZONE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_DISHWASHER_WASHING_OPTIONS,
                translation_key="selected_zone",
                options_attribute=Attribute.SELECTED_ZONE,
                command=Command.SET_SELECTED_ZONE,
                entity_category=EntityCategory.CONFIG,
                supported_option=SupportedOption.SELECTED_ZONE,
            )
        ],
        Attribute.ZONE_BOOSTER: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_DISHWASHER_WASHING_OPTIONS,
                translation_key="zone_booster",
                options_attribute=Attribute.ZONE_BOOSTER,
                command=Command.SET_ZONE_BOOSTER,
                entity_category=EntityCategory.CONFIG,
                supported_option=SupportedOption.ZONE_BOOSTER,
            )
        ],
    }
}

PROGRAMS_TO_SELECTS: dict[
    Capability, dict[Attribute, list[SmartThingsSelectEntityDescription]]
] = {
    Capability.SAMSUNG_CE_DRYER_CYCLE: {
        Attribute.DRYER_CYCLE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.DRYER_CYCLE,
                translation_key="cycle",
                entity_category=EntityCategory.CONFIG,
                command=Command.SET_DRYER_CYCLE,
            )
        ]
    },
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: {
        Attribute.STEAM_CLOSET_CYCLE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.STEAM_CLOSET_CYCLE,
                translation_key="cycle",
                entity_category=EntityCategory.CONFIG,
                command=Command.SET_STEAM_CLOSET_CYCLE,
            )
        ]
    },
    Capability.SAMSUNG_CE_WASHER_CYCLE: {
        Attribute.WASHER_CYCLE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_CYCLE,
                translation_key="cycle",
                entity_category=EntityCategory.CONFIG,
                command=Command.SET_WASHER_CYCLE,
            )
        ]
    },
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE: {
        Attribute.WASHING_COURSE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
                translation_key="dishwasher_course",
                options_attribute=Attribute.SUPPORTED_COURSES,
                command=Command.SET_WASHING_COURSE,
            )
        ]
    },
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE_DETAILS: {
        Attribute.WASHING_COURSE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE_DETAILS,
                translation_key="dishwasher_course",
                options_attribute=Attribute.SUPPORTED_COURSES,
                command=Command.SET_WASHING_COURSE,
                capability_ignore_list=[
                    {Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE}
                ],
            )
        ]
    },
}


OVEN_MODES_TO_SELECTS: dict[
    Capability, dict[Attribute, list[SmartThingsSelectEntityDescription]]
] = {
    Capability.SAMSUNG_CE_OVEN_MODE: {
        Attribute.OVEN_MODE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_OVEN_MODE,
                translation_key="oven_mode",
                entity_category=EntityCategory.CONFIG,
                options_attribute=Attribute.SUPPORTED_OVEN_MODES,
                command=Command.SET_OVEN_MODE,
                component_fn=lambda component: component in ["cavity-01", "cavity-02"],
                component_translation_key={
                    "cavity-01": "oven_mode_cavity_01",
                    "cavity-02": "oven_mode_cavity_02",
                },
            )
        ],
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartThingsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add selects for a config entry."""
    entry_data = entry.runtime_data
    select_entities: list[SmartThingsSelect | SmartThingsDishwasherOptionSelect] = []
    program_select_entities: list[SmartThingsProgramSelect] = []
    oven_select_entities: list[SmartThingsOvenModeSelect] = []

    for device in entry_data.devices.values():
        select_entities.extend(
            SmartThingsSelect(
                entry_data.client, device, description, capability, attribute, component
            )
            for capability, attributes in CAPABILITY_TO_SELECTS.items()
            for component, capabilities in device.status.items()
            if capability in capabilities
            for attribute, descriptions in attributes.items()
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
        )

        select_entities.extend(
            SmartThingsDishwasherOptionSelect(
                entry_data.client, device, description, capability, attribute, component
            )
            for capability, attributes in DISHWASHER_WASHING_OPTIONS_TO_SELECT.items()
            for component, capabilities in device.status.items()
            if capability in capabilities
            if (supp := capabilities[capability].get(Attribute.SUPPORTED_LIST))
            and supp.value
            for attribute, descriptions in attributes.items()
            if attribute in cast(list[str], supp.value)
            for description in descriptions
        )

        program_select_entities.extend(
            SmartThingsProgramSelect(
                entry_data.client, device, description, capability, attribute, component
            )
            for capability, attributes in PROGRAMS_TO_SELECTS.items()
            for component, capabilities in device.status.items()
            if capability in capabilities
            for attribute, descriptions in attributes.items()
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
        )

        oven_select_entities.extend(
            SmartThingsOvenModeSelect(
                entry_data.client, device, description, capability, attribute, component
            )
            for capability, attributes in OVEN_MODES_TO_SELECTS.items()
            for component, capabilities in device.status.items()
            if capability in capabilities
            for attribute, descriptions in attributes.items()
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
        )

    async_add_entities(select_entities + program_select_entities + oven_select_entities)

    program_entities: list[str] = [
        select_entity.entity_id for select_entity in program_select_entities
    ]
    program_entities += [
        select_entity.entity_id for select_entity in oven_select_entities
    ]

    @callback
    def select_state_listener(event: Event[EventStateChangedData]) -> None:
        """Handle state changes of the sensor entity."""
        source_entity_id = event.data["entity_id"]
        new_state = event.data["new_state"]
        old_state = event.data["old_state"]

        if new_state is None or (old_state and old_state.state == new_state.state):
            return
        if new_state.state in [None, "unknown", "unavailable"]:
            return

        source_ent = next(
            (
                ent
                for ent in (program_select_entities + oven_select_entities)
                if ent.entity_id == source_entity_id
            ),
            None,
        )
        if not source_ent:
            return

        source_device_id = source_ent.device.device.device_id

        if isinstance(source_ent, SmartThingsProgramSelect):
            source_ent.device.selected_course = translate_program_course(new_state.state)
            for select_entity in select_entities:
                if (
                    select_entity.device.device.device_id == source_device_id
                    and select_entity.entity_description.supported_option
                ):
                    select_entity.update_default_values(source_ent.device.selected_course)

        if isinstance(source_ent, SmartThingsOvenModeSelect):
            for select_entity in oven_select_entities:
                if select_entity.device.device.device_id == source_device_id:
                    if select_entity.entity_id == source_entity_id:
                        select_entity.async_write_ha_state()
                        async_dispatcher_send(
                            hass,
                            f"smartthings_oven_mode_changed_{source_device_id}_{select_entity.component}",
                            new_state.state,
                        )

    async_track_state_change_event(hass, program_entities, select_state_listener)


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
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        super().__init__(client, device, {capability}, component=component)
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{entity_description.key}"
        self._attribute = attribute
        self.capability = capability
        self.entity_description = entity_description
        self.command = self.entity_description.command
        if self.entity_description.component_translation_key and component != MAIN:
            self._attr_translation_key = (
                self.entity_description.component_translation_key[component]
            )
        self._attr_current_option = None

    @property
    def options(self) -> list[str]:
        """Return the list of options."""
        options = []
        if self.entity_description.supported_option and self.device.programs:
            if active_course := self.device.selected_course:
                options = get_program_options(
                    self.device.programs,
                    active_course,
                    self.entity_description.supported_option,
                ) or []
        if not options and self.entity_description.options_attribute:
            options = self.get_attribute_value(
                self.capability, self.entity_description.options_attribute
            ) or []
        if self.entity_description.options_map:
            options = [
                self.entity_description.options_map.get(option, option)
                for option in options
            ]
        if self.entity_description.value_is_integer or any(isinstance(o, int) for o in options):
            options = [str(option) for option in options]

        return options

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self._attr_current_option is not None:
            return self._attr_current_option

        raw_value = self.get_attribute_value(self.capability, self._attribute)
        new_value = str(raw_value) if raw_value else None
        if self.entity_description.options_map and new_value is not None:
            new_value = self.entity_description.options_map.get(new_value, new_value)
        return str(new_value) if new_value is not None else None

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        self._attr_current_option = None
        new_option: str | int = option
        if self.entity_description.options_map:
            new_option = next(
                (
                    key
                    for key, value in self.entity_description.options_map.items()
                    if value == option
                ),
                new_option,
            )
        if self.entity_description.value_is_integer:
            new_option = int(new_option)
        if self.command:
            await self.execute_device_command(
                self.capability,
                self.command,
                new_option,
            )

    def update_default_values(self, program_id: str | None) -> None:
        """Enforce setting default values when cycle courses changes."""
        self._attr_current_option = None
        if program_id and self.entity_description.supported_option:
            program = self.device.programs.get(program_id)
            if program and (
                opt_data := program.supportedoptions.get(
                    self.entity_description.supported_option
                )
            ):
                if (default_val := getattr(opt_data, "default", None)) is not None:
                    default_str = str(default_val)
                    if self.entity_description.options_map:
                        default_str = self.entity_description.options_map.get(
                            default_str, default_str
                        )

                    self._attr_current_option = default_str

        self.async_write_ha_state()

    @callback
    def _handle_update(self) -> None:
        """Reset staged value when API confirms value."""
        if self._attr_current_option is not None:
            new_value = self.get_attribute_value(self.capability, self._attribute)
            if self.entity_description.options_map:
                new_value = self.entity_description.options_map.get(
                    new_value, new_value
                )
            if str(new_value) == self._attr_current_option:
                self._attr_current_option = None
        super()._handle_update()


class SmartThingsDishwasherOptionSelect(SmartThingsEntity, SelectEntity):
    """Define a SmartThings select for a dishwasher washing option."""

    entity_description: SmartThingsSelectEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsSelectEntityDescription,
        capability: Capability,
        attribute: Attribute,
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        capabilities = {capability}
        capabilities.add(Capability.DISHWASHER_OPERATING_STATE)
        capabilities.add(Capability.SAMSUNG_CE_DISHWASHER_OPERATION)
        capabilities.add(Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE)
        capabilities.add(Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE_DETAILS)
        if entity_description.supported_option:
            capabilities.add(Capability.REMOTE_CONTROL_STATUS)
        super().__init__(client, device, capabilities, component=component)
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{entity_description.key}"
        self._attribute = attribute
        self.capability = capability
        self.entity_description = entity_description
        self.command = self.entity_description.command
        self._attr_current_option = None

    @property
    def options(self) -> list[str]:
        """Return the list of options."""
        options = []
        if self.entity_description.supported_option and self.device.programs:
            if active_course := self.device.selected_course:
                options = get_program_options(
                    self.device.programs,
                    active_course,
                    self.entity_description.supported_option,
                ) or []
        if not options and self.entity_description.options_attribute:
            options = (
                self.get_attribute_value(
                    self.capability, self.entity_description.options_attribute
                )["settable"]
                or []
            )
        if self.entity_description.options_map:
            options = [
                self.entity_description.options_map.get(option, option)
                for option in options
            ]
        if self.entity_description.value_is_integer:
            options = [str(option) for option in options]
        return options

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self._attr_current_option is not None:
            return self._attr_current_option

        raw_status = self.get_attribute_value(self.capability, self._attribute)
        if isinstance(raw_status, dict) and "value" in raw_status:
            new_value = str(raw_status["value"])
        else:
            new_value = str(raw_status) if raw_status else None
        if self.entity_description.options_map and new_value is not None:
            new_value = self.entity_description.options_map.get(new_value, new_value)
        return str(new_value) if new_value is not None else None

    def _validate_before_select(self) -> None:
        """Validate that the select can be used."""
        if (
            self.get_attribute_value(
                Capability.REMOTE_CONTROL_STATUS, Attribute.REMOTE_CONTROL_ENABLED
            )
            == "false"
        ):
            raise ServiceValidationError(
                "Can only be updated when remote control is enabled"
            )
        if (
            self.get_attribute_value(
                Capability.DISHWASHER_OPERATING_STATE, Attribute.MACHINE_STATE
            )
            != "stop"
        ):
            raise ServiceValidationError(
                "Can only be updated when dishwasher machine state is stop"
            )

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        self._attr_current_option = None
        self._validate_before_select()
        selected_course = self.get_attribute_value(
            Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE, Attribute.WASHING_COURSE
        )
        options = {
            opt_key: self.get_attribute_value(self.capability, opt_key)["value"]
            for opt_key in self.get_attribute_value(
                self.capability, Attribute.SUPPORTED_LIST
            )
        }
        options[self.entity_description.options_attribute] = option
        await self.execute_device_command(
            Capability.SAMSUNG_CE_DISHWASHER_OPERATION,
            Command.CANCEL,
            False,
        )
        await self.execute_device_command(
            Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
            Command.SET_WASHING_COURSE,
            selected_course,
        )
        await self.execute_device_command(
            self.capability,
            Command.SET_OPTIONS,
            options,
        )

    def update_default_values(self, program_id: str | None) -> None:
        """Update the options for this select entity."""

        self._attr_current_option = None
        if program_id and self.entity_description.supported_option:
            program = self.device.programs.get(program_id)
            if program and (
                opt_data := program.supportedoptions.get(
                    self.entity_description.supported_option
                )
            ):
                if (default_val := getattr(opt_data, "default", None)) is not None:
                    default_str = str(default_val)
                    if self.entity_description.options_map:
                        default_str = self.entity_description.options_map.get(
                            default_str, default_str
                        )

                    self._attr_current_option = default_str

        self.async_write_ha_state()

    @callback
    def _handle_update(self) -> None:
        """Reset staged value when API confirms value."""
        if self._attr_current_option is not None:
            new_value = self.get_attribute_value(self.capability, self._attribute)
            if self.entity_description.options_map:
                new_value = self.entity_description.options_map.get(
                    new_value, new_value
                )
            if str(new_value) == self._attr_current_option:
                self._attr_current_option = None
        super()._handle_update()

class SmartThingsProgramSelect(SmartThingsEntity, SelectEntity):
    """Define a SmartThings select."""

    entity_description: SmartThingsSelectEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsSelectEntityDescription,
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
        if (table_id := get_program_table_id(device.status)) != "":
            self._attr_translation_key = (
                f"{self.entity_description.translation_key}_{table_id}"
            )

    @property
    def options(self) -> list[str]:
        """Return the list of options."""

        if self.entity_description.options_attribute:
            options: list[str] = (
                self.get_attribute_value(
                    self.capability, self.entity_description.options_attribute
                )
                or []
            )
            return [translate_program_course(option) for option in options]
        return list(self.device.programs)

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        raw_value = self.get_attribute_value(self.capability, self._attribute)
        if raw_value is None:
            return None

        value = translate_program_course(raw_value)
        if value not in self.options:
            return None

        return value

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if self.command is not None:
            await self.execute_device_command(
                self.capability,
                self.command,
                command_program_course(option),
            )


class SmartThingsOvenModeSelect(SmartThingsEntity, SelectEntity):
    """Define a SmartThings select."""

    entity_description: SmartThingsSelectEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsSelectEntityDescription,
        capability: Capability,
        attribute: Attribute,
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        capabilities = {capability}
        capabilities.add(Capability.SAMSUNG_CE_KITCHEN_MODE_SPECIFICATION)
        capabilities.add(Capability.CUSTOM_OVEN_CAVITY_STATUS)
        capabilities.add(Capability.REMOTE_CONTROL_STATUS)
        super().__init__(client, device, capabilities, component=component)
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{entity_description.key}"
        self._attribute = attribute
        self.capability = capability
        self.entity_description = entity_description
        self.command = self.entity_description.command
        if self.entity_description.component_translation_key and component != MAIN:
            self._attr_translation_key = (
                self.entity_description.component_translation_key[component]
            )

    @property
    def options(self) -> list[str]:
        """Return the list of options."""
        cavity_key = get_current_cavity_id(self.device.status, self.component)
        return [
            prog_id.split("_", 1)[-1]
            for prog_id in self.device.programs
            if prog_id.startswith(f"{cavity_key}_")
        ]

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        value = None
        cavity_key = get_current_cavity_id(self.device.status, self.component)
        if self.device.modes and cavity_key in self.device.modes:
            value = self.device.modes[cavity_key].active_mode
        if value not in self.options:
            return None

        return value

    async def async_select_option(self, option: str) -> None:
        """Change the selected option locally."""
        cavity_key = get_current_cavity_id(self.device.status, self.component)
        if self.device.modes and cavity_key in self.device.modes:
            self.device.modes[cavity_key].active_mode = option
            self._attr_current_option = option
            self.async_write_ha_state()

        async_dispatcher_send(
            self.hass,
            f"smartthings_oven_mode_changed_{self.device.device.device_id}_{self.component}",
            option,
        )

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()

        @callback
        def on_oven_state_changed(is_divided: bool = False) -> None:
            """Handles update of the binary_sensor which switches between Single/Dual cook modes."""
            cavity_key = get_current_cavity_id(self.device.status, self.component)
            if self.device.modes and cavity_key in self.device.modes:
                active_mode = self.device.modes[cavity_key].active_mode
                self._attr_current_option = active_mode
                self.async_write_ha_state()

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"smartthings_oven_state_changed_{self.device.device.device_id}",
                on_oven_state_changed,
            )
        )
