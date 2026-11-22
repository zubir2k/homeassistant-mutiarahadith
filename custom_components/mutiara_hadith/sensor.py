"""Mutiara Hadith sensor."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MyHadithConfigEntry
from .const import ATTRIBUTION, BASE_URL, DOMAIN, STATE_MAX_LEN
from .coordinator import MyHadithCoordinator

# The coordinator does all the fetching.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MyHadithConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([MutiaraHadithSensor(entry.runtime_data)])


class MutiaraHadithSensor(CoordinatorEntity[MyHadithCoordinator], SensorEntity):
    """The hadith JAKIM currently features on MyHadith."""

    _attr_has_entity_name = True
    _attr_translation_key = "mutiara_hadith"
    # Main feature of the device: entity takes the device name (sensor.mutiara_hadith).
    _attr_name = None
    _attr_attribution = ATTRIBUTION
    # Long text stays out of the recorder database.
    _unrecorded_attributes = frozenset({"matan", "maksud", "penghayatan", "sumber_rujukan"})

    def __init__(self, coordinator: MyHadithCoordinator) -> None:
        super().__init__(coordinator)
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_mutiara_hadith"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Mutiara Hadith",
            manufacturer="JAKIM",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=BASE_URL,
        )

    @property
    def native_value(self) -> str:
        return self.coordinator.data.title[:STATE_MAX_LEN]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data.as_dict()
        data.pop("title", None)
        return data
