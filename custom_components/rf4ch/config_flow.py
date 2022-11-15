"""Config flow to configure Rf 4 Channel Integration."""

from copy import copy
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.util import slugify

from .const import (
    CONF_AVAILABILITY,
    CONF_CODE,
    CONF_ID,
    CONF_NAME,
    CONF_OPTIONS,
    CONF_SERVICE,
    CONF_SERVICE_DATA,
    CONF_UNIQUE_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


CONF_STATELESS = "stateless"


def _data_schema(services: list):
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME, description={"suggested_value": "My Room"}
            ): selector.TextSelector(),
            vol.Required(f"{CONF_SERVICE}_{CONF_ID}"): selector.SelectSelector(
                {"options": services, "mode": selector.SelectSelectorMode.DROPDOWN}
            ),
            vol.Optional(
                f"{CONF_SERVICE}_{CONF_SERVICE_DATA}"
            ): selector.ObjectSelector(),
            vol.Required(CONF_CODE): selector.TextSelector(),
            vol.Optional(CONF_AVAILABILITY): selector.TemplateSelector(),
        }
    )


async def parse_input(hass: HomeAssistant, cfg):
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    name = cfg[CONF_NAME]
    uid = slugify(name)
    title = f"{name} Switcher".title()

    data = copy(cfg)
    data[CONF_UNIQUE_ID] = uid
    data[CONF_SERVICE] = {
        CONF_ID: cfg[f"{CONF_SERVICE}_{CONF_ID}"],
        CONF_SERVICE_DATA: cfg.get(f"{CONF_SERVICE}_{CONF_SERVICE_DATA}"),
    }

    delete_keys = set(
        [f"{CONF_SERVICE}_{CONF_ID}", f"{CONF_SERVICE}_{CONF_SERVICE_DATA}"]
    ).intersection(set(data.keys()))
    for key in delete_keys:
        del data[key]

    # Return info that you want to store in the config entry.
    return {"title": title, "uid": uid, "data": data}


async def _get_service_list(hass: HomeAssistant):
    """Return list of services"""
    services_dict = hass.services.async_services()

    service_list = []

    for provider, services in services_dict.items():
        if isinstance(services, dict):
            for name in services.keys():
                service_list.append(f"{provider}.{name}")
    return service_list


class Rf4ChFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rf4Ch Integration."""

    VERSION = 1

    def __init__(self):
        """Initialize the Rf4Ch config flow."""
        self.discovered_conf = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        info = None

        if user_input is not None:
            try:
                info = await parse_input(self.hass, user_input)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(info["uid"], raise_on_progress=False)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=info["data"])

        services = await _get_service_list(self.hass)

        return self.async_show_form(
            step_id="user",
            data_schema=_data_schema(services),
            errors=errors,
        )

    async def async_step_import(self, import_config: dict):
        """Setup step import for config flow."""
        cfg = import_config
        opts = import_config.pop(CONF_OPTIONS, {})
        device_name = cfg[CONF_NAME]
        title = f"{device_name} Switcher".title()

        await self.async_set_unique_id(cfg[CONF_UNIQUE_ID])
        return self.async_create_entry(title=title, data=cfg, options=opts)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for isy994."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        stateless = options.get(CONF_STATELESS)

        options_schema = vol.Schema(
            {
                vol.Required(CONF_STATELESS, default=stateless): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=options_schema)
