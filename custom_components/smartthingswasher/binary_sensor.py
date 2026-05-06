"""Support for binary sensors through the SmartThings cloud API."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from pysmartthings import Attribute, Capability, Category, SmartThings, Status

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from . import FullDevice, SmartThingsConfigEntry
from .const import CAPABILITY_COURSES, MAIN
from .entity import SmartThingsEntity
from .models import SupportedOption
from .util import translate_program_course


@dataclass(frozen=True, kw_only=True)
class SmartThingsBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a SmartThings binary sensor entity."""

    is_on_key: str | bool | None = None
    category_device_class: dict[Category | str, BinarySensorDeviceClass] | None = None
    category: set[Category] | None = None
    component_fn: Callable[[str], bool] | None = None
    component_translation_key: dict[str, str] | None = None
    supported_states_attributes: Attribute | None = None
    exists_fn: Callable[[Status], bool] | None = None


CAPABILITY_TO_SENSORS: dict[
    Capability, dict[Attribute, list[SmartThingsBinarySensorEntityDescription]]
] = {
    Capability.ACCELERATION_SENSOR: {
        Attribute.ACCELERATION: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.ACCELERATION,
                translation_key="acceleration",
                device_class=BinarySensorDeviceClass.MOVING,
                is_on_key="active",
            )
        ]
    },
    Capability.CONTACT_SENSOR: {
        Attribute.CONTACT: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.CONTACT,
                device_class=BinarySensorDeviceClass.DOOR,
                is_on_key="open",
                category_device_class={
                    Category.GARAGE_DOOR: BinarySensorDeviceClass.GARAGE_DOOR,
                    Category.DOOR: BinarySensorDeviceClass.DOOR,
                    Category.WINDOW: BinarySensorDeviceClass.WINDOW,
                },
                component_fn=lambda component: component
                in {"freezer", "cooler", "cvroom"},
                component_translation_key={
                    "freezer": "freezer_door",
                    "cooler": "cooler_door",
                    "cvroom": "cool_select_plus_door",
                },
            )
        ]
    },
    Capability.CUSTOM_DRYER_WRINKLE_PREVENT: {
        Attribute.OPERATING_STATE: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.OPERATING_STATE,
                translation_key="dryer_wrinkle_prevent_active",
                is_on_key="running",
                entity_category=EntityCategory.DIAGNOSTIC,
            )
        ]
    },
    Capability.FILTER_STATUS: {
        Attribute.FILTER_STATUS: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.FILTER_STATUS,
                translation_key="filter_status",
                device_class=BinarySensorDeviceClass.PROBLEM,
                is_on_key="replace",
            )
        ]
    },
    Capability.CUSTOM_WATER_FILTER: {
        Attribute.WATER_FILTER_STATUS: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.WATER_FILTER_STATUS,
                translation_key="filter_status",
                device_class=BinarySensorDeviceClass.PROBLEM,
                is_on_key="replace",
            )
        ]
    },
    Capability.SAMSUNG_CE_WATER_RESERVOIR: {
        Attribute.SLOT_STATE: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.SLOT_STATE,
                translation_key="water_reservoir",
                is_on_key="open",
                exists_fn=lambda status: status.value is not None
                and isinstance(status.value, str),
            )
        ]
    },
    Capability.SAMSUNG_CE_STEAM_CLOSET_KEEP_FRESH_MODE: {
        Attribute.OPERATING_STATE: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.OPERATING_STATE,
                translation_key="keep_fresh_mode_active",
                is_on_key="running",
                entity_category=EntityCategory.DIAGNOSTIC,
            )
        ]
    },
    Capability.REMOTE_CONTROL_STATUS: {
        Attribute.REMOTE_CONTROL_ENABLED: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.REMOTE_CONTROL_ENABLED,
                translation_key="remote_control",
                is_on_key="true",
            )
        ]
    },
    Capability.SAMSUNG_CE_KIDS_LOCK: {
        Attribute.LOCK_STATE: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.LOCK_STATE,
                translation_key="child_lock",
                is_on_key="locked",
            )
        ]
    },
    Capability.MOTION_SENSOR: {
        Attribute.MOTION: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.MOTION,
                device_class=BinarySensorDeviceClass.MOTION,
                is_on_key="active",
            )
        ]
    },
    Capability.PRESENCE_SENSOR: {
        Attribute.PRESENCE: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.PRESENCE,
                device_class=BinarySensorDeviceClass.PRESENCE,
                is_on_key="present",
            )
        ]
    },
    Capability.SOUND_SENSOR: {
        Attribute.SOUND: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.SOUND,
                device_class=BinarySensorDeviceClass.SOUND,
                is_on_key="detected",
            )
        ]
    },
    Capability.TAMPER_ALERT: {
        Attribute.TAMPER: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.TAMPER,
                device_class=BinarySensorDeviceClass.TAMPER,
                is_on_key="detected",
                entity_category=EntityCategory.DIAGNOSTIC,
            )
        ]
    },
    Capability.WATER_SENSOR: {
        Attribute.WATER: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.WATER,
                device_class=BinarySensorDeviceClass.MOISTURE,
                is_on_key="wet",
            )
        ]
    },
    Capability.SAMSUNG_CE_DOOR_STATE: {
        Attribute.DOOR_STATE: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.DOOR_STATE,
                translation_key="door",
                device_class=BinarySensorDeviceClass.OPENING,
                is_on_key="open",
                component_fn=lambda component: component == "cavity-02",
                component_translation_key={
                    "cavity-02": "door_cavity_02",
                },
            )
        ]
    },
    Capability.CUSTOM_OVEN_CAVITY_STATUS: {
        Attribute.OVEN_CAVITY_STATUS: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.OVEN_CAVITY_STATUS,
                is_on_key="on",
                component_fn=lambda component: component == "cavity-01",
                component_translation_key={
                    "cavity-01": "oven_status_cavity_01",
                },
            )
        ]
    },
    Capability.GAS_DETECTOR: {
        Attribute.GAS: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.GAS,
                device_class=BinarySensorDeviceClass.GAS,
                is_on_key="detected",
            )
        ]
    },
    Capability.SAMSUNG_CE_ROBOT_CLEANER_DUST_BAG: {
        Attribute.STATUS: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.STATUS,
                is_on_key="full",
                component_fn=lambda component: component == "station",
                component_translation_key={
                    "station": "robot_cleaner_dust_bag",
                },
                supported_states_attributes=Attribute.SUPPORTED_STATUS,
            )
        ]
    },
    Capability.CUSTOM_COOKTOP_OPERATING_STATE: {
        Attribute.COOKTOP_OPERATING_STATE: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.COOKTOP_OPERATING_STATE,
                translation_key="cooktop_operating_state",
                is_on_key="run",
                supported_states_attributes=Attribute.SUPPORTED_COOKTOP_OPERATING_STATE,
            )
        ]
    },
    Capability.SAMSUNG_CE_MICROFIBER_FILTER_STATUS: {
        Attribute.STATUS: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.STATUS,
                translation_key="microfiber_filter_blockage",
                is_on_key="blockage",
                device_class=BinarySensorDeviceClass.PROBLEM,
                entity_category=EntityCategory.DIAGNOSTIC,
            )
        ]
    },
    Capability.SAMSUNG_CE_STICK_CLEANER_DUST_BAG: {
        Attribute.STATUS: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.STATUS,
                is_on_key="full",
                component_fn=lambda component: component == "station",
                component_translation_key={
                    "station": "stick_cleaner_dust_bag",
                },
                device_class=BinarySensorDeviceClass.PROBLEM,
            )
        ]
    },
    Capability.SAMSUNG_CE_CLEAN_STATION_STICK_STATUS: {
        Attribute.STATUS: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.STATUS,
                component_fn=lambda component: component == "station",
                component_translation_key={
                    "station": "stick_cleaner_status",
                },
                is_on_key="attached",
            )
        ]
    },
    Capability.SAMSUNG_CE_STICK_CLEANER_STICK_STATUS: {
        Attribute.STATUS: [
            SmartThingsBinarySensorEntityDescription(
                key=Attribute.STATUS,
                is_on_key="charging",
                device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
                entity_category=EntityCategory.DIAGNOSTIC,
            )
        ]
    },
}

