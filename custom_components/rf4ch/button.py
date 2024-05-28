"""Button platform for RF Four Channel integration."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .lib.switcher import SwitcherAction
from .models import RfSwitcher

ICON_MAP = {
    SwitcherAction.ON: "mdi:power-on",
    SwitcherAction.OFF: "mdi:power-off",
    SwitcherAction.SYNC: "mdi:sync",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> bool:
    """Set up RF Four Channel Switch from a config entry."""
    switcher: RfSwitcher = hass.data[DOMAIN].get(entry.entry_id)
    entites = switcher.get_entities_for_platform(Platform.BUTTON)

    async_add_entities(entites)

    return True


class RfButton(ButtonEntity):
    """Entity class for RF Four Channel button."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, switcher: RfSwitcher, action: SwitcherAction) -> None:
        """Initialize button."""
        self._switcher = switcher
        self._action = action
        self._attr_name = f"{action.name}"
        self._attr_unique_id = f"{DOMAIN}_{switcher.unique_id}_{action}"
        self._attr_device_info = switcher.device_info
        self._attr_available = switcher.available
        self._attr_icon = ICON_MAP[action]

    @property
    def name(self) -> str:
        """Return name."""
        return self._attr_name

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return self._attr_unique_id

    @property
    def available(self) -> bool:
        """Return the availability of the button."""
        return self._switcher.available

    def press(self) -> None:
        """Press the button."""
        self._switcher.handle_action(self._action)
