"""Sensor and setup tests."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mutiara_hadith.const import CONF_MODE, DOMAIN, MODE_SCRAPE


async def test_setup_and_sensor(hass: HomeAssistant, mock_site) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_MODE: MODE_SCRAPE})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED

    state = hass.states.get("sensor.mutiara_hadith")
    assert state is not None
    assert state.state == "Kekayaan VS Kesihatan"
    assert state.attributes["status"] == "Sahih"
    assert state.attributes["hadith_id"] == 1061
    assert "JAKIM" in state.attributes["attribution"]

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_retry_when_site_down(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get("https://myhadith.islam.gov.my/", status=503)
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_MODE: MODE_SCRAPE})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.SETUP_RETRY
