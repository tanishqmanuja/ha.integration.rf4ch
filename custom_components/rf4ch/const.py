"""Constants for RF Four Channel integration."""

from homeassistant.const import (  # noqa: F401 # pylint: disable=unused-import
    CONF_CODE,
    CONF_DEVICE_ID,
    CONF_FRIENDLY_NAME,
    CONF_ID,
    CONF_NAME,
    CONF_SERVICE,
    CONF_SERVICE_DATA,
    CONF_UNIQUE_ID,
    Platform,
)

DOMAIN = "rf4ch"
PLATFORMS = [Platform.BUTTON, Platform.SWITCH]

CONF_AVAILABILITY_TEMPLATE = "availability_template"
CONF_STATELESS = "stateless"
CONF_OPTIONS = "options"

CONF_CODE_A = "channel_a"
CONF_CODE_B = "channel_b"
CONF_CODE_C = "channel_c"
CONF_CODE_D = "channel_d"
CONF_CODE_ON = "channel_on"
CONF_CODE_OFF = "channel_off"
CONF_CODE_PREFIX = "prefix"

SERVICE_DUMMY_RF_SEND = "dummy_rf_send"
SERVICE_INTERNAL_STATE_ON = "internal_state_on"
SERVICE_INTERNAL_STATE_OFF = "internal_state_off"

MANUFACTURER = "TMLabs, Inc"
MODEL = "Four Channel Rf Switcher"
SW_VERSION = "1.0.0"
HW_VERSION = "1.0.0"
