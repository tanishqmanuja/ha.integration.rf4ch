"""Switcher class for Rf 4 Channel Integration."""


import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import ConfigType

from .binary_sensor import RfAvailabilityBinarySensor
from .button import RfButton
from .const import (
    CONF_AVAILABILITY,
    CONF_CODE,
    CONF_DEVICE_ID,
    CONF_FRIENDLY_NAME,
    CONF_NAME,
    CONF_SERVICE,
    CONF_UNIQUE_ID,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    PLATFORMS,
    SW_VERSION,
)
from .models import (
    ACTION_OFF,
    ACTION_ON,
    ACTION_SYNC,
    CHANNEL_A,
    CHANNEL_B,
    CHANNEL_C,
    CHANNEL_D,
    Action,
    Channel,
)
from .switch import RfSwitch

RF_REPEAT = 6

ICONS = {
    CHANNEL_A: "mdi:toggle-switch-variant",
    CHANNEL_B: "mdi:toggle-switch-variant",
    CHANNEL_C: "mdi:toggle-switch-variant",
    CHANNEL_D: "mdi:toggle-switch-variant",
    ACTION_ON: "mdi:power-on",
    ACTION_OFF: "mdi:power-off",
    ACTION_SYNC: "mdi:sync",
    CONF_AVAILABILITY: "mdi:connection",
}

_LOGGER = logging.getLogger(__name__)


class RfSwitcher:
    """RfSwitcher Class"""

    def __init__(
        self, hass: HomeAssistant, config: ConfigType, entry: ConfigEntry
    ) -> None:
        self._config = config
        self._config_entry = entry
        self._hass = hass
        self._service = config[CONF_SERVICE]
        self._repeat = RF_REPEAT
        self._code_prefix = config[CONF_CODE]
        self._channels = [c.value for c in Channel]
        self._actions = [a.value for a in Action]
        self._codes = {
            CHANNEL_A: f"{self._code_prefix}0010",
            CHANNEL_B: f"{self._code_prefix}1000",
            CHANNEL_C: f"{self._code_prefix}0001",
            CHANNEL_D: f"{self._code_prefix}0100",
            ACTION_ON: f"{self._code_prefix}1100",
            ACTION_OFF: f"{self._code_prefix}0011",
        }
        self._states = {c: False for c in self._channels}
        self._available = True
        self._name = config[CONF_NAME]
        self._friendly_name = config[CONF_FRIENDLY_NAME]
        self._unique_id = config[CONF_UNIQUE_ID]
        self._device_id = config[CONF_DEVICE_ID]

        self._availability_template = config.get(CONF_AVAILABILITY)
        self._manufacturer = MANUFACTURER
        self._model = MODEL
        self._sw_version = SW_VERSION

        self.switches = [RfSwitch(self, channel) for channel in self._channels]
        self.buttons = [RfButton(self, action) for action in self._actions]
        self.binary_sensors = []

        if self._availability_template:
            self.binary_sensors.append(
                RfAvailabilityBinarySensor(self, CONF_AVAILABILITY)
            )

    async def async_setup(self, tries=0):
        "Setup Switcher Platforms"

        hass = self._hass

        hass.async_create_task(
            hass.config_entries.async_forward_entry_setups(
                self._config_entry, PLATFORMS
            )
        )

        return True

    @staticmethod
    def get_icon(channel_or_action):
        """Returns the icon for switches"""
        return ICONS.get(channel_or_action)

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the switch."""
        return self._unique_id

    @property
    def availability_template(self):
        """Returns availability template."""
        return self._availability_template

    @property
    def available(self) -> bool:
        """Return the availabilty of switcher."""
        return self._available

    @available.setter
    def available(self, state: bool) -> None:
        if self._available == state:
            return

        self._available = state
        for switch in self.switches:
            switch.schedule_update_ha_state()
        for button in self.buttons:
            button.schedule_update_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Returns device info."""

        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._device_id)
            },
            name=f"{self._friendly_name} Switcher",
            manufacturer=self._manufacturer,
            model=self._model,
            sw_version=self._sw_version,
        )

    def get_hass(self) -> HomeAssistant:
        """Returns hass instance."""
        return self._hass

    def send_rf(self, code):
        """Call service to send rf code."""
        serv = self._service.split(".")
        self._hass.services.call(
            serv[0], serv[1], {"code": self._codes[code], "repeat": self._repeat}
        )

    def update_channel_state(self, channel, state: bool):
        """Update channel state internally."""
        self._states[channel] = state
        switch = self.switches[self._channels.index(channel)]
        switch.schedule_update_ha_state()

    def set_channel_state(self, channel, state: bool):
        """Set channel state."""
        if self._states[channel] != state:
            self.update_channel_state(channel, state)
            self.send_rf(channel)

    def handle_action(self, action):
        """Handle action."""
        if action == ACTION_SYNC:
            self.sync()
        elif action in (ACTION_ON, ACTION_OFF):
            state = action == ACTION_ON
            for channel in self._channels:
                self._states[channel] = state
            for switch in self.switches:
                switch.schedule_update_ha_state()
            self.send_rf(action)

    def get_channel_state(self, channel):
        """Get internal state of channel."""
        return self._states[channel]

    def sync(self):
        """Reset and sync channel states."""
        self.send_rf("OFF")
        for channel, state in self._states.items():
            if channel in self._channels and state is True:
                self.send_rf(channel)
