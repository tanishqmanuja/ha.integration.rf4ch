"""Switcher class for Rf 4 Channel Integration."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.event import TrackTemplate
from homeassistant.helpers.template import Template

from .binary_sensor import RfAvailabilityBinarySensor
from .button import RfButton
from .const import CONF_AVAILABILITY, Platform
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
    SwitcherConfig,
    SwitcherOptions,
)
from .switch import RfSwitch

from tests.helpers.test_event import async_track_template_result

ICONS = {
    CHANNEL_A: "mdi:numeric-1-box",
    CHANNEL_B: "mdi:numeric-2-box",
    CHANNEL_C: "mdi:numeric-3-box",
    CHANNEL_D: "mdi:numeric-4-box",
    ACTION_ON: "mdi:power-on",
    ACTION_OFF: "mdi:power-off",
    ACTION_SYNC: "mdi:sync",
    CONF_AVAILABILITY: "mdi:connection",
}

_LOGGER = logging.getLogger(__name__)


def generate_codes(code_prefix: str):
    """Returns code dictionary"""

    return {
        Channel.A: f"{code_prefix}0010",
        Channel.B: f"{code_prefix}1000",
        Channel.C: f"{code_prefix}0001",
        Channel.D: f"{code_prefix}0100",
        Action.ON: f"{code_prefix}1100",
        Action.OFF: f"{code_prefix}0011",
    }


class EnitityManager:
    """Manages Enitities for switcher"""

    def __init__(self):
        self._entities = {}

    def attach_entity(self, platform: Platform, key: str, entity: Entity):
        """Attaches entity to manager"""
        if not isinstance(self._entities.get(platform), dict):
            self._entities.setdefault(platform, {})

        self._entities[platform][key] = entity

    def get_entity(self, platform: Platform, key: str) -> Entity | None:
        """Retrieves entity from manager"""
        return self._entities.get(platform, {}).get(key, None)

    def get_entities(self, platform: Platform) -> list[Entity] | None:
        """Retrieves list of entities from manager"""
        return self._entities.get(platform, {}).values()

    def mark_for_update(self, platform: Platform, key: str):
        """Mark for HA state update"""
        entity = self.get_entity(platform, key)
        if entity.hass is None:
            return
        entity.schedule_update_ha_state()


class SwitcherStateManager:
    """Class to manage switcher state"""

    def __init__(self):
        setattr(self, Channel.A, False)
        setattr(self, Channel.B, False)
        setattr(self, Channel.C, False)
        setattr(self, Channel.D, False)

    def get_state(self, channel: Channel):
        """Returns the state of a channel"""
        return getattr(self, channel)

    def set_state(self, channel: Channel, state: bool):
        """Updates the state of a channel"""
        setattr(self, channel, state)


class RfSwitcher:
    """RfSwitcher Class"""

    def __init__(
        self, hass: HomeAssistant, config: SwitcherConfig, options: SwitcherOptions
    ) -> None:
        self._hass = hass

        self._config = config
        self._options = options
        self._codes = generate_codes(config.code_prefix)
        self._state_manager = SwitcherStateManager()
        self._entity_manager = EnitityManager()
        self._available = True

        for channel in Channel:
            self._entity_manager.attach_entity(
                platform=Platform.SWITCH,
                key=channel,
                entity=RfSwitch(switcher=self, channel=channel),
            )

        for action in Action:
            self._entity_manager.attach_entity(
                platform=Platform.BUTTON,
                key=action,
                entity=RfButton(switcher=self, action=action),
            )

        if self._config.availability_template:
            _LOGGER.info(
                "Template found for %s Switcher: %s",
                self._config.name,
                self._config.availability_template,
            )
            self._availability_template = Template(config.availability_template, hass)

            self._entity_manager.attach_entity(
                platform=Platform.BINARY_SENSOR,
                key=CONF_AVAILABILITY,
                entity=RfAvailabilityBinarySensor(self, CONF_AVAILABILITY),
            )

            _LOGGER.info(
                "Registering availability tracker %s Switcher", self._config.name
            )
            self._async_track_availability()

    async def setup(self):
        """Setups the async inits of switcher"""
        if self._config.availability_template:
            await self._initial_template_render()
        return True

    async def _async_on_remove(self):
        """Cleanup for switcher on removal"""
        return True

    async def _initial_template_render(self):
        """Update the state for template in switcher."""
        for property_name, template in (("available", self._availability_template),):
            if template is None:
                continue

            try:
                value = template.async_render()
                if property_name == "available":
                    value = bool(value)
                setattr(self, property_name, value)
            except TemplateError as ex:
                friendly_property_name = property_name[1:].replace("_", " ")
                if ex.args and ex.args[0].startswith(
                    "UndefinedError: 'None' has no attribute"
                ):
                    # Common during HA startup - so just a warning
                    _LOGGER.warning(
                        "Could not render %s template %s, the state is unknown",
                        friendly_property_name,
                        self._config.name,
                    )
                    return

                try:
                    setattr(self, property_name, getattr(super(), property_name))
                except AttributeError:
                    _LOGGER.error(
                        "Could not render %s template %s: %s",
                        friendly_property_name,
                        self._config.name,
                        ex,
                    )

    def _async_track_availability(self):
        """Track availability."""

        @callback
        def _async_on_template_update(event, updates):
            """Update ha state when dependencies update."""

            result = updates.pop().result

            if isinstance(result, TemplateError):
                self._available = None
            else:
                self.available = bool(result)

            # if event:
            #     self.async_set_context(event.context)

            # self.async_schedule_update_ha_state(True)
            self._entity_manager.mark_for_update(
                platform=Platform.BINARY_SENSOR, key=CONF_AVAILABILITY
            )

        async_track_template_result(
            hass=self._hass,
            track_templates=[TrackTemplate(self._availability_template, None)],
            action=_async_on_template_update,
        )

    @staticmethod
    def get_icon(channel_or_action):
        """Returns the icon for switches"""
        return ICONS.get(channel_or_action)

    @property
    def hass(self) -> HomeAssistant:
        """Return the HA instance"""
        return self._hass

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the switch."""
        return self._config.unique_id

    @property
    def available(self) -> bool:
        """Return the availabilty of switcher."""
        return self._available

    @available.setter
    def available(self, state: bool) -> None:
        if self._available == state:
            return

        self._available = state
        for channel in Channel:
            self._entity_manager.mark_for_update(Platform.SWITCH, channel)
        for action in Action:
            self._entity_manager.mark_for_update(Platform.BUTTON, action)

    @property
    def device_info(self) -> DeviceInfo:
        """Returns device info of the switcher."""
        return self._config.device_info

    def set_options(self, options: SwitcherOptions) -> None:
        """Setter for switcher options."""
        if self._options.stateless != options.stateless:
            for channel in Channel:
                self.update_channel_state(channel=channel, state=False)

        self._options = options

    def get_entities(self, platform: Platform) -> bool:
        """Return the entities for platform in switcher."""
        return self._entity_manager.get_entities(platform=platform)

    def update_channel_state(self, channel, state: bool) -> None:
        """Update channel state internally."""
        if not self._options.stateless:
            self._state_manager.set_state(channel=channel, state=state)
            self._entity_manager.mark_for_update(platform=Platform.SWITCH, key=channel)

    def get_channel_state(self, channel) -> bool:
        """Get internal state of channel."""
        return self._state_manager.get_state(channel=channel)

    def set_channel_state(self, channel, state: bool) -> None:
        """Set channel state."""
        if self.get_channel_state(channel=channel) != state:
            self.update_channel_state(channel, state)
            self._send_rf(channel)

    def handle_action(self, action) -> None:
        """Handle action."""
        if action == ACTION_SYNC:
            self._sync()
        elif action in (ACTION_ON, ACTION_OFF):
            self._send_rf(action)
            state = action == ACTION_ON
            for channel in Channel:
                self.update_channel_state(channel=channel, state=state)

    def _sync(self) -> None:
        """Reset and sync channel states."""
        self._send_rf(Action.OFF)
        for channel in Channel:
            if self.get_channel_state(channel) is True:
                self._send_rf(code=channel)

    def _send_rf(self, code) -> None:
        """Call service to send rf code."""
        code = self._codes[code]
        domain, service = self._config.service_id.split(".")
        service_data = {"code": code, **self._config.service_data}
        _LOGGER.info("Sending Code %s via %s.%s", code, domain, service)
        self._hass.services.call(
            domain=domain, service=service, service_data=service_data
        )
