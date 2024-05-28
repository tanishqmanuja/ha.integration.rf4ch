"""Internal implementation for RF Four Channel Switcher."""

from collections.abc import Callable
from dataclasses import InitVar, dataclass
from enum import IntEnum, StrEnum
from typing import NotRequired, TypedDict

INITIAL_SWITCHER_STATE = 0b0000


class SwitcherChannel(IntEnum):
    """Enum for switcher channels."""

    A = 0
    B = 1
    C = 2
    D = 3


class SwitcherAction(StrEnum):
    """Enum for switcher actions."""

    ON = "on"
    OFF = "off"
    SYNC = "sync"


class SwitcherState:
    """Class for switcher state."""

    def __init__(self, initial_state: int = INITIAL_SWITCHER_STATE) -> None:
        """Initialize switcher state."""
        self.__state = initial_state

    def set_channel(self, channel: SwitcherChannel, state: bool):
        """Set channel state."""
        self.__state = (self.__state & ~(1 << channel)) | (state << channel)

    def get_channel(self, channel: SwitcherChannel):
        """Get channel state."""
        return (self.__state & (1 << channel)) != 0

    def turn_on_all(self):
        """Turn on all channels."""
        self.__state = 0b1111

    def turn_off_all(self):
        """Turn off all channels."""
        self.__state = 0b0000

    def is_all_off(self):
        """Check if all channels are off."""
        return self.__state == 0b0000

    def is_all_on(self):
        """Check if all channels are on."""
        return self.__state == 0b1111

    def __str__(self):
        """Return string representation of instance for debugging."""
        return f"SwitcherState(state=0b{self.__state:04b})"


class SwitcherCodeDict(TypedDict):
    """Switcher code dictionary."""

    channel_a: str
    channel_b: str
    channel_c: str
    channel_d: str
    channel_off: str
    channel_on: str
    prefix: NotRequired[str]


@dataclass(frozen=True)
class SwitcherCode:
    """Class for switcher code."""

    channel_a: str
    channel_b: str
    channel_c: str
    channel_d: str
    channel_off: str
    channel_on: str
    prefix: InitVar[str | None] = None

    def get_code_for_channel(self, channel: SwitcherChannel):
        """Get code for channel."""
        if channel == SwitcherChannel.A:
            return self.channel_a
        if channel == SwitcherChannel.B:
            return self.channel_b
        if channel == SwitcherChannel.C:
            return self.channel_c
        if channel == SwitcherChannel.D:
            return self.channel_d

    def __post_init__(self, prefix):
        """Post init."""
        if prefix is not None:
            object.__setattr__(self, "channel_a", prefix + self.channel_a)
            object.__setattr__(self, "channel_b", prefix + self.channel_b)
            object.__setattr__(self, "channel_c", prefix + self.channel_c)
            object.__setattr__(self, "channel_d", prefix + self.channel_d)
            object.__setattr__(self, "channel_off", prefix + self.channel_off)
            object.__setattr__(self, "channel_on", prefix + self.channel_on)

    @staticmethod
    def from_dict(d: SwitcherCodeDict):
        """Create instance from dictionary."""
        return SwitcherCode(**d)


class Switcher:
    """Class for RF Four Channel Switcher."""

    def __init__(
        self,
        code: SwitcherCodeDict,
        send_rf_callback: Callable[[str], None],
        initial_state: int = INITIAL_SWITCHER_STATE,
    ) -> None:
        """Initialize switcher."""
        self.__c = SwitcherCode.from_dict(code)
        self.__s = SwitcherState(initial_state)
        self.__send_rf_callback = send_rf_callback

    def __send_rf_code(self, code: str):
        if self.__send_rf_callback is not None:
            self.__send_rf_callback(code)

    def get_channel(self, channel: SwitcherChannel):
        """Get channel state."""
        return self.__s.get_channel(channel)

    def set_channel(
        self, channel: SwitcherChannel, state: bool, only_internal: bool = False
    ):
        """Set channel state."""
        if state == self.__s.get_channel(channel):
            return

        self.__s.set_channel(channel, state)
        if not only_internal:
            self.__send_rf_code(self.__c.get_code_for_channel(channel))

    def toggle_channel(self, channel: SwitcherChannel, force: bool = False):
        """Toggle channel state."""
        self.__s.set_channel(
            channel, force if force is not None else not self.__s.get_channel(channel)
        )
        self.__send_rf_code(self.__c.get_code_for_channel(channel))

    def turn_on_all(self):
        """Turn on all channels."""
        self.__s.turn_on_all()
        self.__send_rf_code(self.__c.channel_on)

    def turn_off_all(self):
        """Turn off all channels."""
        self.__s.turn_off_all()
        self.__send_rf_code(self.__c.channel_off)

    def sync_channels(self):
        """Sync channels."""
        if self.__s.is_all_on():
            self.turn_on_all()
        elif self.__s.is_all_off():
            self.turn_off_all()
        else:
            self.__send_rf_code(self.__c.channel_off)

            for ch in SwitcherChannel:
                if self.__s.get_channel(ch):
                    self.__send_rf_code(self.__c.get_code_for_channel(ch))

    def __str__(self):
        """Return string representation of instance for debugging."""
        return str(self.__s) + "\n" + str(self.__c)
