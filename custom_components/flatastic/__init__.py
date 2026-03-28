"""The Flatastic integration."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .cleanup_service import async_setup_cleanup_service
from .const import DOMAIN, SERVICE_COMPLETE_CHORE
from .coordinator import FlatasticDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Service schema
COMPLETE_CHORE_SCHEMA = vol.Schema(
    {
        vol.Required("chore_id"): cv.positive_int,
        vol.Required("completed_by"): cv.positive_int,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Flatastic from a config entry."""
    session = async_get_clientsession(hass)

    coordinator = FlatasticDataUpdateCoordinator(
        hass,
        session,
        entry.data["api_key"],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register service
    async def handle_complete_chore(call: ServiceCall) -> None:
        """Handle the complete chore service call."""
        chore_id = call.data["chore_id"]
        completed_by = call.data["completed_by"]

        # Get the first coordinator (assuming single config entry for now)
        coordinators = list(hass.data[DOMAIN].values())
        if coordinators:
            coordinator = coordinators[0]
            success = await coordinator.complete_chore(chore_id, completed_by)
            if success:
                _LOGGER.info("Successfully completed chore %s for user %s", chore_id, completed_by)
            else:
                _LOGGER.error("Failed to complete chore %s for user %s", chore_id, completed_by)

    hass.services.async_register(
        DOMAIN,
        SERVICE_COMPLETE_CHORE,
        handle_complete_chore,
        schema=COMPLETE_CHORE_SCHEMA,
    )

    # Register cleanup service
    await async_setup_cleanup_service(hass)

    # Register frontend resources
    add_extra_js_url(hass, f"/hacsfiles/{DOMAIN}/flatastic-chores-card.js")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

        # Remove service if no more config entries
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_COMPLETE_CHORE)

    return unload_ok
