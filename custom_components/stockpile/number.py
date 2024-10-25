"""Number platform for Stockpile."""
from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    RestoreNumber,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    CONF_PILE_OF,
    CONF_PILE_SIZE,
    CONF_STEP_SIZE,
    DOMAIN,
    VERSION,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Stockpile number platform."""
    async_add_entities(
        [
            StockpileNumber(
                entry.data[CONF_PILE_OF],
                entry.data[CONF_PILE_SIZE],
                entry.data[CONF_STEP_SIZE],
                entry.entry_id,
            )
        ]
    )


class StockpileNumber(RestoreNumber, NumberEntity):
    """Representation of a Stockpile number."""

    def __init__(
        self,
        name: str,
        initial_value: float,
        step: float,
        entry_id: str,
    ) -> None:
        """Initialize the number."""
        self._attr_unique_id = f"{entry_id}"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 9999999
        self._attr_native_step = step
        self._attr_native_value = initial_value
        self._attr_name = name
        self._attr_has_entity_name = True
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": name,
            "manufacturer": "Home Assistant Community",
            "model": "Stockpile Integration",
            "sw_version": VERSION,
        }

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            try:
                self._attr_native_value = float(last_state.state)
            except ValueError:
                self._attr_native_value = 0

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        self.async_write_ha_state()
