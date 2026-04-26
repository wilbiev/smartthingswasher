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

CAVITY_LOWER = "lower"
CAVITY_SINGLE = "single"
CAVITY_UPPER = "upper"
CAVITY_SECOND = "second"

CONF_APP_ID = "app_id"
CONF_CLOUDHOOK_URL = "cloudhook_url"
CONF_INSTALLED_APP_ID = "installed_app_id"
CONF_INSTANCE_ID = "instance_id"
CONF_LOCATION_ID = "location_id"
CONF_REFRESH_TOKEN = "refresh_token"

MAIN = "main"
CAVITY_01 = "cavity-01"
CAVITY_02 = "cavity-02"
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
PROGRAM_SUPPORTED_OPERATIONS = "supportedOperations"
PROGRAM_MODE = "mode"
PROGRAM_OPTION_MIN = "min"
PROGRAM_OPTION_MAX = "max"
PROGRAM_OPTION_STEP = "resolution"


CAPABILITIES_WITH_PROGRAMS: dict[Capability, Attribute] = {
    Capability.SAMSUNG_CE_DRYER_CYCLE: Attribute.DRYER_CYCLE,
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: Attribute.STEAM_CLOSET_CYCLE,
    Capability.SAMSUNG_CE_WASHER_CYCLE: Attribute.WASHER_CYCLE,
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE_DETAILS: Attribute.WASHING_COURSE,
    Capability.SAMSUNG_CE_KITCHEN_MODE_SPECIFICATION: Attribute.SPECIFICATION,
}

CAPABILITY_COURSES: dict[Capability, Attribute] = {
    Capability.SAMSUNG_CE_DRYER_CYCLE: Attribute.DRYER_CYCLE,
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: Attribute.STEAM_CLOSET_CYCLE,
    Capability.SAMSUNG_CE_WASHER_CYCLE: Attribute.WASHER_CYCLE,
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE: Attribute.WASHING_COURSE,
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE_DETAILS: Attribute.WASHING_COURSE,
}

CAPABILITY_COMMANDS: dict[Capability, Command] = {
    Capability.SAMSUNG_CE_DRYER_CYCLE: Command.SET_DRYER_CYCLE,
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: Command.SET_STEAM_CLOSET_CYCLE,
    Capability.SAMSUNG_CE_WASHER_CYCLE: Command.SET_WASHER_CYCLE,
    Capability.SAMSUNG_CE_DISHWASHER_WASHING_COURSE: Command.SET_WASHING_COURSE,
}

