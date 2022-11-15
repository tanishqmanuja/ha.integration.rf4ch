"""Switch Platform for Rf 4 Channel Integration."""

from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .models import Channel, RfSwitcher
from .services import async_setup_device_services

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    """Set up entry."""
    # Setup connection with switcher
    uid = config_entry.entry_id
    switcher: RfSwitcher = hass.data[DOMAIN][uid]

    _LOGGER.info("Setting up %s for rf4ch with uid: %s", Platform.SWITCH, uid)

    # Add switch enitities
    add_entities(switcher.get_entities(Platform.SWITCH))
    async_setup_device_services(hass)


class RfSwitch(SwitchEntity, RestoreEntity):
    """RfSwitch Class"""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, switcher: RfSwitcher, channel: Channel) -> None:

        self._channel = channel
        self._switcher = switcher
        self._name = channel.title()
        self._unique_id = f"{DOMAIN}_{switcher.unique_id}_{channel.lower()}"

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()
        if (
            last_state := await self.async_get_last_state()
        ) and last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            self._switcher.update_channel_state(
                self._channel, last_state.state == STATE_ON
            )

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the switch."""
        return self._unique_id

    @property
    def icon(self) -> str:
        """Return the icon of the switch."""
        return self._switcher.get_icon(self._channel)

    @property
    def available(self) -> str:
        """Return the availability of the switch."""
        return self._switcher.available

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._switcher.get_channel_state(self._channel)

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._switcher.set_channel_state(self._channel, True)

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._switcher.set_channel_state(self._channel, False)

    def override_on(self, **kwargs):
        """Override internal state On."""
        self._switcher.update_channel_state(self._channel, True)

    def override_off(self, **kwargs):
        """Override internal state Off."""
        self._switcher.update_channel_state(self._channel, False)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._switcher.device_info
