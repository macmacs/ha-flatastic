"""Fixtures for Flatastic integration tests."""
from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest


def _setup_ha_mocks():
    """Set up mock modules for homeassistant dependencies."""
    ha_modules = {
        "homeassistant": MagicMock(),
        "homeassistant.config_entries": MagicMock(),
        "homeassistant.const": MagicMock(),
        "homeassistant.core": MagicMock(),
        "homeassistant.data_entry_flow": MagicMock(),
        "homeassistant.exceptions": MagicMock(),
        "homeassistant.helpers": MagicMock(),
        "homeassistant.helpers.aiohttp_client": MagicMock(),
        "homeassistant.helpers.config_validation": MagicMock(),
        "homeassistant.helpers.entity_platform": MagicMock(),
        "homeassistant.helpers.entity_registry": MagicMock(),
        "homeassistant.helpers.update_coordinator": MagicMock(),
        "homeassistant.components": MagicMock(),
        "homeassistant.components.frontend": MagicMock(),
        "homeassistant.components.sensor": MagicMock(),
        "voluptuous": MagicMock(),
    }

    # Make Platform.SENSOR work
    ha_modules["homeassistant.const"].Platform.SENSOR = "sensor"

    # Make UpdateFailed an actual exception class
    class UpdateFailed(Exception):
        pass

    ha_modules["homeassistant.helpers.update_coordinator"].UpdateFailed = UpdateFailed

    # Make DataUpdateCoordinator a proper base class
    class DataUpdateCoordinator:
        def __init__(self, hass, logger, *, name, update_interval):
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval

    ha_modules["homeassistant.helpers.update_coordinator"].DataUpdateCoordinator = DataUpdateCoordinator

    # Make HomeAssistantError an actual exception class
    class HomeAssistantError(Exception):
        pass

    ha_modules["homeassistant.exceptions"].HomeAssistantError = HomeAssistantError

    # Make SensorEntity a real base class that supports _attr_* pattern
    class SensorEntity:
        @property
        def unique_id(self):
            return getattr(self, "_attr_unique_id", None)

        @property
        def name(self):
            return getattr(self, "_attr_name", None)

    ha_modules["homeassistant.components.sensor"].SensorEntity = SensorEntity

    # Make CoordinatorEntity a real base class with coordinator support
    class CoordinatorEntity:
        def __init__(self, coordinator, *args, **kwargs):
            self.coordinator = coordinator

    ha_modules["homeassistant.helpers.update_coordinator"].CoordinatorEntity = CoordinatorEntity

    for mod_name, mod in ha_modules.items():
        sys.modules.setdefault(mod_name, mod)


_setup_ha_mocks()


@pytest.fixture
def mock_api_chores():
    """Return sample chore data from the API."""
    return [
        {
            "id": 100,
            "title": "Dishes",
            "currentUser": 1,
            "users": [1, 2],
            "points": 5,
            "timeLeftNext": -172800,
            "rotationTime": 604800,
            "lastDoneDate": "2025-01-20",
            "creationDate": "2024-06-01",
            "fixed": False,
        },
        {
            "id": 200,
            "title": "Vacuum",
            "currentUser": 2,
            "users": [1, 2],
            "points": 10,
            "timeLeftNext": 43200,
            "rotationTime": 604800,
            "lastDoneDate": "2025-01-24",
            "creationDate": "2024-06-01",
            "fixed": False,
        },
        {
            "id": 300,
            "title": "Trash",
            "currentUser": 1,
            "users": [1, 2],
            "points": 3,
            "timeLeftNext": 259200,
            "rotationTime": 604800,
            "lastDoneDate": "2025-01-23",
            "creationDate": "2024-06-01",
            "fixed": False,
        },
    ]


@pytest.fixture
def mock_api_users():
    """Return sample WG/user data from the API."""
    return {
        "flatmates": [
            {"id": "1", "firstName": "Alice"},
            {"id": "2", "firstName": "Bob"},
        ]
    }


def _make_context_manager(response):
    """Create an async context manager wrapping a response."""
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=response)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


@pytest.fixture
def mock_session(mock_api_chores, mock_api_users):
    """Create a mock aiohttp session."""
    session = MagicMock()

    def mock_get(url, **kwargs):
        response = AsyncMock()
        if "chores" in url:
            response.status = 200
            response.json = AsyncMock(return_value=mock_api_chores)
        elif "wg" in url:
            response.status = 200
            response.json = AsyncMock(return_value=mock_api_users)
        else:
            response.status = 200
            response.json = AsyncMock(return_value={})
        return _make_context_manager(response)

    session.get = mock_get
    return session