PROGRAMS_OPTIONS_TO_BINARY_SENSORS: dict[
    Capability, dict[Attribute, list[SmartThingsBinarySensorEntityDescription]]
] = {
    Capability.SAMSUNG_CE_WASHER_CYCLE: {
        Attribute.WASHER_CYCLE: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.BUBBLE_SOAK,
                translation_key="bubble_soak_support",
            )
        ]
    },
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: {
        Attribute.STEAM_CLOSET_CYCLE: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.KEEP_FRESH,
                translation_key="keep_fresh_support",
            )
        ],
        Attribute.SANITIZE: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.SANITIZE,
                translation_key="sanitize_support",
            )
        ],
    },
}

DISHWASHER_OPTIONS_TO_BINARY_SENSORS: dict[
    Capability, dict[Attribute, list[SmartThingsBinarySensorEntityDescription]]
] = {
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE: {
        Attribute.ADD_RINSE: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.ADD_RINSE,
                translation_key="add_rinse_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.DRY_PLUS: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.DRY_PLUS,
                translation_key="dry_plus_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.SPEED_BOOSTER: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.SPEED_BOOSTER,
                translation_key="speed_booster_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.HEATED_DRY: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.HEATED_DRY,
                translation_key="heated_dry_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.HIGH_TEMP_WASH: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.HIGH_TEMP_WASH,
                translation_key="high_temp_wash_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.HOT_AIR_DRY: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.HOT_AIR_DRY,
                translation_key="hot_air_dry_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.MULTI_TAB: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.MULTI_TAB,
                translation_key="multi_tab_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.RINSE_PLUS: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.RINSE_PLUS,
                translation_key="rinse_plus_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.SANITIZING_WASH: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.SANITIZING_WASH,
                translation_key="sanitizing_wash_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.STEAM_SOAK: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.STEAM_SOAK,
                translation_key="steam_soak_support",
                entity_registry_enabled_default=False,
            )
        ],
        Attribute.STORM_WASH: [
            SmartThingsBinarySensorEntityDescription(
                key=SupportedOption.STORM_WASH,
                translation_key="storm_wash_support",
                entity_registry_enabled_default=False,
            )
        ],
    }
}


