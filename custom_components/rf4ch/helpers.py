"""Helpers for Rf 4 Channel Integration."""

from copy import copy

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.template import Template
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_AVAILABILITY,
    CONF_CODE,
    CONF_ID,
    CONF_NAME,
    CONF_SERVICE,
    CONF_SERVICE_DATA,
    CONF_STATELESS,
    CONF_UNIQUE_ID,
    DOMAIN,
    HW_VERSION,
    MANUFACTURER,
    MODEL,
    SW_VERSION,
)
from .models import SwitcherConfig, SwitcherOptions


def get_switcher_confs_from_domain_conf(config: ConfigType):
    """Returns list of switcher configs"""
    switcher_confs = []

    for key, val in config.items():
        if isinstance(val, dict):
            switcher_conf = copy(val)
            switcher_conf[CONF_UNIQUE_ID] = key
            switcher_confs.append(switcher_conf)

    return switcher_confs


def generate_switcher_conf_from_entry(entry: ConfigEntry):
    """Return switcher dataclass"""

    switcher_conf = entry.data

    name = switcher_conf[CONF_NAME]
    unique_id = switcher_conf[CONF_UNIQUE_ID]
    service_id = switcher_conf[CONF_SERVICE][CONF_ID]
    service_data = switcher_conf[CONF_SERVICE].get(CONF_SERVICE_DATA, {})
    code_prefix = switcher_conf[CONF_CODE]
    availability_template = switcher_conf.get(CONF_AVAILABILITY)
    device_info = get_device_info(name=name, uid=unique_id)

    return SwitcherConfig(
        name=name,
        unique_id=unique_id,
        service_id=service_id,
        service_data=service_data,
        code_prefix=code_prefix,
        availability_template=availability_template,
        device_info=device_info,
    )


def generate_switcher_opts_from_entry(entry: ConfigEntry):
    """Return switcher dataclass"""

    switcher_opts = entry.options

    stateless = switcher_opts.get(CONF_STATELESS)

    return SwitcherOptions(stateless=stateless)


def switcher_conf_to_entry_data(config: ConfigType):
    """Return serialized config"""
    data = copy(config)

    template_keys = set([CONF_AVAILABILITY]).intersection(set(data.keys()))
    for key in template_keys:
        val = data[key]
        if isinstance(val, str):
            data[key] = val
        elif isinstance(val, Template):
            data[key] = val.template

    return data


def get_device_info(name: str, uid: str) -> DeviceInfo:
    """Returns device info for switcher"""
    return DeviceInfo(
        identifiers={
            # Serial numbers are unique identifiers within a specific domain
            (DOMAIN, uid)
        },
        name=f"{name} Switcher",
        manufacturer=MANUFACTURER,
        model=MODEL,
        sw_version=SW_VERSION,
        hw_version=HW_VERSION,
    )
