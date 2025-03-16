"""Constants used by the SmartThings component and platforms."""

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
