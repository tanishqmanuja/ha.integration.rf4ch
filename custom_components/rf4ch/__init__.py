"""Integration Component for Rf 4 Channel Integration."""

from __future__ import annotations

from copy import copy
import logging

import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_AVAILABILITY,
    CONF_CODE,
    CONF_FRIENDLY_NAME,
    CONF_NAME,
    CONF_SERVICE,
    CONF_SWITCHERS,
    CONF_UNIQUE_ID,
    DOMAIN,
)
from .helpers import parse_config, serialize_entry_data
from .switcher import RfSwitcher

_LOGGER = logging.getLogger(__name__)

SWITCHER_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_SERVICE): cv.string,
        vol.Required(CONF_CODE): cv.string,
        vol.Optional(CONF_UNIQUE_ID): cv.template,
        vol.Optional(CONF_FRIENDLY_NAME): cv.string,
        vol.Optional(CONF_AVAILABILITY): cv.template,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_SWITCHERS): vol.All(
                    cv.ensure_list, [SWITCHER_CONFIG_SCHEMA]
                ),
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Rf 4 Channel component."""

    unparsed_conf = config.get(DOMAIN)
    conf = parse_config(unparsed_conf)

    hass.data[DOMAIN] = {}

    if CONF_SWITCHERS in conf:
        switchers = conf[CONF_SWITCHERS]

    if not switchers:
        return True

    # Delete specific entries that no longer exist in the config
    if hass.config_entries.async_entries(DOMAIN):
        for entry in hass.config_entries.async_entries(DOMAIN):
            remove = True
            for switcher in switchers:
                if not entry.data.get(CONF_UNIQUE_ID):
                    break

                if entry.data[CONF_UNIQUE_ID] == switcher[CONF_UNIQUE_ID]:
                    remove = False
                    break
            if remove:
                await hass.config_entries.async_remove(entry.entry_id)

    # Setup new entries and update old entries
    for switcher in switchers:
        # copy to prevent mutation
        switcher_config = copy(switcher)

        sid = switcher[CONF_UNIQUE_ID]
        hass.data[DOMAIN][sid] = switcher_config

        existing_entry = False

        for entry in hass.config_entries.async_entries(DOMAIN):
            if switcher[CONF_UNIQUE_ID] == entry.data[CONF_UNIQUE_ID]:
                existing_entry = True
                switcher_config[CONF_NAME] = entry.data[CONF_NAME]
                hass.config_entries.async_update_entry(
                    entry, data=serialize_entry_data(switcher_config)
                )
                break
        if not existing_entry:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": SOURCE_IMPORT},
                    data=serialize_entry_data(switcher_config),
                )
            )

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up a switcher from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    _LOGGER.debug(
        "Setting up rf4ch id %s, name %s, config %s",
        config_entry.entry_id,
        config_entry.data[CONF_NAME],
        config_entry.data,
    )

    sid = config_entry.data[CONF_UNIQUE_ID]
    config = hass.data[DOMAIN][sid]

    switcher = RfSwitcher(hass, config, config_entry)

    if not await switcher.async_setup():
        return False

    # Set switcher in data for switch and button platforms
    hass.data[DOMAIN][sid] = switcher

    return True
