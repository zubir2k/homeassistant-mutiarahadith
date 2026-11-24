"""Mutiara Hadith (JAKIM) integration."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .client import ScrapeBackend
from .const import (
    CONF_SCAN_HOURS,
    CARD_FILENAME,
    DEFAULT_SCAN_HOURS,
    DOMAIN,
    FRONTEND_URL,
    VERSION,
)
from .coordinator import MyHadithCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type MyHadithConfigEntry = ConfigEntry[MyHadithCoordinator]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Serve the bundled Lovelace card and load it on every dashboard."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(Path(__file__).parent / "frontend"), True)]
    )
    add_extra_js_url(hass, f"{FRONTEND_URL}/{CARD_FILENAME}?v={VERSION}")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: MyHadithConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    backend = ScrapeBackend(session)
    hours = entry.options.get(CONF_SCAN_HOURS, DEFAULT_SCAN_HOURS)
    coordinator = MyHadithCoordinator(hass, entry, backend, timedelta(hours=hours))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: MyHadithConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: MyHadithConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
