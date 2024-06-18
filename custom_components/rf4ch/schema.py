"""Schema for RF Four Channel integration."""

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_AVAILABILITY_TEMPLATE,
    CONF_CODE,
    CONF_CODE_A,
    CONF_CODE_B,
    CONF_CODE_C,
    CONF_CODE_D,
    CONF_CODE_OFF,
    CONF_CODE_ON,
    CONF_CODE_PREFIX,
    CONF_ID,
    CONF_NAME,
    CONF_OPTIONS,
    CONF_SERVICE,
    CONF_SERVICE_DATA,
    CONF_STATELESS,
    CONF_TRANSMISSION_GAP,
)

RF_SERVICE_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): cv.service,
        vol.Optional(CONF_SERVICE_DATA): vol.Schema({}, extra=vol.ALLOW_EXTRA),
    }
)

RF_CODE_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CODE_ON): cv.string,
        vol.Required(CONF_CODE_OFF): cv.string,
        vol.Required(CONF_CODE_A): cv.string,
        vol.Required(CONF_CODE_B): cv.string,
        vol.Required(CONF_CODE_C): cv.string,
        vol.Required(CONF_CODE_D): cv.string,
        vol.Optional(CONF_CODE_PREFIX): cv.string,
    }
)

SWITCHER_OPTIONS_SCHEMA = vol.Schema({vol.Optional(CONF_STATELESS): cv.boolean})

SWITCHER_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_SERVICE): RF_SERVICE_CONFIG_SCHEMA,
        vol.Required(CONF_CODE): RF_CODE_CONFIG_SCHEMA,
        vol.Optional(CONF_AVAILABILITY_TEMPLATE): cv.template,
        vol.Optional(CONF_OPTIONS): SWITCHER_OPTIONS_SCHEMA,
        vol.Optional(CONF_TRANSMISSION_GAP): vol.Range(min=0.0, max=1.0),
    }
)
