"""Config flow tests."""
from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mutiara_hadith.const import (
    CONF_API_KEY,
    CONF_MODE,
    CONF_SCAN_HOURS,
    DOMAIN,
    MODE_API,
    MODE_SCRAPE,
)

API_URL = "https://myhadith.islam.gov.my/api/hadith"


async def test_user_scrape(hass: HomeAssistant, mock_site) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODE: MODE_SCRAPE}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_MODE: MODE_SCRAPE}


async def test_user_cannot_connect(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get("https://myhadith.islam.gov.my/", status=500)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODE: MODE_SCRAPE}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_api_needs_key(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODE: MODE_API}
    )
    assert result["errors"] == {CONF_API_KEY: "api_key_required"}


async def test_user_api_invalid_key(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(API_URL, status=401, json={"status": "error"})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODE: MODE_API, CONF_API_KEY: "bad"}
    )
    assert result["errors"] == {"base": "invalid_auth"}


async def test_single_instance(hass: HomeAssistant) -> None:
    MockConfigEntry(domain=DOMAIN, data={CONF_MODE: MODE_SCRAPE}).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_reconfigure_to_api(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(API_URL, json={"status": "ok"})
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_MODE: MODE_SCRAPE})
    entry.add_to_hass(hass)
    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MODE: MODE_API, CONF_API_KEY: "good"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data == {CONF_MODE: MODE_API, CONF_API_KEY: "good"}


async def test_options_flow(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_MODE: MODE_SCRAPE})
    entry.add_to_hass(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={CONF_SCAN_HOURS: 12}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {CONF_SCAN_HOURS: 12}
