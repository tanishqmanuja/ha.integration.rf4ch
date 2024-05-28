"""Data Models for RF Four Channel Integration."""

from typing import Protocol

from homeassistant.helpers.entity import Entity

from .lib.switcher import SwitcherAction, SwitcherChannel


class RfSwitcher(Protocol):
    """Protocol for RF Switcher."""

    @property
    def name(self) -> str:
        """Return unique ID."""

    @property
    def unique_id(self) -> str:
        """Return unique ID."""

    @property
    def device_info(self) -> dict[str, str]:
        """Return device info."""

    @property
    def available(self) -> bool:
        """Return availability."""

    def get_entities_for_platform(self, platform: str) -> list[Entity]:
        """Get entities for platform."""

    def get_channel(self, channel: SwitcherChannel) -> bool:
        """Get channel state."""

    def set_channel(
        self, channel: SwitcherChannel, state: bool, only_internal: bool = False
    ):
        """Set channel state."""

    def turn_on_all(self):
        """Turn on all channels."""

    def turn_off_all(self):
        """Turn off all channels."""

    def sync_channels(self):
        """Sync channels."""

    def handle_action(self, action: SwitcherAction):
        """Handle action."""
