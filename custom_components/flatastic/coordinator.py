"""DataUpdateCoordinator for Flatastic."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_CHORES_ENDPOINT, API_COMPLETE_CHORE_ENDPOINT, API_WG_ENDPOINT, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class FlatasticDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Flatastic API."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        api_key: str,
    ) -> None:
        """Initialize."""
        self.session = session
        self.api_key = api_key
        self.headers = {"x-api-key": api_key}
        self.users_data = {}

        super().__init__(
            hass,
            _LOGGER,
            name="Flatastic",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _fetch_users_data(self) -> dict[int, str]:
        """Fetch user data from WG endpoint."""
        try:
            async with self.session.get(
                API_WG_ENDPOINT, headers=self.headers
            ) as response:
                if response.status == 200:
                    wg_data = await response.json()
                    users = {}
                    # Extract users from WG data - the API returns "flatmates" not "users"
                    if isinstance(wg_data, dict) and "flatmates" in wg_data:
                        for user in wg_data["flatmates"]:
                            if isinstance(user, dict) and "id" in user and "firstName" in user:
                                # Convert string ID to int for consistency
                                user_id = int(user["id"])
                                users[user_id] = user["firstName"]
                    return users
                else:
                    _LOGGER.warning("Failed to fetch users data: %s", response.status)
                    return {}
        except Exception as err:
            _LOGGER.warning("Error fetching users data: %s", err)
            return {}

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Update data via library."""
        try:
            # Fetch users data first
            self.users_data = await self._fetch_users_data()

            async with self.session.get(
                API_CHORES_ENDPOINT, headers=self.headers
            ) as response:
                if response.status == 401:
                    raise UpdateFailed("Invalid API key")
                elif response.status != 200:
                    raise UpdateFailed(f"API returned status {response.status}")

                data = await response.json()

                # Ensure we return a list
                if not isinstance(data, list):
                    raise UpdateFailed("API did not return a list")

                return data

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def complete_chore(self, chore_id: int, completed_by: int) -> bool:
        """Complete a chore for a specific user."""
        try:
            params = {
                "id": chore_id,
                "completedBy": completed_by
            }

            async with self.session.get(
                API_COMPLETE_CHORE_ENDPOINT,
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 401:
                    _LOGGER.error("Invalid API key when completing chore")
                    return False
                elif response.status != 200:
                    _LOGGER.error("API returned status %s when completing chore", response.status)
                    return False

                # Trigger a data refresh after completing a chore
                await self.async_request_refresh()
                return True

        except aiohttp.ClientError as err:
            _LOGGER.error("Error completing chore: %s", err)
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error completing chore: %s", err)
            return False
