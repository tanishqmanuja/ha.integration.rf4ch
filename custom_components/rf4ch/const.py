"""Constants for Rf 4 Channel Integration."""

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
from homeassistant.helpers.trigger_template_entity import (  # noqa: F401 # pylint: disable=unused-import
    CONF_AVAILABILITY,
)

DOMAIN = "rf4ch"
PLATFORMS = [Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SWITCH]

CONF_OPTIONS = "options"
CONF_STATELESS = "stateless"

SERVICE_INTERNAL_STATE_ON = "internal_state_on"
SERVICE_INTERNAL_STATE_OFF = "internal_state_off"

MANUFACTURER = "TMLabs, Inc"
MODEL = "4 Channel Rf Switcher"
SW_VERSION = "1.0.0"
HW_VERSION = "1.0.0"
