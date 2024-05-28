"""Switch platform for RF Four Channel integration."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .lib.switcher import SwitcherChannel
from .models import RfSwitcher
from .services import async_setup_device_services


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> bool:
    """Set up RF Four Channel Switch from a config entry."""
    switcher: RfSwitcher = hass.data[DOMAIN].get(entry.entry_id)
    entites = switcher.get_entities_for_platform(Platform.SWITCH)

    async_add_entities(entites)
    async_setup_device_services(hass)

    return True


class RfSwitch(SwitchEntity, RestoreEntity):
    """Entity class for RF Four Channel switch."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, switcher: RfSwitcher, channel: SwitcherChannel) -> None:
        """Initialize switch."""
        self._switcher = switcher
        self._channel = channel
        self._attr_name = f"Ch {chr(ord('A') + channel)}"
        self._attr_unique_id = f"{DOMAIN}_{switcher.unique_id}_{channel}"
        self._attr_device_info = switcher.device_info
        self._attr_is_on = switcher.get_channel(channel)
        self._attr_available = switcher.available
        self._attr_icon = f"mdi:numeric-{channel+1}-box"

    @property
    def name(self) -> str:
        """Return name."""
        return self._attr_name

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return self._attr_unique_id

    @property
    def available(self) -> str:
        """Return the availability of the switch."""
        return self._switcher.available

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self._switcher.get_channel(self._channel)

    def turn_on(self, **kwargs) -> None:
        """Turn on switch."""
        self._switcher.set_channel(self._channel, True)

    def turn_off(self, **kwargs) -> None:
        """Turn off switch."""
        self._switcher.set_channel(self._channel, False)

    def override_on(self, **kwargs):
        """Override internal state On."""
        self._switcher.set_channel(self._channel, True, only_internal=True)

    def override_off(self, **kwargs):
        """Override internal state Off."""
        self._switcher.set_channel(self._channel, False, only_internal=True)

    async def async_added_to_hass(self) -> None:
        """Restore state."""
        await super().async_added_to_hass()

        if (last_state := await self.async_get_last_state()) and last_state not in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            self._switcher.set_channel(
                self._channel, last_state.state == STATE_ON, only_internal=True
            )
