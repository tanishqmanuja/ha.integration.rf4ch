"""Helpers for RF Four Channel integration."""

from copy import copy

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.template import Template
from homeassistant.helpers.typing import ConfigType

from . import const
from .switcher import SwitcherConfig, SwitcherOptions


def normalise_config_entry(config: ConfigType) -> ConfigType:
    """Normalise config entry."""
    c = copy(config)

    if const.CONF_AVAILABILITY_TEMPLATE in c and isinstance(
        c[const.CONF_AVAILABILITY_TEMPLATE], Template
    ):
        c[const.CONF_AVAILABILITY_TEMPLATE] = c[
            const.CONF_AVAILABILITY_TEMPLATE
        ].template

    if const.CONF_AVAILABILITY_TEMPLATE not in c:
        c[const.CONF_AVAILABILITY_TEMPLATE] = None

    return c


def generate_switcher_config(
    config_or_entry: ConfigType | ConfigEntry,
) -> SwitcherConfig:
    """Generate SwitcherConfig from config or entry."""
    config = (
        config_or_entry.data
        if isinstance(config_or_entry, ConfigEntry)
        else config_or_entry
    )

    return SwitcherConfig(
        name=config[const.CONF_NAME],
        unique_id=config[const.CONF_UNIQUE_ID],
        code=config[const.CONF_CODE],
        service=config[const.CONF_SERVICE],
        availability_template=config.get(const.CONF_AVAILABILITY_TEMPLATE),
        device_info=get_device_info(
            config[const.CONF_UNIQUE_ID], config[const.CONF_NAME]
        ),
    )


def generate_switcher_options(
    config_or_entry: ConfigType | ConfigEntry,
) -> SwitcherOptions:
    """Generate SwitcherOptions from config or entry."""

    options = (
        config_or_entry.options
        if isinstance(config_or_entry, ConfigEntry)
        else config_or_entry.get(const.CONF_OPTIONS, {})
    )

    return SwitcherOptions(
        stateless=options.get(const.CONF_STATELESS, False),
    )


def get_device_info(uid: str, name: str) -> DeviceInfo:
    """Get device info."""
    return DeviceInfo(
        identifiers={(const.DOMAIN, uid)},
        manufacturer=const.MANUFACTURER,
        model=const.MODEL,
        name=name,
        sw_version=const.SW_VERSION,
        hw_version=const.HW_VERSION,
    )
