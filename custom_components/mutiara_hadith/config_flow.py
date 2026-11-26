"""Config flow for MyHadith (JAKIM)."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .client import MyHadithError, ScrapeBackend
from .const import (
    CONF_SCAN_HOURS,
    DEFAULT_SCAN_HOURS,
    DOMAIN,
    MAX_SCAN_HOURS,
    MIN_SCAN_HOURS,
)


class MyHadithConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up MyHadith."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                await ScrapeBackend(session).async_get_featured()
                return self.async_create_entry(title="Mutiara Hadith", data={})
            except MyHadithError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return MyHadithOptionsFlow()


class MyHadithOptionsFlow(OptionsFlow):
    """Refresh interval."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data={CONF_SCAN_HOURS: int(user_input[CONF_SCAN_HOURS])})
        current = self.config_entry.options.get(CONF_SCAN_HOURS, DEFAULT_SCAN_HOURS)
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_HOURS, default=current): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_HOURS,
                        max=MAX_SCAN_HOURS,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="h",
                    )
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
