"""The Stockpile integration."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers import entity_platform

from .const import (
    DOMAIN, 
    SERVICE_EXPEND_STOCK, 
    LOGGER,
    VERSION
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

    @callback
    async def expend_stock(call: ServiceCall) -> None:
        """Handle the service call."""
        LOGGER.debug("Service call received: %s", call)
        
        quantity = float(call.data.get("quantity", 0))
        if quantity <= 0:
            raise ServiceValidationError(
                "Quantity must be greater than 0",
                translation_domain=DOMAIN,
                translation_key="invalid_quantity",
            )

        entity_reg = er.async_get(hass)
        device_reg = dr.async_get(hass)
        
        # Get all target entities
        target_entities = []
        
        # Handle entity targets
        if "entity_id" in call.data:
            target_entities.extend(call.data["entity_id"])
            
        # Handle device targets
        if "device_id" in call.data:
            for device_id in call.data["device_id"]:
                # Get all entities for this device
                device_entities = er.async_entries_for_device(
                    entity_reg,
                    device_id,
                    include_disabled_entities=False,
                )
                # Only include number entities from our integration
                target_entities.extend(
                    entity.entity_id
                    for entity in device_entities
                    if entity.domain == Platform.NUMBER
                    and entity.platform == DOMAIN
                )

        if not target_entities:
            raise ServiceValidationError(
                "No valid targets specified",
                translation_domain=DOMAIN,
                translation_key="no_target",
            )

        # Process each entity
        for entity_id in target_entities:
            state = hass.states.get(entity_id)
            if not state:
                raise ServiceValidationError(
                    f"Entity {entity_id} not found",
                    translation_domain=DOMAIN,
                    translation_key="entity_not_found",
                )

            try:
                current_value = float(state.state)
                new_value = current_value - quantity
                if new_value < 0:
                    raise ServiceValidationError(
                        f"Cannot expend {quantity} from {current_value} in {entity_id}",
                        translation_domain=DOMAIN,
                        translation_key="insufficient_stock",
                    )
                
                await hass.services.async_call(
                    Platform.NUMBER,
                    "set_value",
                    {"entity_id": entity_id, "value": new_value},
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
