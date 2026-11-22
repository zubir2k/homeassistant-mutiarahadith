"""Diagnostics tests."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mutiara_hadith.const import CONF_API_KEY, CONF_MODE, DOMAIN, MODE_SCRAPE
from custom_components.mutiara_hadith.diagnostics import async_get_config_entry_diagnostics


async def test_diagnostics(hass: HomeAssistant, mock_site) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_MODE: MODE_SCRAPE, CONF_API_KEY: "secret_token"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    diag = await async_get_config_entry_diagnostics(hass, entry)
    assert diag["entry"]["data"][CONF_API_KEY] == "**REDACTED**"
    assert diag["last_update_success"] is True
    assert diag["data"]["hadith_id"] == 1061
    assert diag["data"]["title"] == "Kekayaan VS Kesihatan"
