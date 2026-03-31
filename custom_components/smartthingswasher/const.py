"""Constants used by the SmartThings component and platforms."""

from pysmartthings import Attribute, Capability, Command

from homeassistant.const import UnitOfTemperature

DOMAIN = "smartthings"

SCOPES = [
    "r:devices:*",
    "w:devices:*",
    "x:devices:*",
    "r:hubs:*",
    "r:locations:*",
    "w:locations:*",
    "x:locations:*",
    "r:scenes:*",
    "x:scenes:*",
    "r:rules:*",
    "w:rules:*",
    "sse",
]

REQUESTED_SCOPES = [
    *SCOPES,
    "r:installedapps",
    "w:installedapps",
]

CONF_APP_ID = "app_id"
CONF_CLOUDHOOK_URL = "cloudhook_url"
CONF_INSTALLED_APP_ID = "installed_app_id"
CONF_INSTANCE_ID = "instance_id"
CONF_LOCATION_ID = "location_id"
CONF_REFRESH_TOKEN = "refresh_token"

MAIN = "main"
OLD_DATA = "old_data"

CONF_SUBSCRIPTION_ID = "subscription_id"
EVENT_BUTTON = "smartthings.button"

PROGRAM_COURSE_NAME = "courseName"
PROGRAM_CYCLE = "cycle"
PROGRAM_CYCLE_TYPE = "cycleType"
PROGRAM_OPTION_RAW = "raw"
PROGRAM_OPTION_DEFAULT = "default"
PROGRAM_OPTION_OPTIONS = "options"
PROGRAM_OPTION_SETTABLE = "settable"
PROGRAM_SUPPORTED_OPTIONS = "supportedOptions"

CAPABILITIES_WITH_PROGRAMS: dict[Capability, Attribute] = {
    Capability.SAMSUNG_CE_DRYER_CYCLE: Attribute.DRYER_CYCLE,
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: Attribute.STEAM_CLOSET_CYCLE,
    Capability.SAMSUNG_CE_WASHER_CYCLE: Attribute.WASHER_CYCLE,
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE_DETAILS: Attribute.WASHING_COURSE,
}

CAPABILITY_COURSES: dict[Capability, Attribute] = {
    Capability.SAMSUNG_CE_DRYER_CYCLE: Attribute.DRYER_CYCLE,
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: Attribute.STEAM_CLOSET_CYCLE,
    Capability.SAMSUNG_CE_WASHER_CYCLE: Attribute.WASHER_CYCLE,
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE: Attribute.WASHING_COURSE,
}

CAPABILITY_COMMANDS: dict[Capability, Command] = {
    Capability.SAMSUNG_CE_DRYER_CYCLE: Command.SET_DRYER_CYCLE,
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: Command.SET_STEAM_CLOSET_CYCLE,
    Capability.SAMSUNG_CE_WASHER_CYCLE: Command.SET_WASHER_CYCLE,
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE: Command.SET_WASHING_COURSE,
}

UNIT_MAP = {"C": UnitOfTemperature.CELSIUS, "F": UnitOfTemperature.FAHRENHEIT}

LAMP_TO_HA = {
    "extraHigh": "extra_high",
    "high": "high",
    "mid": "mid",
    "low": "low",
    "on": "on",
    "off": "off",
}

SOUND_MODE_TO_HA = {
    "voice": "voice",
    "beep": "tone",
    "mute": "mute",
}

DRIVING_MODE_TO_HA = {
    "areaThenWalls": "area_then_walls",
    "wallFirst": "walls_first",
    "quickCleaningZigzagPattern": "quick_clean_zigzag_pattern",
}

CLEANING_TYPE_TO_HA = {
    "vacuum": "vacuum",
    "mop": "mop",
    "vacuumAndMopTogether": "vacuum_and_mop_together",
    "mopAfterVacuum": "mop_after_vacuum",
}

DISPENSE_DENSITY_TO_HA = {
    "normal": "normal",
    "high": "high",
    "extraHigh": "extra_high",
}

WASHER_SOIL_LEVEL_TO_HA = {
    "none": "none",
    "heavy": "heavy",
    "normal": "normal",
    "light": "light",
    "extraLight": "extra_light",
    "extraHeavy": "extra_heavy",
    "up": "up",
    "down": "down",
}

WATER_SPRAY_LEVEL_TO_HA = {
    "high": "high",
    "mediumHigh": "moderate_high",
    "medium": "medium",
    "mediumLow": "moderate_low",
    "low": "low",
}

WASHER_SPIN_LEVEL_TO_HA = {
    "none": "none",
    "rinseHold": "rinse_hold",
    "noSpin": "no_spin",
    "low": "low",
    "extraLow": "extra_low",
    "delicate": "delicate",
    "medium": "medium",
    "high": "high",
    "extraHigh": "extra_high",
    "200": "200",
    "400": "400",
    "600": "600",
    "800": "800",
    "1000": "1000",
    "1200": "1200",
    "1400": "1400",
    "1600": "1600",
}

WASHER_WATER_TEMPERATURE_TO_HA = {
    "none": "none",
    "20": "20",
    "30": "30",
    "40": "40",
    "50": "50",
    "60": "60",
    "65": "65",
    "70": "70",
    "75": "75",
    "80": "80",
    "90": "90",
    "95": "95",
    "tapCold": "tap_cold",
    "cold": "cold",
    "cool": "cool",
    "ecoWarm": "eco_warm",
    "warm": "warm",
    "semiHot": "semi_hot",
    "hot": "hot",
    "extraHot": "extra_hot",
    "extraLow": "extra_low",
    "low": "low",
    "mediumLow": "medium_low",
    "medium": "medium",
    "high": "high",
}

