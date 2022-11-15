"""Integration Component for Rf 4 Channel Integration."""

from __future__ import annotations

from copy import copy
import logging

import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, SOURCE_USER, ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_AVAILABILITY,
    CONF_CODE,
    CONF_ID,
    CONF_NAME,
    CONF_OPTIONS,
    CONF_SERVICE,
    CONF_SERVICE_DATA,
    CONF_STATELESS,
    CONF_UNIQUE_ID,
    DOMAIN,
    PLATFORMS,
)
from .helpers import (
    generate_switcher_conf_from_entry,
    generate_switcher_opts_from_entry,
    get_switcher_confs_from_domain_conf,
    switcher_conf_to_entry_data,
)
from .switcher import RfSwitcher

_LOGGER = logging.getLogger(__name__)

SERVICE_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): cv.service,
        vol.Optional(CONF_SERVICE_DATA): vol.Schema({}, extra=vol.ALLOW_EXTRA),
    }
)

SWITCHER_OPTIONS_SCHEMA = vol.Schema({vol.Optional(CONF_STATELESS): cv.boolean})

SWITCHER_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_SERVICE): SERVICE_CONFIG_SCHEMA,
        vol.Required(CONF_CODE): cv.string,
        vol.Optional(CONF_AVAILABILITY): cv.template,
        vol.Optional(CONF_OPTIONS): SWITCHER_OPTIONS_SCHEMA,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: cv.schema_with_slug_keys(SWITCHER_CONFIG_SCHEMA)},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Rf 4 Channel integration from YAML"""

    rf4ch_conf = config.get(DOMAIN)
    hass.data.setdefault(DOMAIN, {})

    if not rf4ch_conf:
        return True

    switcher_confs = get_switcher_confs_from_domain_conf(rf4ch_conf)

    if len(switcher_confs) < 1:
        return True

    # Delete specific entries that no longer exist in the config
    if hass.config_entries.async_entries(DOMAIN):
        for entry in hass.config_entries.async_entries(DOMAIN):
            remove = True
            for switcher_conf in switcher_confs:
                if entry.source == SOURCE_USER:
                    remove = False
                    break

                if (
                    entry.source == SOURCE_IMPORT
                    and entry.data[CONF_UNIQUE_ID] == switcher_conf[CONF_UNIQUE_ID]
                ):
                    remove = False
                    break

            if remove:
                await hass.config_entries.async_remove(entry.entry_id)

    # Setup new entries and update old entries
    for switcher_conf in switcher_confs:
        # copy to prevent mutation
        switcher_cfg = copy(switcher_conf)

        existing_entry = False
        for entry in hass.config_entries.async_entries(DOMAIN):
            if switcher_cfg[CONF_UNIQUE_ID] == entry.data[CONF_UNIQUE_ID]:
                existing_entry = True
                switcher_cfg[CONF_NAME] = entry.data[CONF_NAME]
                hass.config_entries.async_update_entry(
                    entry, data=switcher_conf_to_entry_data(switcher_cfg)
                )
                break
        if not existing_entry:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": SOURCE_IMPORT},
                    data=switcher_conf_to_entry_data(switcher_cfg),
                )
            )

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up a switcher from a config entry."""
    if DOMAIN not in hass.data:
        hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug(
        "Setting up rf4ch id %s, name %s, config %s",
        config_entry.entry_id,
        config_entry.data[CONF_NAME],
        config_entry.data,
    )

    # Setup switcher

    switcher_config = generate_switcher_conf_from_entry(config_entry)
    switcher_opts = generate_switcher_opts_from_entry(config_entry)
    switcher = RfSwitcher(hass=hass, config=switcher_config, options=switcher_opts)
    await switcher.setup()
    hass.data[DOMAIN][config_entry.entry_id] = switcher

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    )

    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    switcher = hass.data[DOMAIN].get(config_entry.entry_id)
    switcher_opts = generate_switcher_opts_from_entry(config_entry)
    if switcher:
        switcher.set_options(switcher_opts)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle removal of an entry."""
    switcher = hass.data[DOMAIN].pop(config_entry.entry_id)
    return await switcher.async_on_remove()
