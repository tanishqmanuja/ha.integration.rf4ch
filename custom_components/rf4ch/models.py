"""Models for Rf 4 Channel Integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from homeassistant.backports.enum import StrEnum
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo


class Channel(StrEnum):
    """Output channels for Switcher."""

    A = "Ch1"
    B = "Ch2"
    C = "Ch3"
    D = "Ch4"


class Action(StrEnum):
    """Actions for Switcher."""

    ON = "On"
    OFF = "Off"
    SYNC = "Sync"


CHANNEL_A = Channel.A.value
CHANNEL_B = Channel.B.value
CHANNEL_C = Channel.C.value
CHANNEL_D = Channel.D.value

ACTION_ON = Action.ON.value
ACTION_OFF = Action.OFF.value
ACTION_SYNC = Action.SYNC.value


@dataclass(frozen=True, order=True)
class SwitcherConfig:
    """Dataclass for switcher config"""

    name: str
    unique_id: str
    code_prefix: str
    service_id: str
    service_data: dict
    availability_template: str
    device_info: DeviceInfo


@dataclass(frozen=True, order=True)
class SwitcherOptions:
    """Dataclass for switcher options"""

    stateless: bool = False


class RfSwitcher(Protocol):
    """RfSwitcher Protocol Class"""

    available: bool

    @staticmethod
    def get_icon(icon: str) -> str:
        """Returns the icon for switches"""

    @property
    def hass(self) -> HomeAssistant:
        """Return the HA instance"""

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the switch."""

    @property
    def device_info(self) -> DeviceInfo:
        """Returns device info."""

    def get_channel_state(self, channel: Channel) -> bool:
        """Get internal state of channel."""

    def handle_action(self, action: Action):
        """Handle action."""

    def update_channel_state(self, channel: Channel, state: bool):
        """Update channel state internally."""

    def set_channel_state(self, channel: Channel, state: bool):
        """Set channel state."""

    def get_entities(self, platform: Platform) -> bool:
        """Return the entities for platform in switcher."""
