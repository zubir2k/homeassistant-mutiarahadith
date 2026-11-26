"""Diagnostics for MyHadith (JAKIM)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import MyHadithConfigEntry

TO_REDACT: set[str] = set()


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MyHadithConfigEntry
) -> dict[str, Any]:
    coordinator = entry.runtime_data
    return {
        "entry": {
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "last_update_success": coordinator.last_update_success,
        "update_interval": str(coordinator.update_interval),
        "data": coordinator.data.as_dict() if coordinator.data else None,
    }
