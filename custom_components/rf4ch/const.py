"""Constants for Rf 4 Channel Integration."""

from homeassistant.const import (  # noqa: F401 # pylint: disable=unused-import
    CONF_CODE,
    CONF_DEVICE_ID,
    CONF_FRIENDLY_NAME,
    CONF_NAME,
    CONF_SERVICE,
    CONF_UNIQUE_ID,
)
from homeassistant.helpers.template_entity import (  # noqa: F401 # pylint: disable=unused-import
    CONF_AVAILABILITY,
)

DOMAIN = "rf4ch"
PLATFORMS = ["binary_sensor", "button", "switch"]

CONF_SWITCHERS = "switchers"

SERVICE_INTERNAL_STATE_ON = "internal_state_on"
SERVICE_INTERNAL_STATE_OFF = "internal_state_off"

MANUFACTURER = "starkinc"
MODEL = "4 Channel Rf Switcher"
SW_VERSION = "1.0.0"
