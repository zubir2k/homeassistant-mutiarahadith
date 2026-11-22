"""Config flow for MyHadith (JAKIM)."""
from __future__ import annotations

from collections.abc import Mapping
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
    SelectSelector,
    SelectSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .client import ApiBackend, MyHadithAuthError, MyHadithError, ScrapeBackend
from .const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_SCAN_HOURS,
    DEFAULT_SCAN_HOURS,
    DOMAIN,
    MAX_SCAN_HOURS,
    MIN_SCAN_HOURS,
    MODE_API,
    MODE_SCRAPE,
)

SOURCE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MODE, default=MODE_SCRAPE): SelectSelector(
            SelectSelectorConfig(options=[MODE_SCRAPE, MODE_API], translation_key="mode")
        ),
        vol.Optional(CONF_API_KEY): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)
API_KEY_SCHEMA = vol.Schema(
    {vol.Required(CONF_API_KEY): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))}
)


class MyHadithConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up MyHadith."""

    VERSION = 1

    async def _async_validate(self, user_input: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
        """Test the chosen source. Returns (entry data, errors)."""
        session = async_get_clientsession(self.hass)
        mode = user_input.get(CONF_MODE, MODE_SCRAPE)
        errors: dict[str, str] = {}
        data: dict[str, Any] = {CONF_MODE: mode}
        try:
            if mode == MODE_API:
                api_key = (user_input.get(CONF_API_KEY) or "").strip()
                if not api_key:
                    errors[CONF_API_KEY] = "api_key_required"
                    return data, errors
                await ApiBackend(session, api_key).async_validate()
                data[CONF_API_KEY] = api_key
            else:
                await ScrapeBackend(session).async_get_featured()
        except MyHadithAuthError:
            errors["base"] = "invalid_auth"
        except MyHadithError:
            errors["base"] = "cannot_connect"
        return data, errors

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            data, errors = await self._async_validate(user_input)
            if not errors:
                return self.async_create_entry(title="Mutiara Hadith", data=data)
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(SOURCE_SCHEMA, user_input),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Switch between scrape and API mode, e.g. once JAKIM issues a key."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            data, errors = await self._async_validate(user_input)
            if not errors:
                return self.async_update_reload_and_abort(entry, data=data)
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                SOURCE_SCHEMA, user_input or {CONF_MODE: entry.data.get(CONF_MODE, MODE_SCRAPE)}
            ),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            data, errors = await self._async_validate({CONF_MODE: MODE_API, **user_input})
            if not errors:
                return self.async_update_reload_and_abort(self._get_reauth_entry(), data=data)
        return self.async_show_form(
            step_id="reauth_confirm", data_schema=API_KEY_SCHEMA, errors=errors
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
