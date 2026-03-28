"""Tests for the Flatastic data coordinator."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.conftest import _make_context_manager
from custom_components.flatastic.coordinator import FlatasticDataUpdateCoordinator


@pytest.fixture
def coordinator(mock_session):
    """Create a coordinator instance with a mock hass and session."""
    hass = MagicMock()
    coordinator = FlatasticDataUpdateCoordinator(
        hass, mock_session, "test-api-key"
    )
    return coordinator


class TestFlatasticDataUpdateCoordinator:
    """Tests for FlatasticDataUpdateCoordinator."""

    def test_init(self, coordinator):
        """Test coordinator initialises with correct attributes."""
        assert coordinator.api_key == "test-api-key"
        assert coordinator.headers == {"x-api-key": "test-api-key"}
        assert coordinator.users_data == {}

    @pytest.mark.asyncio
    async def test_fetch_users_data(self, coordinator):
        """Test fetching user data from the WG endpoint."""
        users = await coordinator._fetch_users_data()
        assert users == {1: "Alice", 2: "Bob"}

    @pytest.mark.asyncio
    async def test_fetch_users_data_converts_string_ids(self, coordinator):
        """Test that string user IDs are converted to int."""
        users = await coordinator._fetch_users_data()
        for user_id in users:
            assert isinstance(user_id, int)

    @pytest.mark.asyncio
    async def test_fetch_users_data_handles_error(self, coordinator):
        """Test that user fetch errors return empty dict."""
        def failing_get(url, **kwargs):
            raise Exception("Connection error")

        coordinator.session.get = failing_get
        users = await coordinator._fetch_users_data()
        assert users == {}

    @pytest.mark.asyncio
    async def test_fetch_users_data_handles_non_200(self, coordinator):
        """Test that non-200 responses return empty dict."""
        def mock_get(url, **kwargs):
            response = AsyncMock()
            response.status = 500
            return _make_context_manager(response)

        coordinator.session.get = mock_get
        users = await coordinator._fetch_users_data()
        assert users == {}

    @pytest.mark.asyncio
    async def test_fetch_users_data_handles_missing_flatmates(self, coordinator):
        """Test handling of WG response without flatmates key."""
        def mock_get(url, **kwargs):
            response = AsyncMock()
            response.status = 200
            response.json = AsyncMock(return_value={"other_key": "value"})
            return _make_context_manager(response)

        coordinator.session.get = mock_get
        users = await coordinator._fetch_users_data()
        assert users == {}

    @pytest.mark.asyncio
    async def test_complete_chore_success(self, coordinator):
        """Test successful chore completion."""
        coordinator.async_request_refresh = AsyncMock()

        def mock_get(url, **kwargs):
            response = AsyncMock()
            response.status = 200
            return _make_context_manager(response)

        coordinator.session.get = mock_get
        result = await coordinator.complete_chore(100, 1)
        assert result is True
        coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_complete_chore_unauthorized(self, coordinator):
        """Test chore completion with invalid API key."""
        def mock_get(url, **kwargs):
            response = AsyncMock()
            response.status = 401
            return _make_context_manager(response)

        coordinator.session.get = mock_get
        result = await coordinator.complete_chore(100, 1)
        assert result is False

    @pytest.mark.asyncio
    async def test_complete_chore_server_error(self, coordinator):
        """Test chore completion with server error."""
        def mock_get(url, **kwargs):
            response = AsyncMock()
            response.status = 500
            return _make_context_manager(response)

        coordinator.session.get = mock_get
        result = await coordinator.complete_chore(100, 1)
        assert result is False

    @pytest.mark.asyncio
    async def test_complete_chore_connection_error(self, coordinator):
        """Test chore completion with connection error."""
        import aiohttp

        def mock_get(url, **kwargs):
            raise aiohttp.ClientError("Connection refused")

        coordinator.session.get = mock_get
        result = await coordinator.complete_chore(100, 1)
        assert result is False