CAPABILITY_EXCEPTIONS: dict[Capability | str, str] = {
    Capability.CUSTOM_OVEN_CAVITY_STATUS: CAVITY_01,
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

DISHWASHER_COURSE_TO_HA = {
    "AI": "ai_wash",
    "auto": "auto",
    "babyBottle": "baby_bottle",
    "babycare": "babycare",
    "chef": "chef",
    "coldRinse": "cold_rinse",
    "daily": "daily",
    "daily_09": "daily_09",
    "delicate": "delicate",
    "drinkware": "drinkware",
    "dryOnly": "dry_only",
    "eco": "eco",
    "eco_08": "eco_08",
    "eco_10": "eco_10",
    "express": "express",
    "express_0C": "express_0c",
    "extraSilence": "extra_silence",
    "glasses": "glasses",
    "heavy": "heavy",
    "intensive": "intensive",
    "machineCare": "machine_care",
    "night": "night",
    "nightSilence": "night_silence",
    "normal": "normal",
    "plastics": "plastics",
    "potsAndPans": "pots_and_pans",
    "preBlast": "pre_blast",
    "preWash": "pre_wash",
    "quick": "quick",
    "quick_14": "quick_14",
    "rinseDry": "rinse_dry",
    "rinseOnly": "rinse_only",
    "selfClean": "self_clean",
    "selfSanitize": "self_sanitize",
    "steamSoak": "steam_soak",
    "upperExpress": "upper_express",
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
    "96": "course_96",
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
    "delayWashing": "delay_washing",
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

OVEN_MODE_TO_HA = {
    "AiDefrost": "ai_defrost",
    "AiReheat": "ai_reheat",
    "AiSousvide": "ai_sousvide",
    "AirFry": "air_fry",
    "AirFryer": "air_fryer",
    "AirFryMax": "air_fry_max",
    "AirSousvide": "air_sousvide",
    "Autocook": "autocook",
    "AutocookCustom": "autocook_custom",
    "Bake": "bake",
    "Bottom": "bottom",
    "BottomConvection": "bottom_convection",
    "BottomHeat": "bottom_heat",
    "BottomHeatPlusConvection": "bottom_heat_plus_convection",
    "BottomHeatPluseConvection": "bottom_heat_plus_econvection",
    "BreadProof": "bread_proof",
    "Broil": "broil",
    "BroilCombi": "broil_combi",
    "BroilConvection": "broil_convection",
    "BroilS": "broil_s",
    "Brownie": "brownie",
    "CatalyticClean": "catalytic_clean",
    "ChefBake": "chef_bake",
    "ChefBroil": "chef_broil",
    "ChefProof": "chef_proof",
    "CleanAirPyro": "clean_air_pyro",
    "Convection": "convection",
    "ConvectionBake": "convection_bake",
    "ConvectionBroil": "convection_broil",
    "ConvectionCombi": "convection_combi",
    "ConvectionRoast": "convection_roast",
    "ConvectionSear": "convection_sear",
    "ConvectionVegetable": "convection_vegetable",
    "Conventional": "conventional",
    "Cookie": "cookie",
    "Defrost": "defrost",
    "DefrostA": "defrost_a",
    "Defrosting": "defrosting",
    "Dehydrate": "dehydrate",
    "Deodorization": "deodorization",
    "Descale": "descale",
    "Drain": "drain",
    "Drying": "drying",
    "Easycook1": "easycook1",
    "Easycook2": "easycook2",
    "Easycook3": "easycook3",
    "EcoConvection": "eco_convection",
    "EcoGrill": "eco_grill",
    "FanConventional": "fan_conventional",
    "FanGrill": "fan_grill",
    "FavoriteCook": "favorite_cook",
    "FavoriteRecipes": "favorite_recipes",
    "Fermentation": "fermentation",
    "FineSteam": "fine_steam",
    "FourPartPureConvection": "four_part_pure_convection",
    "FourPartPureConvectionSingle": "four_part_pure_convection_single",
    "FrozenFood": "frozen_food",
    "FrozenMode": "frozen_mode",
    "GreenClean": "green_clean",
    "GreenCleanReal": "green_clean_real",
    "Grill": "grill",
    "GrillConvection": "grill_convection",
    "GuidedCook": "guided_cook",
    "HOMECARE_WIZARD_V2": "homecare_wizard_v2",
    "Healthycook1": "healthycook1",
    "Healthycook2": "healthycook2",
    "Healthycook3": "healthycook3",
    "Healthycook4": "healthycook4",
    "Healthycook5": "healthycook5",
    "Healthycook6": "healthycook6",
    "heating": "heating",
    "HotBlast": "hot_blast",
    "IntensiveCook": "intensive_cook",
    "InternalClean": "internal_clean",
    "KeepWarm": "keep_warm",
    "LargeGrill": "large_grill",
    "MW+HotBlast2": "mw+hotblast2",
    "MemoryCook": "memory_cook",
    "MicroWave": "micro_wave",
    "MicroWaveConvection": "micro_wave_convection",
    "MicroWaveFanGrill": "micro_wave_fan_grill",
    "MicroWaveGrill": "micro_wave_grill",
    "MicroWaveHotBlast": "micro_wave_hot_blast",
    "MicroWaveRoast": "micro_wave_roast",
    "MoistSteam": "moist_steam",
    "MultiGrill": "multi_grill",
    "MultiLevelCook": "multi_level_cook",
    "MWplusGrill": "microwave_plus_grill",
    "MWplusConvection": "microwave_plus_convection",
    "MWplusHotBlast": "microwave_plus_hot_blast",
    "MWplusHotBlast2": "microwave_plus_hot_blast_2",
    "NaturalSteam": "natural_steam",
    "NoOperation": "no_operation",
    "Others": "others",
    "Pizza": "pizza",
    "PizzaCook": "pizza_cook",
    "PizzaNaan": "pizza_naan",
    "PlateWarm": "plate_warm",
    "PowerBake": "power_bake",
    "PowerConvection": "power_convection",
    "PowerConvectionCombi": "power_convection_combi",
    "Preheat": "preheat",
    "ProConvection": "pro_convection",
    "ProRoasting": "pro_roasting",
    "Proof": "proof",
    "ProveDough": "prove_dough",
    "PureConvection": "pure_convection",
    "PureConvectionSear": "pure_convection_sear",
    "PureSteam": "pure_steam",
    "PyroFree": "pyro_free",
    "Rinse": "rinse",
    "Roast": "roast",
    "Roasting": "roasting",
    "Seafood": "seafood",
    "SelfClean": "self_clean",
    "SensorSelfDiagnosis": "sensor_self_diagnosis",
    "SlimfryMiddle": "slimfry_middle",
    "SlimfryStrong": "slimfry_strong",
    "SlimMiddle": "slim_middle",
    "SlimStrong": "slim_strong",
    "SlowCook": "slow_cook",
    "SlowCookBeef": "slow_cook_beef",
    "SlowCookPoultry": "slow_cook_poultry",
    "SlowCookStew": "slow_cook_stew",
    "SmallGrill": "small_grill",
    "SpareRib": "spare_rib",
    "SpeedBake": "speed_bake",
    "SpeedBroil": "speed_broil",
    "SpeedBrown": "speed_brown",
    "SpeedConvSear": "speed_conv_sear",
    "SpeedConvection": "speed_convection",
    "SpeedGrill": "speed_grill",
    "SpeedPowerConvection": "speed_power_convection",
    "SpeedRoast": "speed_roast",
    "SteamAssist": "steam_assist",
    "SteamAutocook": "steam_autocook",
    "SteamBake": "steam_bake",
    "SteamBottomConvection": "steam_bottom_convection",
    "SteamBottomHeatplusConvection": "steam_bottom_heat_plus_convection",
    "SteamBreadProof": "steam_bread_proof",
    "SteamClean": "steam_clean",
    "SteamCleanReal": "steam_clean_real",
    "SteamConvection": "steam_convection",
    "SteamCook": "steam_cook",
    "SteamProof": "steam_proof",
    "SteamReheat": "steam_reheat",
    "SteamRoast": "steam_roast",
    "SteamTopConvection": "steam_top_convection",
    "StoneMode": "stone_mode",
    "StrongSteam": "strong_steam",
    "ThreePartPureConvection": "three_part_pure_convection",
    "ToastBagle": "toast_bagle",
    "ToastCroissant": "toast_croissant",
    "ToastSlicedBread": "toast_sliced_bread",
    "TopConvection": "top_convection",
    "TopHeatPluseConvection": "top_heat_plus_econvection",
    "Turkey": "turkey",
    "VaporBottomHeatPluseConvection": "vapor_bottom_heat_pluse_convection",
    "VaporCleaning": "vapor_cleaning",
    "VaporConvection": "vapor_convection",
    "VaporGRILL": "vapor_grill",
    "VaporMWO": "vapor_mwo",
    "VaporTopHeatPluseConvection": "vapor_top_heat_pluse_convection",
    "WarmHold": "warm_hold",
    "warming": "warming",
}

HEALTH_CONCERN = {
    "good": "good",
    "moderate": "moderate",
    "slightlyUnhealthy": "slightly_unhealthy",
    "unhealthy": "unhealthy",
    "veryUnhealthy": "very_unhealthy",
    "hazardous": "hazardous",
}
