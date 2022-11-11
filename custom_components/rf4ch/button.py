"""Button Platform for Rf 4 Channel Integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .models import ACTION_SYNC, RfSwitcher

SCAN_INTERVAL = timedelta(seconds=10)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=5)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    """Set up entry."""
    # Setup connection with switcher
    sid = config_entry.data[CONF_NAME]
    switcher: RfSwitcher = hass.data[DOMAIN][sid]

    # Add button enitites
    add_entities(switcher.buttons)


class RfButton(ButtonEntity):
    """Rf Button Class"""

    _attr_has_entity_name = True
    _attr_should_poll: bool = False

    def __init__(self, switcher, action) -> None:
        self._action = action
        self._switcher: RfSwitcher = switcher
        self._name = action.title()
        self._unique_id = f"{DOMAIN}_{switcher.unique_id}_{action.lower()}"

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the switch."""
        return self._unique_id

    @property
    def icon(self) -> str:
        """Return the icon of the switch."""
        return self._switcher.get_icon(self._action)

    @property
    def available(self) -> str:
        """Return the availability of the switch."""
        if self._action == ACTION_SYNC:
            return True

        return self._switcher.available

    def press(self) -> None:
        """Press the button."""
        self._switcher.handle_action(self._action)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._switcher.device_info
