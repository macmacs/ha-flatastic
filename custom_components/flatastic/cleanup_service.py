"""Cleanup service for Flatastic integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_cleanup_orphaned_entities(hass: HomeAssistant, call: ServiceCall) -> None:
    """Clean up orphaned Flatastic entities that no longer exist in the API."""
    entity_registry = er.async_get(hass)
    
    # Get all Flatastic entities from the registry
    flatastic_entities = [
        entity for entity in entity_registry.entities.values()
        if entity.platform == DOMAIN
    ]
    
    if not flatastic_entities:
        _LOGGER.info("No Flatastic entities found in registry")
        return
    
    # Get the coordinator to check current data
    config_entries = hass.config_entries.async_entries(DOMAIN)
    if not config_entries:
        _LOGGER.warning("No Flatastic config entries found")
        return
    
    removed_count = 0
    
    for config_entry in config_entries:
        coordinator = hass.data[DOMAIN].get(config_entry.entry_id)
        if not coordinator:
            continue
            
        # Get current chore IDs from API data
        current_chore_ids = set()
        if coordinator.data:
            current_chore_ids = {
                str(chore_data.get("id")) for chore_data in coordinator.data 
                if chore_data.get("id") is not None
            }
        
        # Check each entity in the registry
        for entity in flatastic_entities:
            if entity.config_entry_id != config_entry.entry_id:
                continue
                
            # Extract chore ID from unique_id
            if entity.unique_id and entity.unique_id.startswith("flatastic_chore_"):
                chore_id = entity.unique_id.replace("flatastic_chore_", "")
                
                # If this chore no longer exists in the API data, remove the entity
                if chore_id not in current_chore_ids:
                    _LOGGER.info(f"Removing orphaned entity: {entity.entity_id} (chore_id: {chore_id})")
                    entity_registry.async_remove(entity.entity_id)
                    removed_count += 1
    
    _LOGGER.info(f"Cleanup completed. Removed {removed_count} orphaned entities.")


async def async_setup_cleanup_service(hass: HomeAssistant) -> None:
    """Set up the cleanup service."""
    hass.services.async_register(
        DOMAIN,
        "cleanup_orphaned_entities",
        async_cleanup_orphaned_entities,
        schema=None,
    )
    _LOGGER.info("Flatastic cleanup service registered")
