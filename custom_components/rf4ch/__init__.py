"""RF Four Channel integration."""

import json
import logging

import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, SOURCE_USER, ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from . import helpers
from .const import CONF_UNIQUE_ID, DOMAIN, PLATFORMS
from .schema import SWITCHER_CONFIG_SCHEMA
from .services import async_setup_dummy_rf_send_service
from .switcher import RfSwitcher

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: cv.schema_with_slug_keys(SWITCHER_CONFIG_SCHEMA)},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the RF Four Channel Integration using Config."""

    if DOMAIN not in config:
        return True

    # Register our services with Home Assistant.
    async_setup_dummy_rf_send_service(hass)

    # Delete redundant exisiting entries
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.source == SOURCE_USER:
            continue
        if entry.source == SOURCE_IMPORT and next(
            (
                config_entry
                for unique_id, config_entry in config[DOMAIN].items()
                if unique_id == entry.data[CONF_UNIQUE_ID]
            ),
            None,
        ):
            continue

        _LOGGER.debug("Cleaning up %s", entry.data[CONF_UNIQUE_ID])
        await hass.config_entries.async_remove(entry.entry_id)

    # Add new entries or update existing ones
    def _are_same_entries(user_config_entry, hass_config_entry):
        a = helpers.normalise_config_entry(user_config_entry)
        b = hass_config_entry  # Mapping proxy canot be normalised

        keys = set(a.keys()).intersection(set(b.keys()))

        return hash(json.dumps({k: a[k] for k in keys}, sort_keys=True)) == hash(
            json.dumps({k: b[k] for k in keys}, sort_keys=True)
        )

    for unique_id, config_entry in config[DOMAIN].items():
        _found = next(
            (
                entry
                for entry in hass.config_entries.async_entries(DOMAIN)
                if entry.data[CONF_UNIQUE_ID] == unique_id
            ),
            None,
        )

        if _found:
            _LOGGER.debug("Found existing entry %s", unique_id)

        if _found and not _are_same_entries(config_entry, _found.data):
            data = helpers.normalise_config_entry(config_entry)
            data[CONF_UNIQUE_ID] = unique_id

            _LOGGER.debug("Updating %s, %s", unique_id, data)
            hass.config_entries.async_update_entry(
                _found,
                data=data,
            )

        if not _found:
            data = helpers.normalise_config_entry(config_entry)
            data[CONF_UNIQUE_ID] = unique_id

            _LOGGER.debug("Adding %s, %s", unique_id, data)
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": SOURCE_IMPORT},
                    data=data,
                )
            )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RF Four Channel from a config entry."""
    if DOMAIN not in hass.data:
        hass.data.setdefault(DOMAIN, {})

    switcher = RfSwitcher(
        hass,
        helpers.generate_switcher_config(entry),
        helpers.generate_switcher_options(entry),
    )
    await switcher.async_added_to_hass()

    hass.data[DOMAIN][entry.entry_id] = switcher

    # Setup platforms
    hass.create_task(hass.config_entries.async_forward_entry_setups(entry, PLATFORMS))
    # Add Update Listener
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    switcher: RfSwitcher = hass.data[DOMAIN].get(entry.entry_id)
    if switcher:
        _LOGGER.info("Updating switcher options for %s", switcher.unique_id)
        switcher.update_options(helpers.generate_switcher_options(entry))


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle removal of an entry."""
    switcher: RfSwitcher = hass.data[DOMAIN].pop(config_entry.entry_id)
    await switcher.async_will_remove_from_hass()
    return True
