"""The Stockpile integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_NAME,
    Platform,
)
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.NUMBER]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Stockpile component."""
    hass.data.setdefault(DOMAIN, {})

    async def expend_stock(service_call: ServiceCall) -> None:
        """Handle the service call."""
        entities = service_call.data.get(ATTR_ENTITY_ID)
        amount = service_call.data.get("amount", 1)

        if not isinstance(entities, list):
            entities = [entities]

        for entity in entities:
            try:
                state = hass.states.get(entity)
                if state is None:
                    _LOGGER.warning("Entity %s not found", entity)
                    continue

                current_value = float(state.state)
                new_value = max(0, current_value - amount)

                await hass.services.async_call(
                    Platform.NUMBER,
                    "set_value",
                    {ATTR_ENTITY_ID: entity, "value": new_value},
                    blocking=True,
                )
            except (ValueError, TypeError) as err:
                _LOGGER.error("Error processing entity %s: %s", entity, str(err))

    hass.services.async_register(DOMAIN, "expend_stock", expend_stock)

    return True

async def async_setup_entry(hass: HomeAssistant, entry: Any) -> bool:
    """Set up Stockpile from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: Any) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
