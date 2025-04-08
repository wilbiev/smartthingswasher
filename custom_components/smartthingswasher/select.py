"""Support for selects through the SmartThings cloud API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pysmartthings import Attribute, Capability, Command, SmartThings

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import FullDevice, SmartThingsConfigEntry
from .const import MAIN
from .entity import SmartThingsEntity
from .models import SupportedOption
from .utils import get_program_options, translate_program_course


@dataclass(frozen=True, kw_only=True)
class SmartThingsSelectEntityDescription(SelectEntityDescription):
    """Describe a SmartThings select entity."""

    options_attribute: Attribute | None = None
    command: Command | None = None
    except_if_state_none: bool = False
    supported_option: SupportedOption | None = None


CAPABILITY_TO_SELECTS: dict[
    Capability, dict[Attribute, list[SelectEntityDescription]]
] = {
    Capability.DISHWASHER_OPERATING_STATE: {
        Attribute.MACHINE_STATE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.MACHINE_STATE,
                translation_key="machine_state",
                icon="mdi:play-speed",
                options_attribute=Attribute.SUPPORTED_MACHINE_STATES,
                command=Command.SET_MACHINE_STATE,
            )
        ]
    },
    Capability.DRYER_OPERATING_STATE: {
        Attribute.MACHINE_STATE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.MACHINE_STATE,
                translation_key="machine_state",
                icon="mdi:play-speed",
                options_attribute=Attribute.SUPPORTED_MACHINE_STATES,
                command=Command.SET_MACHINE_STATE,
            )
        ]
    },
    Capability.SAMSUNG_CE_AUTO_DISPENSE_DETERGENT: {
        Attribute.AMOUNT: [
            SmartThingsSelectEntityDescription(
                key="auto_detergent",
                translation_key="auto_dispense_detergent_amount",
                icon="mdi:bottle-tonic",
                options_attribute=Attribute.SUPPORTED_AMOUNT,
                command=Command.SET_AMOUNT,
            )
        ]
    },
    Capability.SAMSUNG_CE_AUTO_DISPENSE_SOFTENER: {
        Attribute.AMOUNT: [
            SmartThingsSelectEntityDescription(
                key="auto_softener",
                translation_key="auto_dispense_softener_amount",
                icon="mdi:bottle-tonic",
                options_attribute=Attribute.SUPPORTED_AMOUNT,
                command=Command.SET_AMOUNT,
            )
        ]
    },
    Capability.CUSTOM_DRYER_DRY_LEVEL: {
        Attribute.DRYER_DRY_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Attribute.DRYER_DRY_LEVEL,
                translation_key="dryer_dry_level",
                icon="mdi:waves-arrow-up",
                options_attribute=Attribute.SUPPORTED_DRYER_DRY_LEVEL,
                command=Command.SET_DRYER_DRY_LEVEL,
                supported_option=SupportedOption.DRYING_LEVEL,
            )
        ]
    },
    Capability.CUSTOM_SUPPORTED_OPTIONS: {
        Attribute.COURSE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.COURSE,
                translation_key="course",
                icon="mdi:list-box-outline",
                options_attribute=Attribute.SUPPORTED_COURSES,
                command=Command.SET_COURSE,
            )
        ]
    },
    Capability.CUSTOM_WASHER_RINSE_CYCLES: {
        Attribute.WASHER_RINSE_CYCLES: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_RINSE_CYCLES,
                translation_key="washer_rinse_cycles",
                icon="mdi:water-sync",
                options_attribute=Attribute.SUPPORTED_WASHER_RINSE_CYCLES,
                command=Command.SET_WASHER_RINSE_CYCLES,
                supported_option=SupportedOption.RINSE_CYCLE,
            )
        ]
    },
    Capability.CUSTOM_WASHER_SOIL_LEVEL: {
        Attribute.WASHER_SOIL_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_SOIL_LEVEL,
                translation_key="washer_soil_level",
                icon="mdi:brightness-7",
                options_attribute=Attribute.SUPPORTED_WASHER_SOIL_LEVEL,
                command=Command.SET_WASHER_SOIL_LEVEL,
                supported_option=SupportedOption.SOIL_LEVEL,
            )
        ]
    },
    Capability.CUSTOM_WASHER_SPIN_LEVEL: {
        Attribute.WASHER_SPIN_LEVEL: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_SPIN_LEVEL,
                translation_key="washer_spin_level",
                icon="mdi:autorenew",
                options_attribute=Attribute.SUPPORTED_WASHER_SPIN_LEVEL,
                command=Command.SET_WASHER_SPIN_LEVEL,
                supported_option=SupportedOption.SPIN_LEVEL,
            )
        ]
    },
    Capability.CUSTOM_WASHER_WATER_TEMPERATURE: {
        Attribute.WASHER_WATER_TEMPERATURE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_WATER_TEMPERATURE,
                translation_key="washer_water_temperature",
                icon="mdi:water-thermometer",
                options_attribute=Attribute.SUPPORTED_WASHER_WATER_TEMPERATURE,
                command=Command.SET_WASHER_WATER_TEMPERATURE,
                supported_option=SupportedOption.WATER_TEMPERATURE,
            )
        ]
    },
    Capability.WASHER_OPERATING_STATE: {
        Attribute.MACHINE_STATE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.MACHINE_STATE,
                translation_key="machine_state",
                icon="mdi:play-speed",
                options_attribute=Attribute.SUPPORTED_MACHINE_STATES,
                command=Command.SET_MACHINE_STATE,
            )
        ]
    },
}


PROGRAMS_TO_SELECTS: dict[
    Capability, dict[Attribute, list[SelectEntityDescription]]
] = {
    Capability.SAMSUNG_CE_WASHER_CYCLE: {
        Attribute.WASHER_CYCLE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.WASHER_CYCLE,
                translation_key="washer_cycle",
                icon="mdi:list-box-outline",
                command=Command.SET_WASHER_CYCLE,
            )
        ]
    },
    Capability.SAMSUNG_CE_DRYER_CYCLE: {
        Attribute.DRYER_CYCLE: [
            SmartThingsSelectEntityDescription(
                key=Attribute.DRYER_CYCLE,
                translation_key="dryer_cycle",
                icon="mdi:list-box-outline",
                command=Command.SET_DRYER_CYCLE,
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
        )
        for device in entry_data.devices.values()
        for capability, attributes in CAPABILITY_TO_SELECTS.items()
        if capability in device.status[MAIN]
        for attribute, descriptions in attributes.items()
        for description in descriptions
    ]
    async_add_entities(select_entities)

    program_select_entities = [
        SmartThingsProgramSelect(
            entry_data.client,
            device,
            description,
            capability,
            attribute,
        )
        for device in entry_data.devices.values()
        for capability, attributes in PROGRAMS_TO_SELECTS.items()
        if capability in device.status[MAIN]
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
                    == "false"
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
        await self.execute_device_command(
            self.capability,
            self.command,
            option,
        )

    def update_select_options(self, options: list[str]) -> None:
        """Update the options for this select entity."""
        self._attr_options = options
        self.async_write_ha_state()


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
        value = translate_program_course(option)
        await self.execute_device_command(
            self.capability,
            self.command,
            value,
        )
