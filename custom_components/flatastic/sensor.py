"""Sensor platform for Flatastic integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FlatasticDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Flatastic sensor based on a config entry."""
    coordinator: FlatasticDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Store the async_add_entities callback for dynamic entity management
    coordinator.async_add_entities = async_add_entities
    coordinator.existing_entities = {}

    entities = []
    
    # Create a sensor for each chore item
    if coordinator.data:
        for idx, chore_data in enumerate(coordinator.data):
            chore_id = chore_data.get("id", idx)
            entity = FlatasticChoreSensor(coordinator, idx, chore_data)
            entities.append(entity)
            coordinator.existing_entities[chore_id] = entity

    async_add_entities(entities)
    
    # Set up listener for data updates to manage entities dynamically
    async def _async_update_entities() -> None:
        """Update entities when coordinator data changes."""
        if not coordinator.data:
            # If no data, remove all existing entities
            entities_to_remove = list(coordinator.existing_entities.keys())
            for chore_id in entities_to_remove:
                entity = coordinator.existing_entities.pop(chore_id)
                await entity.async_remove(force_remove=True)
                _LOGGER.info(f"Removed sensor for deleted chore {chore_id} (no data)")
            return
        
        current_chore_ids = {chore_data.get("id") for chore_data in coordinator.data if chore_data.get("id")}
        existing_chore_ids = set(coordinator.existing_entities.keys())
        
        # Remove entities for chores that no longer exist
        entities_to_remove = existing_chore_ids - current_chore_ids
        for chore_id in entities_to_remove:
            entity = coordinator.existing_entities.pop(chore_id)
            # Force remove the entity from Home Assistant registry
            await entity.async_remove(force_remove=True)
            _LOGGER.info(f"Removed sensor for deleted chore {chore_id}")
        
        # Add entities for new chores
        new_chore_ids = current_chore_ids - existing_chore_ids
        new_entities = []
        
        for idx, chore_data in enumerate(coordinator.data):
            chore_id = chore_data.get("id")
            if chore_id in new_chore_ids:
                entity = FlatasticChoreSensor(coordinator, idx, chore_data)
                new_entities.append(entity)
                coordinator.existing_entities[chore_id] = entity
                _LOGGER.info(f"Added sensor for new chore {chore_id}: {chore_data.get('title', 'Unknown')}")
        
        if new_entities:
            coordinator.async_add_entities(new_entities)

    coordinator.async_add_listener(_async_update_entities)


class FlatasticChoreSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Flatastic chore sensor."""

    def __init__(
        self,
        coordinator: FlatasticDataUpdateCoordinator,
        idx: int,
        chore_data: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._chore_id = chore_data.get("id", idx)
        self._chore_data = chore_data
        
        # Extract title for the sensor name and value
        self._title = chore_data.get("title", f"Chore {idx}")
        
        # Create unique ID based on chore data
        self._attr_unique_id = f"flatastic_chore_{self._chore_id}"
        self._attr_name = f"Flatastic {self._title}"

    def _get_current_chore_data(self) -> dict[str, Any] | None:
        """Get current chore data by ID."""
        if not self.coordinator.data:
            return None
        
        for chore_data in self.coordinator.data:
            if chore_data.get("id") == self._chore_id:
                return chore_data
        return None

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        current_data = self._get_current_chore_data()
        if current_data:
            current_user_id = current_data.get("currentUser")
            if current_user_id:
                return self.coordinator.users_data.get(current_user_id, f"User {current_user_id}")
            return "No assigned user"
        return "Unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        current_data = self._get_current_chore_data()
        if current_data:
            # Return all attributes except title (since that's the value)
            attributes = {}
            for key, value in current_data.items():
                if key != "title":
                    attributes[key] = value
            
            # Add the chore title as an attribute since it's no longer the sensor value
            attributes["title"] = current_data.get("title", self._title)
            
            # Add filterable attributes for Auto Entities card
            attributes["integration"] = "flatastic"
            attributes["chore_type"] = "household"
            
            # Add status based on timeLeftNext for easy filtering
            time_left = current_data.get("timeLeftNext", 0)
            if time_left < 0:
                attributes["status"] = "overdue"
            elif time_left < 86400:  # Less than 1 day
                attributes["status"] = "due_soon"
            else:
                attributes["status"] = "pending"
            
            # Add user-friendly time status
            if time_left < -604800:  # More than 1 week overdue
                attributes["urgency"] = "high"
            elif time_left < 0:  # Overdue but less than 1 week
                attributes["urgency"] = "medium"
            else:
                attributes["urgency"] = "low"
            
            # Add user names for the users assigned to this chore
            user_names = []
            users_list = current_data.get("users", [])
            if isinstance(users_list, list):
                for user_id in users_list:
                    user_name = self.coordinator.users_data.get(user_id, f"User {user_id}")
                    user_names.append({"id": user_id, "name": user_name})
            attributes["user_names"] = user_names
            
            # Add current user name
            current_user_id = current_data.get("currentUser")
            if current_user_id:
                attributes["current_user_name"] = self.coordinator.users_data.get(current_user_id, f"User {current_user_id}")
                
            return attributes
        return {}

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._get_current_chore_data() is not None
        )

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "flatastic_chores")},
            "name": "Flatastic Chores",
            "manufacturer": "Flatastic",
            "model": "Chore Tracker",
        }
