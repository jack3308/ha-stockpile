"""The Stockpile integration."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError

from .const import (
    DOMAIN, 
    SERVICE_EXPEND_STOCK, 
    LOGGER,
    VERSION  # Add this import
)
PLATFORMS: list[Platform] = [Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Stockpile from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "version": VERSION,
        "title": entry.title
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def expend_stock(call: ServiceCall) -> None:
        """Handle the service call."""
        LOGGER.debug("Service call received: %s", call)
        
        # The entity_id is in the service call data
        entity = call.data.get("entity_id")
        if not entity:
            raise ServiceValidationError(
                "No target entity specified",
                translation_domain=DOMAIN,
                translation_key="no_target",
            )
        
        quantity = call.data["quantity"]
        LOGGER.debug("Processing expend_stock: entity=%s, quantity=%s", entity, quantity)
        
        state = hass.states.get(entity)
        if not state:
            raise ServiceValidationError(
                f"Entity {entity} not found",
                translation_domain=DOMAIN,
                translation_key="entity_not_found",
            )

        try:
            current_value = float(state.state)
            new_value = current_value - quantity
            if new_value < 0:
                raise ServiceValidationError(
                    f"Cannot expend {quantity} from {current_value}",
                    translation_domain=DOMAIN,
                    translation_key="insufficient_stock",
                )
            
            await hass.services.async_call(
                Platform.NUMBER,
                "set_value",
                {"entity_id": entity, "value": new_value},
                blocking=True,
            )
        except ValueError as ex:
            raise ServiceValidationError(str(ex)) from ex

    hass.services.async_register(
        DOMAIN,
        SERVICE_EXPEND_STOCK,
        expend_stock,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.services.async_remove(DOMAIN, SERVICE_EXPEND_STOCK)

    return unload_ok