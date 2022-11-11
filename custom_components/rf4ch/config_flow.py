"""Config flow to configure Rf 4 Channel Integration."""

from homeassistant import config_entries
from homeassistant.const import CONF_FRIENDLY_NAME, CONF_NAME

from .const import DOMAIN


class FirmataFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Rf4Ch config flow."""

    VERSION = 1

    async def async_step_import(self, import_config: dict):
        """Setup step import for config flow."""

        fallback_name = import_config[CONF_NAME]
        device_name = import_config.get(CONF_FRIENDLY_NAME, fallback_name)
        title = f"{device_name} Switcher".title()

        return self.async_create_entry(title=title, data=import_config)
