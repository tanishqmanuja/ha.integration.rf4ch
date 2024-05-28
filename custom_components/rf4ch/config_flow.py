"""Config Flow for RF Four Channel integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.util import slugify

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
    CONF_SERVICE,
    CONF_SERVICE_DATA,
    CONF_STATELESS,
    CONF_UNIQUE_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


CODE_SCHEMA = vol.Schema(
    {
        vol.Required(f"{CONF_CODE}_{CONF_CODE_PREFIX}"): selector.TextSelector(),
        vol.Required(
            f"{CONF_CODE}_{CONF_CODE_A}", default="0010"
        ): selector.TextSelector(),
        vol.Required(
            f"{CONF_CODE}_{CONF_CODE_B}", default="1000"
        ): selector.TextSelector(),
        vol.Required(
            f"{CONF_CODE}_{CONF_CODE_C}", default="0001"
        ): selector.TextSelector(),
        vol.Required(
            f"{CONF_CODE}_{CONF_CODE_D}", default="0100"
        ): selector.TextSelector(),
        vol.Required(
            f"{CONF_CODE}_{CONF_CODE_ON}", default="1100"
        ): selector.TextSelector(),
        vol.Required(
            f"{CONF_CODE}_{CONF_CODE_OFF}", default="0011"
        ): selector.TextSelector(),
    }
)


def _create_data_schema(services: list):
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default="RF Switcher"): selector.TextSelector(),
            vol.Required(f"{CONF_SERVICE}_{CONF_ID}"): selector.SelectSelector(
                {"options": services, "mode": selector.SelectSelectorMode.DROPDOWN}
            ),
            vol.Optional(
                f"{CONF_SERVICE}_{CONF_SERVICE_DATA}"
            ): selector.ObjectSelector(),
            vol.Optional(CONF_AVAILABILITY_TEMPLATE): selector.TemplateSelector(),
        }
    )


async def _get_service_list(hass: HomeAssistant):
    """Return list of services."""
    services_dict = hass.services.async_services()

    return [
        f"{provider}.{name}"
        for provider, services in services_dict.items()
        if isinstance(services, dict)
        for name in services
    ]


class RfConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RF Four Channel."""

    VERSION = 1

    data = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle flow initiated by user."""
        services = await _get_service_list(self.hass)

        if user_input is not None:
            _LOGGER.debug("step user input: %s", user_input)

            # reset data
            self.data = {}

            self.data[CONF_UNIQUE_ID] = slugify(user_input[CONF_NAME])
            self.data[CONF_NAME] = user_input[CONF_NAME]
            self.data[CONF_SERVICE] = {
                CONF_ID: user_input[f"{CONF_SERVICE}_{CONF_ID}"],
                CONF_SERVICE_DATA: user_input.get(
                    f"{CONF_SERVICE}_{CONF_SERVICE_DATA}", {}
                ),
            }

            if CONF_AVAILABILITY_TEMPLATE in user_input:
                self.data[CONF_AVAILABILITY_TEMPLATE] = user_input[
                    CONF_AVAILABILITY_TEMPLATE
                ]

            return await self.async_step_code()

        return self.async_show_form(
            step_id="user",
            data_schema=_create_data_schema(services),
        )

    async def async_step_code(self, user_input: dict[str, Any] | None = None):
        """Handle code step."""

        if user_input is not None:
            _LOGGER.debug("step code input: %s", user_input)

            self.data[CONF_CODE] = {
                CONF_CODE_PREFIX: user_input.get(f"{CONF_CODE}_{CONF_CODE_PREFIX}"),
                CONF_CODE_A: user_input[f"{CONF_CODE}_{CONF_CODE_A}"],
                CONF_CODE_B: user_input[f"{CONF_CODE}_{CONF_CODE_B}"],
                CONF_CODE_C: user_input[f"{CONF_CODE}_{CONF_CODE_C}"],
                CONF_CODE_D: user_input[f"{CONF_CODE}_{CONF_CODE_D}"],
                CONF_CODE_ON: user_input[f"{CONF_CODE}_{CONF_CODE_ON}"],
                CONF_CODE_OFF: user_input[f"{CONF_CODE}_{CONF_CODE_OFF}"],
            }

            return self.async_create_entry(title=self.data[CONF_NAME], data=self.data)

        return self.async_show_form(
            step_id="code",
            data_schema=CODE_SCHEMA,
        )

    async def async_step_import(self, config):
        """Handle step import."""

        await self.async_set_unique_id(config[CONF_UNIQUE_ID])
        return self.async_create_entry(title=config[CONF_NAME], data=config)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Required(
                CONF_STATELESS,
                default=self.config_entry.options.get(CONF_STATELESS, False),
            ): bool,
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))
