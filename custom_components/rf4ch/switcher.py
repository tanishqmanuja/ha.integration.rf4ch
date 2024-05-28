"""Switcher Device for RF Four Channel integration."""

from dataclasses import dataclass
import logging
from typing import TypedDict

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.event import TrackTemplate, async_track_template_result
from homeassistant.helpers.template import Template

from .button import RfButton
from .lib.switcher import (
    Switcher as InternalSwitcher,
    SwitcherAction,
    SwitcherChannel,
    SwitcherCodeDict,
)
from .switch import RfSwitch

_LOGGER = logging.getLogger(__name__)


class RfServiceDict(TypedDict):
    """RF service dictionary."""

    id: str
    data: dict


@dataclass(frozen=True)
class SwitcherOptions:
    """Switcher options."""

    stateless: bool


@dataclass(frozen=True)
class SwitcherConfig:
    """Switcher config."""

    name: str
    unique_id: str
    code: SwitcherCodeDict
    service: RfServiceDict
    availability_template: str
    device_info: DeviceInfo


class EntityStore:
    """Entity store."""

    def __init__(self) -> None:
        """Initialize entity store."""
        self._store: dict = {}

    def attach(self, platform: Platform, key: str, entity: Entity) -> None:
        """Attach entity with platform to entity store."""
        if self._store.get(platform) is None:
            self._store.setdefault(platform, {})

        self._store[platform][key] = entity

    def detach(self, platform: Platform, key: str) -> None:
        """Detach entity from entity store."""
        if self._store.get(platform) is None:
            return
        self._store[platform].pop(key)

    def get(self, platform: Platform, key: str) -> Entity | None:
        """Get entity from entity store."""
        if self._store.get(platform) is None:
            return None
        return self._store[platform].get(key)

    def get_for_platform(self, platform: Platform) -> list[Entity]:
        """Get entities for platform from entity store."""
        if self._store.get(platform) is None:
            return []
        return list(self._store[platform].values())

    def mark_for_update(self, platform: Platform, key: str) -> None:
        """Update entity in entity store."""
        entity = self.get(platform, key)
        if entity.hass is not None:
            entity.schedule_update_ha_state()

    def mark_platform_for_update(self, platform: Platform) -> None:
        """Update all entities for platform in entity store."""
        for entity in self.get_for_platform(platform):
            if entity.hass is not None:
                entity.schedule_update_ha_state()

    def mark_all_for_update(self) -> None:
        """Update all entities in entity store."""
        for entities in self._store.values():
            for entity in entities.values():
                if entity.hass is not None:
                    entity.schedule_update_ha_state()


class RfSwitcher:
    """Class for RF Four Channel Switcher."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: SwitcherConfig,
        options: SwitcherOptions = SwitcherOptions(stateless=False),
    ) -> None:
        """Initialize switcher."""
        self.hass = hass
        self._config = config
        self._options = options
        self._switcher = InternalSwitcher(config.code, self._send_rf_code)
        self._entity_store = EntityStore()
        self._available = True

        self._unsub_track_template = None

        # Initialise channel switches
        for channel in SwitcherChannel:
            self._entity_store.attach(Platform.SWITCH, channel, RfSwitch(self, channel))
        for action in SwitcherAction:
            self._entity_store.attach(Platform.BUTTON, action, RfButton(self, action))

    @property
    def name(self) -> str:
        """Rehassname."""
        return self._config.name

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return self._config.unique_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return self._config.device_info

    @property
    def available(self) -> bool:
        """Return availability."""
        return self._available

    @property
    def is_stateless(self) -> bool:
        """Return stateless."""
        return self._options.stateless

    def get_channel(self, channel: SwitcherChannel) -> bool:
        """Get channel state."""
        if self.is_stateless:
            return False
        return self._switcher.get_channel(channel)

    def set_channel(
        self, channel: SwitcherChannel, state: bool, only_internal: bool = False
    ):
        """Set channel state."""
        if self.is_stateless:
            if not only_internal:
                self._switcher.toggle_channel(channel, False)
        else:
            self._switcher.set_channel(channel, state, only_internal)
            self._entity_store.mark_for_update(Platform.SWITCH, channel)

    def turn_on_all(self):
        """Turn on all channels."""
        self._switcher.turn_on_all()
        self._entity_store.mark_platform_for_update(Platform.SWITCH)

    def turn_off_all(self):
        """Turn off all channels."""
        self._switcher.turn_off_all()
        self._entity_store.mark_platform_for_update(Platform.SWITCH)

    def sync_channels(self):
        """Sync channels."""
        self._switcher.sync_channels()

    def handle_action(self, action: SwitcherAction):
        """Handle action."""
        if action == SwitcherAction.ON:
            self.turn_on_all()
        if action == SwitcherAction.OFF:
            self.turn_off_all()
        if action == SwitcherAction.SYNC:
            self.sync_channels()

    def get_entities_for_platform(self, platform: Platform) -> list[Entity]:
        """Get entities for platform."""
        return self._entity_store.get_for_platform(platform)

    def update_options(self, options: SwitcherOptions):
        """Update options."""
        self._options = options

    def _send_rf_code(self, code: str):
        domain, service = self._config.service["id"].split(".")
        extra_service_data = self._config.service.get("data", None) or {}
        self.hass.services.call(domain, service, {"code": code, **extra_service_data})

    def _update_availability(self, result):
        """Update availability based on template result."""
        try:
            self._available = bool(result)
        except TemplateError as ex:
            self._available = False
            _LOGGER.error("Error rendering availability template: %s", ex)
        finally:
            self._entity_store.mark_all_for_update()

    async def async_added_to_hass(self):
        """Set switcher."""

        if self._config.availability_template is None:
            return

        @callback
        def _async_on_template_update(event, updates):
            """Update ha state when dependencies update."""

            result = updates.pop().result

            if isinstance(result, TemplateError):
                self._available = None
            else:
                self._update_availability(result)

        _template = Template(self._config.availability_template, self.hass)
        self._unsub_track_template = async_track_template_result(
            self.hass,
            [TrackTemplate(_template, None)],
            _async_on_template_update,
        )

        # initial template result
        self._update_availability(_template.async_render())

    async def async_will_remove_from_hass(self):
        """Remove switcher."""

        if self._unsub_track_template is not None:
            self._unsub_track_template()
            self._unsub_track_template = None
