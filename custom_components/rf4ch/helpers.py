"""Helpers for Rf 4 Channel Integration."""

from copy import copy

from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_AVAILABILITY,
    CONF_CODE,
    CONF_DEVICE_ID,
    CONF_FRIENDLY_NAME,
    CONF_NAME,
    CONF_SWITCHERS,
    CONF_UNIQUE_ID,
)


def parse_config(config: ConfigType):
    """Return parsed config"""
    if config is None:
        return {}

    cfg = copy(config)

    if CONF_SWITCHERS in cfg:
        switchers = cfg[CONF_SWITCHERS]

    for switcher in switchers:
        switcher[CONF_UNIQUE_ID] = get_unique_id(switcher)
        switcher[CONF_DEVICE_ID] = get_device_id(switcher)
        switcher[CONF_FRIENDLY_NAME] = get_friendly_name(switcher)

    return cfg


def serialize_entry_data(config: ConfigType):
    """Return serialized config"""
    cfg = copy(config)

    keys_to_remove = set([CONF_AVAILABILITY]).intersection(set(cfg.keys()))
    for key in keys_to_remove:
        del cfg[key]

    return cfg


def get_friendly_name(config: ConfigType):
    """Return friendly name"""
    name = config[CONF_NAME]
    friendly_name = config.get(CONF_FRIENDLY_NAME, name)
    return friendly_name.title()


def get_unique_id(config: ConfigType):
    """Return unique id"""
    name = config[CONF_NAME]
    return config.get(CONF_UNIQUE_ID, name)


def get_device_id(config: ConfigType):
    """Return device id"""
    uid = get_unique_id(config)
    code = config[CONF_CODE]
    return f"{uid}_{code}"
