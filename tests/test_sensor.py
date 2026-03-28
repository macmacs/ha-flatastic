"""Tests for the Flatastic sensor platform."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.flatastic.sensor import FlatasticChoreSensor


@pytest.fixture
def coordinator_with_data(mock_api_chores):
    """Create a mock coordinator with chore data."""
    coordinator = MagicMock()
    coordinator.data = mock_api_chores
    coordinator.users_data = {1: "Alice", 2: "Bob"}
    coordinator.last_update_success = True
    return coordinator


@pytest.fixture
def overdue_sensor(coordinator_with_data, mock_api_chores):
    """Create a sensor for an overdue chore (Dishes, timeLeftNext=-172800)."""
    return FlatasticChoreSensor(coordinator_with_data, 0, mock_api_chores[0])


@pytest.fixture
def due_soon_sensor(coordinator_with_data, mock_api_chores):
    """Create a sensor for a due-soon chore (Vacuum, timeLeftNext=43200)."""
    return FlatasticChoreSensor(coordinator_with_data, 1, mock_api_chores[1])


@pytest.fixture
def pending_sensor(coordinator_with_data, mock_api_chores):
    """Create a sensor for a pending chore (Trash, timeLeftNext=259200)."""
    return FlatasticChoreSensor(coordinator_with_data, 2, mock_api_chores[2])


class TestFlatasticChoreSensor:
    """Tests for FlatasticChoreSensor."""

    def test_unique_id(self, overdue_sensor):
        """Test unique ID is based on chore ID."""
        assert overdue_sensor.unique_id == "flatastic_chore_100"

    def test_name(self, overdue_sensor):
        """Test sensor name includes chore title."""
        assert overdue_sensor.name == "Flatastic Dishes"

    def test_native_value_shows_assigned_user(self, overdue_sensor):
        """Test state shows current assigned user name."""
        assert overdue_sensor.native_value == "Alice"

    def test_native_value_shows_other_user(self, due_soon_sensor):
        """Test state shows correct user for different chore."""
        assert due_soon_sensor.native_value == "Bob"

    def test_native_value_unknown_user(self, coordinator_with_data, mock_api_chores):
        """Test state shows fallback for unknown user ID."""
        coordinator_with_data.users_data = {}
        sensor = FlatasticChoreSensor(coordinator_with_data, 0, mock_api_chores[0])
        assert sensor.native_value == "User 1"

    def test_native_value_no_current_user(self, coordinator_with_data):
        """Test state when no user is assigned."""
        chore = {"id": 999, "title": "No user chore", "users": []}
        coordinator_with_data.data.append(chore)
        sensor = FlatasticChoreSensor(coordinator_with_data, 3, chore)
        assert sensor.native_value == "No assigned user"

    def test_native_value_no_data(self, coordinator_with_data):
        """Test state returns Unknown when chore data is missing."""
        coordinator_with_data.data = None
        chore = {"id": 888, "title": "Missing"}
        sensor = FlatasticChoreSensor(coordinator_with_data, 0, chore)
        assert sensor.native_value == "Unknown"

    def test_status_overdue(self, overdue_sensor):
        """Test overdue status attribute."""
        attrs = overdue_sensor.extra_state_attributes
        assert attrs["status"] == "overdue"

    def test_status_due_soon(self, due_soon_sensor):
        """Test due_soon status attribute."""
        attrs = due_soon_sensor.extra_state_attributes
        assert attrs["status"] == "due_soon"

    def test_status_pending(self, pending_sensor):
        """Test pending status attribute."""
        attrs = pending_sensor.extra_state_attributes
        assert attrs["status"] == "pending"

    def test_urgency_medium(self, overdue_sensor):
        """Test medium urgency (overdue < 1 week)."""
        attrs = overdue_sensor.extra_state_attributes
        assert attrs["urgency"] == "medium"

    def test_urgency_high(self, coordinator_with_data):
        """Test high urgency (overdue > 1 week)."""
        chore = {
            "id": 400,
            "title": "Very late",
            "currentUser": 1,
            "users": [1],
            "points": 1,
            "timeLeftNext": -700000,
        }
        coordinator_with_data.data.append(chore)
        sensor = FlatasticChoreSensor(coordinator_with_data, 3, chore)
        attrs = sensor.extra_state_attributes
        assert attrs["urgency"] == "high"

    def test_urgency_low(self, pending_sensor):
        """Test low urgency (not overdue)."""
        attrs = pending_sensor.extra_state_attributes
        assert attrs["urgency"] == "low"

    def test_integration_attribute(self, overdue_sensor):
        """Test integration attribute is always flatastic."""
        attrs = overdue_sensor.extra_state_attributes
        assert attrs["integration"] == "flatastic"

    def test_chore_type_attribute(self, overdue_sensor):
        """Test chore_type attribute is always household."""
        attrs = overdue_sensor.extra_state_attributes
        assert attrs["chore_type"] == "household"

    def test_user_names_attribute(self, overdue_sensor):
        """Test user_names contains mapped user names."""
        attrs = overdue_sensor.extra_state_attributes
        assert attrs["user_names"] == [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]

    def test_current_user_name_attribute(self, overdue_sensor):
        """Test current_user_name attribute."""
        attrs = overdue_sensor.extra_state_attributes
        assert attrs["current_user_name"] == "Alice"

    def test_title_in_attributes(self, overdue_sensor):
        """Test chore title is in attributes."""
        attrs = overdue_sensor.extra_state_attributes
        assert attrs["title"] == "Dishes"

    def test_available_when_data_present(self, overdue_sensor):
        """Test sensor is available when data exists."""
        assert overdue_sensor.available is True

    def test_unavailable_when_no_data(self, coordinator_with_data):
        """Test sensor is unavailable when coordinator has no data."""
        chore = {"id": 888, "title": "Gone"}
        sensor = FlatasticChoreSensor(coordinator_with_data, 0, chore)
        coordinator_with_data.data = None
        assert sensor.available is False

    def test_unavailable_when_chore_removed(self, coordinator_with_data):
        """Test sensor is unavailable when its chore is no longer in data."""
        chore = {"id": 999, "title": "Removed"}
        sensor = FlatasticChoreSensor(coordinator_with_data, 0, chore)
        assert sensor.available is False

    def test_device_info(self, overdue_sensor):
        """Test device info is consistent."""
        info = overdue_sensor.device_info
        assert info["name"] == "Flatastic Chores"
        assert info["manufacturer"] == "Flatastic"
        assert ("flatastic", "flatastic_chores") in info["identifiers"]

    def test_empty_attributes_when_no_data(self, coordinator_with_data):
        """Test empty attributes when chore data is missing."""
        coordinator_with_data.data = None
        chore = {"id": 888, "title": "Gone"}
        sensor = FlatasticChoreSensor(coordinator_with_data, 0, chore)
        assert sensor.extra_state_attributes == {}
