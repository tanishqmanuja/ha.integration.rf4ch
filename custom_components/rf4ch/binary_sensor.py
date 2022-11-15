"""Binary Sensor Platform for Rf 4 Channel Integration."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .models import RfSwitcher

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    """Set up entry."""
    # Setup connection with switcher
    uid = config_entry.entry_id
    switcher: RfSwitcher = hass.data[DOMAIN][uid]

    _LOGGER.info("Setting up %s for rf4ch with uid: %s", Platform.BINARY_SENSOR, uid)

    # Add switch enitities
    add_entities(switcher.get_entities(Platform.BINARY_SENSOR))


class RfAvailabilityBinarySensor(BinarySensorEntity):
    """Rf Binary Sensor Class"""

    _attr_has_entity_name = True
    _attr_available = True
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_should_poll = False

    def __init__(self, switcher, name) -> None:
        self._switcher: RfSwitcher = switcher
        self._name = name
        self._unique_id = f"{DOMAIN}_{switcher.unique_id}_{name.lower()}"

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name.title()

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the switch."""
        return self._unique_id

    @property
    def icon(self) -> str:
        """Return the icon of the switch."""
        return self._switcher.get_icon(self._name)

    @property
    def is_on(self):
        """Return if the device is on."""
        return self._switcher.available

    @property
    def available(self):
        """Return if the device is online."""
        return True

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._switcher.device_info
