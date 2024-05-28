"""Services for RF Four Channel integration."""

import logging

from homeassistant.components import persistent_notification
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import entity_platform

from .const import (
    DOMAIN,
    SERVICE_DUMMY_RF_SEND,
    SERVICE_INTERNAL_STATE_OFF,
    SERVICE_INTERNAL_STATE_ON,
)

_LOGGER = logging.getLogger(__name__)


@callback
def async_setup_dummy_rf_send_service(hass: HomeAssistant):
    """Set dummy Rf send service."""

    def _dummy_rf_send_service(call: ServiceCall) -> None:
        _LOGGER.info("Dummy Rf Send Service: %s", call.data)
        persistent_notification.create(
            hass,
            message=f"Data {call.data} sent via Dummy Rf Send.",
            title="RF Four Channel",
            notification_id="dummy_rf_send_service",
        )

    hass.services.async_register(DOMAIN, SERVICE_DUMMY_RF_SEND, _dummy_rf_send_service)


@callback
def async_setup_device_services(hass: HomeAssistant):
    """Create device specific services."""

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
