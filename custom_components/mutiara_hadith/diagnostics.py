"""Diagnostics for MyHadith (JAKIM)."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import MyHadithConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MyHadithConfigEntry
) -> dict[str, Any]:
    coordinator = entry.runtime_data
    return {
        "entry": {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "last_update_success": coordinator.last_update_success,
        "update_interval": str(coordinator.update_interval),
        "data": coordinator.data.as_dict() if coordinator.data else None,
    }
