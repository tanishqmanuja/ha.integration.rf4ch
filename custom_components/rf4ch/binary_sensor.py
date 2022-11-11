"""Binary Sensor Platform for Rf 4 Channel Integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import TemplateError
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.template_entity import TemplateEntity

from .const import DOMAIN
from .models import RfSwitcher

SCAN_INTERVAL = timedelta(seconds=5)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=1)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    """Set up entry."""
    # Setup connection with switcher
    sid = config_entry.data[CONF_NAME]
    switcher: RfSwitcher = hass.data[DOMAIN][sid]

    # Add button enitites
    add_entities(switcher.binary_sensors)


class RfAvailabilityBinarySensor(TemplateEntity, BinarySensorEntity):
    """Rf Binary Sensor Class"""

    _attr_has_entity_name = True
    _attr_available = True
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, switcher, name) -> None:
        self._switcher: RfSwitcher = switcher
        self._name = name
        self._unique_id = f"{DOMAIN}_{switcher.unique_id}_{name.lower()}"

        hass = self._switcher.get_hass()
        TemplateEntity.__init__(
            self, hass, availability_template=switcher.availability_template
        )

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name.title()

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the switch."""
        return self._unique_id

    @property
    def icon(self) -> str:
        """Return the icon of the switch."""
        return self._switcher.get_icon(self._name)

    @property
    def is_on(self):
        """Return if the device is on."""
        return self._switcher.available

    @property
    def available(self):
        """Return if the device is online."""
        return True

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._switcher.device_info

    async def async_update(self):
        """Update the stae for templates in switch."""
        for property_name, template, obj in (
            # ("_icon", self._icon_template),
            # ("_entity_picture", self._entity_picture_template),
            ("available", self._availability_template, self._switcher),
        ):
            if template is None:
                continue

            try:
                value = template.async_render()
                if property_name == "available":
                    value = bool(value)
                    # _LOGGER.error(
                    #     "Setting state of %s Switcher to %s", self._switcher.unique_id, value
                    # )
                setattr(obj, property_name, value)
            except TemplateError as ex:
                friendly_property_name = property_name[1:].replace("_", " ")
                if ex.args and ex.args[0].startswith(
                    "UndefinedError: 'None' has no attribute"
                ):
                    # Common during HA startup - so just a warning
                    _LOGGER.warning(
                        "Could not render %s template %s, the state is unknown",
                        friendly_property_name,
                        self._name,
                    )
                    return

                try:
                    setattr(self, property_name, getattr(super(), property_name))
                except AttributeError:
                    _LOGGER.error(
                        "Could not render %s template %s: %s",
                        friendly_property_name,
                        self._name,
                        ex,
                    )
