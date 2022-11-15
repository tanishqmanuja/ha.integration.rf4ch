"""Services for Rf 4 Channel Integration."""

from homeassistant.core import callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.typing import HomeAssistantType

from .const import SERVICE_INTERNAL_STATE_OFF, SERVICE_INTERNAL_STATE_ON


@callback
def async_setup_device_services(hass: HomeAssistantType):
    """Create device-specific services for the rf4ch Integration."""

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_INTERNAL_STATE_ON,
        {},
        "override_on",
    )
    platform.async_register_entity_service(
        SERVICE_INTERNAL_STATE_OFF,
        {},
        "override_off",
    )
