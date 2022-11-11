"""Models for Rf 4 Channel Integration."""

from __future__ import annotations

from enum import Enum
from typing import Protocol

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.template import Template


class Channel(Enum):
    """Output channels for Switcher."""

    A = "CH1"
    B = "CH2"
    C = "CH3"
    D = "CH4"


class Action(Enum):
    """Actions for Switcher."""

    ON = "ON"
    OFF = "OFF"
    SYNC = "SYNC"


CHANNEL_A = Channel.A.value
CHANNEL_B = Channel.B.value
CHANNEL_C = Channel.C.value
CHANNEL_D = Channel.D.value

ACTION_ON = Action.ON.value
ACTION_OFF = Action.OFF.value
ACTION_SYNC = Action.SYNC.value


class RfSwitcher(Protocol):
    """RfSwitcher Class"""

    switches: list
    buttons: list
    binary_sensors: list
    available: bool

    @staticmethod
    def get_icon(icon: str) -> str:
        """Returns the icon for switches"""

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the switch."""

    @property
    def availability_template(self) -> Template | None:
        """Returns availability template."""

    @property
    def device_info(self) -> DeviceInfo:
        """Returns device info."""

    def get_hass(self) -> HomeAssistant:
        """Returns hass instance."""

    def get_channel_state(self, channel: str) -> bool:
        """Get internal state of channel."""

    def handle_action(self, action: str):
        """Handle action."""

    def update_channel_state(self, channel: str, state: bool):
        """Update channel state internally."""

    def set_channel_state(self, channel, state: bool):
        """Set channel state."""
