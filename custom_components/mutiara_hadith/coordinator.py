"""Coordinator for MyHadith (JAKIM)."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import ApiBackend, Hadith, MyHadithAuthError, MyHadithError, ScrapeBackend
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MyHadithCoordinator(DataUpdateCoordinator[Hadith]):
    """Fetches the featured Mutiara Hadith."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        backend: ScrapeBackend | ApiBackend,
        interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=interval,
        )
        self.backend = backend

    async def _async_update_data(self) -> Hadith:
        try:
            return await self.backend.async_get_featured()
        except MyHadithAuthError as err:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN, translation_key="invalid_auth"
            ) from err
        except MyHadithError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                translation_placeholders={"error": str(err)},
            ) from err
