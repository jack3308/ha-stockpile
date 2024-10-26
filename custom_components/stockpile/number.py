"""Platform for Stockpile number integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMeasurement
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Stockpile number platform."""
    name = config_entry.data["name"]
    
    async_add_entities(
        [
            StockpileNumber(
                config_entry,
                name,
            )
        ]
    )


class StockpileNumber(NumberEntity):
    """Representation of a Stockpile number."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        name: str,
    ) -> None:
        """Initialize the Stockpile number."""
        self._config_entry = config_entry
        self._attr_name = name
        # Fix the duplicate name in entity_id by using just the name
        self.entity_id = f"number.{name.lower().replace(' ', '_')}"
        self._attr_unique_id = f"{config_entry.entry_id}"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 9999
        self._attr_mode = NumberMode.BOX
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "units"
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name=name,
            manufacturer="Stockpile",
            model="Stock Counter",
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        LOGGER.debug("Setting value to %s", value)
        self._attr_native_value = value
        self.async_write_ha_state()