def get_main_component_category(
    device: FullDevice,
) -> Category | str:
    """Get the main component of a device."""
    main = device.device.components[MAIN]
    return main.user_category or main.manufacturer_category


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartThingsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add binary sensors for a config entry."""
    entry_data = entry.runtime_data
    sensor_entities: list[SmartThingsBinarySensor] = []
    program_sensor_entities: list[SmartThingsProgramBinarySensor] = []

    for device in entry_data.devices.values():
        sensor_entities.extend(
            SmartThingsBinarySensor(
                entry_data.client,
                device,
                description,
                capability,
                attribute,
                component,
            )
            for capability, attributes in CAPABILITY_TO_SENSORS.items()
            for component, capabilities in device.status.items()
            if capability in capabilities
            for attribute, descriptions in attributes.items()
            if (attr_status := capabilities[capability].get(attribute)) is not None
            for description in descriptions
            if (
                component == MAIN
                or (
                    description.component_fn is not None
                    and description.component_fn(component)
                )
            )
            and (
                not description.category
                or get_main_component_category(device) in description.category
            )
            and (
                not description.supported_states_attributes
                or (
                    isinstance(
                        options := device.status[component][capability][
                            description.supported_states_attributes
                        ].value,
                        list,
                    )
                    and len(options) == 2
                )
            )
            and (not description.exists_fn or description.exists_fn(attr_status))
        )

        program_sensor_entities.extend(
            SmartThingsProgramBinarySensor(
                entry_data.client,
                device,
                description,
                capability,
                attribute,
                component,
            )
            for capability, attributes in PROGRAMS_OPTIONS_TO_BINARY_SENSORS.items()
            if device.programs is not None
            for component in device.status
            if capability in device.status[component]
            for attribute, descriptions in attributes.items()
            for description in descriptions
        )

        program_sensor_entities.extend(
            SmartThingsProgramBinarySensor(
                entry_data.client,
                device,
                description,
                capability,
                attribute,
                component,
            )
            for capability, attributes in DISHWASHER_OPTIONS_TO_BINARY_SENSORS.items()
            for component in device.status
            if capability in device.status[component]
            for supported_attr in [
                device.status[component][
                    Capability.SAMSUNG_CE_DISHWASHER_WASHING_OPTIONS
                ].get(Attribute.SUPPORTED_LIST)
            ]
            if supported_attr and supported_attr.value
            for attribute, descriptions in attributes.items()
            if attribute in cast(list[str], supported_attr.value)
            for description in descriptions
        )

    async_add_entities(sensor_entities + program_sensor_entities)
    oven_status_sensors = [
        ent
        for ent in sensor_entities
        if ent.capability == Capability.CUSTOM_OVEN_CAVITY_STATUS
    ]
    oven_status_entity_ids = [ent.entity_id for ent in oven_status_sensors]

    @callback
    def select_state_listener(event: Event[EventStateChangedData]) -> None:
        """Handle state changes of the sensor entity."""
        new_state = event.data["new_state"]
        old_state = event.data["old_state"]

        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return

        if old_state is not None and old_state.state == new_state.state:
            return

        source_entity_id = event.data["entity_id"]
        target_sensor = next(
            (ent for ent in oven_status_sensors if ent.entity_id == source_entity_id),
            None,
        )
        if target_sensor:
            device_id = target_sensor.device.device.device_id
            is_divided = new_state.state == "on"

            async_dispatcher_send(
                hass, f"smartthings_oven_state_changed_{device_id}", is_divided
            )

    if oven_status_entity_ids:
        entry.async_on_unload(
            async_track_state_change_event(
                hass, oven_status_entity_ids, select_state_listener
            )
        )


class SmartThingsBinarySensor(SmartThingsEntity, BinarySensorEntity):
    """Define a SmartThings Binary Sensor."""

    entity_description: SmartThingsBinarySensorEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsBinarySensorEntityDescription,
        capability: Capability,
        attribute: Attribute,
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        super().__init__(client, device, {capability}, component=component)
        self._attribute = attribute
        self.capability = capability
        self.entity_description = entity_description
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{entity_description.key}"
        if (
            entity_description.category_device_class
            and (category := get_main_component_category(device))
            in entity_description.category_device_class
        ):
            self._attr_device_class = entity_description.category_device_class[category]
            self._attr_name = None
        if self.entity_description.component_translation_key and component != MAIN:
            self._attr_translation_key = (
                self.entity_description.component_translation_key[component]
            )

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        value = self.get_attribute_value(self.capability, self._attribute)
        target = self.entity_description.is_on_key

        if value is None:
            return False

        if isinstance(target, str):
            return str(value).lower() == target.lower()

        return value == target


class SmartThingsProgramBinarySensor(SmartThingsEntity, BinarySensorEntity):
    """Define a SmartThings Program Binary Sensor."""

    entity_description: SmartThingsBinarySensorEntityDescription

    def __init__(
        self,
        client: SmartThings,
        device: FullDevice,
        entity_description: SmartThingsBinarySensorEntityDescription,
        capability: Capability,
        attribute: Attribute,
        component: str = MAIN,
    ) -> None:
        """Init the class."""
        super().__init__(client, device, {capability}, component=component)
        self._attribute = attribute
        self.capability = capability
        self.entity_description = entity_description
        self._attr_unique_id = f"{device.device.device_id}_{component}_{capability}_{attribute}_{attribute}"

    @property
    def is_on(self) -> bool:
        """Return true if the option is supported."""
        if (attribute_course := CAPABILITY_COURSES.get(self.capability)) is None:
            return False

        if (
            current_course_raw := self.get_attribute_value(
                self.capability, attribute_course
            )
        ) is None:
            return False

        current_course = translate_program_course(current_course_raw)
        if not self.device.programs or current_course not in self.device.programs:
            return False

        program = self.device.programs[current_course]
        if (
            opt := program.supportedoptions.get(self.entity_description.key)
        ) is not None:
            return len(opt.options) > 1

        return False