WASHING_COURSE_TO_HA = {
    "auto": "auto",
    "normal": "normal",
    "heavy": "heavy",
    "delicate": "delicate",
    "express": "express",
    "rinseOnly": "rinse_only",
    "selfClean": "self_clean"
}

DISHWASHER_COURSE_TO_HA = {
    "auto": "auto",
    "eco": "eco",
    "intensive": "intensive",
    "delicate": "delicate",
    "express_0C": "express_0c",
    "preWash": "pre_wash",
    "extraSilence": "extra_silence",
    "machineCare": "machine_care",
    "plastics": "plastics",
    "potsAndPans": "pots_and_pans",
    "babycare": "babycare",
    "drinkware": "drinkware"
}

COURSE_TO_HA = {
    "1B": "course_1b",
    "1C": "course_1c",
    "1D": "course_1d",
    "1E": "course_1e",
    "1F": "course_1f",
    "20": "course_20",
    "21": "course_21",
    "22": "course_22",
    "23": "course_23",
    "24": "course_24",
    "25": "course_25",
    "26": "course_26",
    "27": "course_27",
    "28": "course_28",
    "29": "course_29",
    "2A": "course_2a",
    "2B": "course_2b",
    "2D": "course_2d",
    "2E": "course_2e",
    "2F": "course_2f",
    "30": "course_30",
    "32": "course_32",
    "33": "course_33",
    "34": "course_34",
    "35": "course_35",
    "36": "course_36",
    "37": "course_37",
    "38": "course_38",
    "39": "course_39",
    "3A": "course_3a",
    "66": "course_66",
    "8F": "course_8f",
    "96": "course_96"
}

COOKTOP_HEATING_MODES = {
    "off": "off",
    "manual": "manual",
    "boost": "boost",
    "keepWarm": "keep_warm",
    "quickPreheat": "quick_preheat",
    "defrost": "defrost",
    "melt": "melt",
    "simmer": "simmer",
}

JOB_STATE_MAP = {
    "airWash": "air_wash",
    "airwash": "air_wash",
    "aIRinse": "ai_rinse",
    "aISpin": "ai_spin",
    "aIWash": "ai_wash",
    "aIDrying": "ai_drying",
    "internalCare": "internal_care",
    "continuousDehumidifying": "continuous_dehumidifying",
    "thawingFrozenInside": "thawing_frozen_inside",
    "delayWash": "delay_wash",
    "weightSensing": "weight_sensing",
    "freezeProtection": "freeze_protection",
    "preDrain": "pre_drain",
    "preWash": "pre_wash",
    "prewash": "pre_wash",
    "wrinklePrevent": "wrinkle_prevent",
    "rinseOnly": "rinse_only",
    "rinsing": "rinse",
    "washing": "wash",
    "drying": "dry",
    "selfClean": "self_clean",
    "none": "none",
    "unknown": None,
}

OVEN_JOB_STATE_MAP = {
    "scheduledStart": "scheduled_start",
    "fastPreheat": "fast_preheat",
    "scheduledEnd": "scheduled_end",
    "stone_heating": "stone_heating",
    "timeHoldPreheat": "time_hold_preheat",
}

MEDIA_PLAYBACK_STATE_MAP = {
    "fast forwarding": "fast_forwarding",
}

ROBOT_CLEANER_TURBO_MODE_STATE_MAP = {
    "extraSilence": "extra_silence",
}

ROBOT_CLEANER_MOVEMENT_MAP = {
    "powerOff": "off",
}

OVEN_MODE = {
    "Conventional": "conventional",
    "Bake": "bake",
    "BottomHeat": "bottom_heat",
    "ConvectionBake": "convection_bake",
    "ConvectionRoast": "convection_roast",
    "Broil": "broil",
    "ConvectionBroil": "convection_broil",
    "SteamCook": "steam_cook",
    "SteamBake": "steam_bake",
    "SteamRoast": "steam_roast",
    "SteamBottomHeatplusConvection": "steam_bottom_heat_plus_convection",
    "Microwave": "microwave",
    "MWplusGrill": "microwave_plus_grill",
    "MWplusConvection": "microwave_plus_convection",
    "MWplusHotBlast": "microwave_plus_hot_blast",
    "MWplusHotBlast2": "microwave_plus_hot_blast_2",
    "SlimMiddle": "slim_middle",
    "SlimStrong": "slim_strong",
    "SlowCook": "slow_cook",
    "Proof": "proof",
    "Dehydrate": "dehydrate",
    "Others": "others",
    "StrongSteam": "strong_steam",
    "Descale": "descale",
    "Rinse": "rinse",
    "heating": "heating",
    "grill": "grill",
    "defrosting": "defrosting",
    "warming": "warming"
}

HEALTH_CONCERN = {
    "good": "good",
    "moderate": "moderate",
    "slightlyUnhealthy": "slightly_unhealthy",
    "unhealthy": "unhealthy",
    "veryUnhealthy": "very_unhealthy",
    "hazardous": "hazardous",
}
