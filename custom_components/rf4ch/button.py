"""Button Platform for Rf 4 Channel Integration."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .models import ACTION_SYNC, Action, RfSwitcher

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    """Set up entry."""
    # Setup connection with switcher
    uid = config_entry.entry_id
    switcher: RfSwitcher = hass.data[DOMAIN][uid]

    _LOGGER.info("Setting up %s for rf4ch with uid: %s", Platform.BUTTON, uid)

    # Add switch enitities
    add_entities(switcher.get_entities(Platform.BUTTON))


class RfButton(ButtonEntity):
    """Rf Button Class"""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, switcher: RfSwitcher, action: Action) -> None:
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
