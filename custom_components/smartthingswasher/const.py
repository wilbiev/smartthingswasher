"""Constants used by the SmartThings component and platforms."""

from pysmartthings import Attribute, Capability, Command

from .models import SupportedOption

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

PROGRAM_CYCLE = "cycle"
PROGRAM_CYCLE_TYPE = "cycleType"
PROGRAM_OPTION_RAW = "raw"
PROGRAM_OPTION_DEFAULT = "default"
PROGRAM_OPTION_OPTIONS = "options"
PROGRAM_SUPPORTED_OPTIONS = "supportedOptions"


SUPPORTEDOPTIONS_LIST = (
    SupportedOption.BUBBLE_SOAK,
    SupportedOption.DRYING_LEVEL,
    SupportedOption.DRYING_TEMPERATURE,
    SupportedOption.KEEP_FRESH,
    SupportedOption.RINSE_CYCLE,
    SupportedOption.SANITIZE,
    SupportedOption.SOIL_LEVEL,
    SupportedOption.SPIN_LEVEL,
    SupportedOption.WATER_TEMPERATURE,
)


CAPABILITIES_WITH_PROGRAMS: dict[str, str] = {
    Capability.SAMSUNG_CE_DRYER_CYCLE: Attribute.DRYER_CYCLE,
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: Attribute.STEAM_CLOSET_CYCLE,
    Capability.SAMSUNG_CE_WASHER_CYCLE: Attribute.WASHER_CYCLE,
}


CAPABILITY_COMMANDS: dict[str, str] = {
    Capability.SAMSUNG_CE_DRYER_CYCLE: Command.SET_DRYER_CYCLE,
    Capability.SAMSUNG_CE_STEAM_CLOSET_CYCLE: Command.SET_STEAM_CLOSET_CYCLE,
    Capability.SAMSUNG_CE_WASHER_CYCLE: Command.SET_WASHER_CYCLE,
}
