"""The bundled Lovelace card is served and auto-loaded."""
from __future__ import annotations

from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.mutiara_hadith.const import (
    CARD_FILENAME,
    DOMAIN,
    FRONTEND_URL,
    VERSION,
)


async def test_card_registered(hass: HomeAssistant, hass_client) -> None:
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    url = f"{FRONTEND_URL}/{CARD_FILENAME}?v={VERSION}"
    assert url in hass.data[DATA_EXTRA_MODULE_URL].urls

    client = await hass_client()
    resp = await client.get(f"{FRONTEND_URL}/{CARD_FILENAME}")
    assert resp.status == 200
    assert "mutiara-hadith-card" in await resp.text()
