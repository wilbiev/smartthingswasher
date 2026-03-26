"""Support for selects through the SmartThings cloud API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import cast

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
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
    SOUND_MODE_TO_HA,
    WASHER_SOIL_LEVEL_TO_HA,
    WASHER_SPIN_LEVEL_TO_HA,
    WASHER_WATER_TEMPERATURE_TO_HA,
    WASHING_COURSE_TO_HA,
    WATER_SPRAY_LEVEL_TO_HA,
)
from .entity import SmartThingsEntity
from .models import SupportedOption
from .util import get_program_options, get_program_table_id, translate_program_course


@dataclass(frozen=True, kw_only=True)
class SmartThingsSelectEntityDescription(SelectEntityDescription):
    """Describe a SmartThings select entity."""

    command: Command | None = None
    options_attribute: Attribute | None = None
    supported_option: SupportedOption | None = None
    extra_components: list[str] | None = None
    capability_ignore_list: list[Capability] | None = None


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
                    *CAPABILITIES_WITH_PROGRAMS,
                    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE
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
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE: {
        Attribute.WASHING_COURSE: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE,
                translation_key="washing_course",
                options_attribute=Attribute.SUPPORTED_COURSES,
                command=Command.SET_WASHING_COURSE,
                options_map=WASHING_COURSE_TO_HA,
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
                extra_components=["hood"],
                capability_ignore_list=[Capability.SAMSUNG_CE_CONNECTION_STATE],
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
            )
        ],
        Attribute.ZONE_BOOSTER: [
            SmartThingsSelectEntityDescription(
                key=Capability.SAMSUNG_CE_DISHWASHER_WASHING_OPTIONS,
                translation_key="zone_booster",
                options_attribute=Attribute.ZONE_BOOSTER,
                command=Command.SET_ZONE_BOOSTER,
                entity_category=EntityCategory.CONFIG,
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
        Attribute.DRYER_CYCLE: [
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
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartThingsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add selects for a config entry."""
    entry_data = entry.runtime_data
    select_entities = [
        SmartThingsSelect(
            entry_data.client,
            device,
            description,
            capability,
            attribute,
            component,
        )
        for device in entry_data.devices.values()
        for capability, attributes in CAPABILITY_TO_SELECTS.items()
        for component in device.status
        if capability in device.status[component]
        for attribute, descriptions in attributes.items()
        for description in descriptions
        if (
            (component == MAIN or (
                description.extra_components is not None
                and component in description.extra_components
            ))
            and (
                description.capability_ignore_list is None
                or all(
                    capability not in device.status[component]
                    for capability in description.capability_ignore_list
                )
            )
        )
    ]
    async_add_entities(select_entities)

    select_dishwasher_entities = [
        SmartThingsDishwasherOptionSelect(
            entry_data.client,
            device,
            description,
            capability,
            attribute,
            component,
        )
        for device in entry_data.devices.values()
        for capability, attributes in DISHWASHER_WASHING_OPTIONS_TO_SELECT.items()
        for component in device.status
        if capability in device.status[component]
        for attribute, descriptions in attributes.items()
        for attribute in cast(
            list[str],
            device.status[component][Capability.SAMSUNG_CE_DISHWASHER_WASHING_OPTIONS][
                Attribute.SUPPORTED_LIST
            ].value,
        )
        for description in descriptions
    ]
    async_add_entities(select_dishwasher_entities)

    program_select_entities = [
        SmartThingsProgramSelect(
            entry_data.client,
            device,
            description,
            capability,
            attribute,
            component,
        )
        for device in entry_data.devices.values()
        for capability, attributes in PROGRAMS_TO_SELECTS.items()
        for component in device.status
        if capability in device.status[component]
        for attribute, descriptions in attributes.items()
        for description in descriptions
    ]
    async_add_entities(program_select_entities)

    program_entities: list[str] = [
        select_entity.entity_id for select_entity in program_select_entities
    ]

    @callback
    def select_state_listener(event: Event[EventStateChangedData]) -> None:
        """Handle state changes of the sensor entity."""
        entity_id = event.data["entity_id"]
        new_state = event.data["new_state"]
        if new_state is None:
            return

        device_name: str = entity_id.split(".")[1]
        for select_entity in select_entities:
            if (
                device_name.startswith(select_entity.device.device.label.lower())
                and select_entity.entity_description.supported_option
            ):
                if (
                    select_entity.get_attribute_value(
                        Capability.REMOTE_CONTROL_STATUS,
                        Attribute.REMOTE_CONTROL_ENABLED,
                    )
                    == "false" and select_entity.entity_description.options_attribute is not None
                ):
                    if (
                        options := select_entity.get_attribute_value(
                            select_entity.capability,
                            select_entity.entity_description.options_attribute,
                        )
                    ) is not None:
                        select_entity.update_select_options(
                            [option.lower() for option in options]
                        )
                elif (
                    options := get_program_options(
                        select_entity.device.programs,
                        translate_program_course(new_state.state),
                        select_entity.entity_description.supported_option,
                    )
                ) is not None:
                    select_entity.update_select_options(options)

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
        capabilities = {capability}
        if entity_description.supported_option:
            capabilities.add(Capability.REMOTE_CONTROL_STATUS)
        super().__init__(client, device, capabilities, component=component)
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{entity_description.key}"
        self._attribute = attribute
        self.capability = capability
        self.entity_description = entity_description
        self.command = self.entity_description.command
        options: list[str] = []
        if self.entity_description.options_attribute:
            if (
                options := self.get_attribute_value(
                    self.capability, self.entity_description.options_attribute
                )
            ) is not None:
                [option.lower() for option in options]
        self._attr_options = options

    @property
    def native_value(self) -> str | float | datetime | int | None:
        """Return the state of the select."""
        return self.get_attribute_value(self.capability, self._attribute)

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        value = self.get_attribute_value(self.capability, self._attribute)
        if value is None or value not in self._attr_options:
            return None
        return value

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if self.command is not None:
            await self.execute_device_command(
                self.capability,
                self.command,
                option,
            )

    def update_select_options(self, options: list[str]) -> None:
        """Update the options for this select entity."""
        self._attr_options = options
        self.async_write_ha_state()


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


    @property
    def options(self) -> list[str]:
        """Return the list of options."""
        device_options = self.get_attribute_value(
            self.capability, self.entity_description.options_attribute
        )["settable"]
        selected_course = self.get_attribute_value(
            Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE, Attribute.WASHING_COURSE
        )
        course_details = self.get_attribute_value(
            Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE_DETAILS,
            Attribute.PREDEFINED_COURSES,
        )
        course_options = set(
            next(
                (
                    detail["options"][self.entity_description.options_attribute][
                        "settable"
                    ]
                    for detail in course_details
                    if detail["courseName"] == selected_course
                ),
                [],
            )
        )
        return [option for option in device_options if option in course_options]

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        return self.get_attribute_value(
            self.capability, self._attribute
        )["value"]

    def _validate_before_select(self) -> None:
        """Validate that the select can be used."""
        super()._validate_before_select()
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
        self._validate_before_select()
        selected_course = self.get_attribute_value(
            Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE, Attribute.WASHING_COURSE
        )
        options = {
            option: self.get_attribute_value(self.capability, option)[
                "value"
            ]
            for option in self.get_attribute_value(
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
        options: list[str] = []
        if self.entity_description.options_attribute:
            if (
                options := self.get_attribute_value(
                    self.capability, self.entity_description.options_attribute
                )
            ) is not None:
                [option.lower() for option in options]
        else:
            for program in self.device.programs:
                options.append(program.lower())
        self._attr_options = options

    @property
    def native_value(self) -> str | float | datetime | int | None:
        """Return the state of the select."""
        return translate_program_course(
            self.get_attribute_value(self.capability, self._attribute)
        ).lower()

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        value = translate_program_course(
            self.get_attribute_value(self.capability, self._attribute)
        ).lower()
        if value is None or value not in self._attr_options:
            return None
        return value

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if self.command is not None:
            value = translate_program_course(option)
            await self.execute_device_command(
                self.capability,
                self.command,
                value,
            )
