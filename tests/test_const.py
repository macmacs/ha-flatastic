"""Tests for the Flatastic constants."""
from custom_components.flatastic.const import (
    API_BASE_URL,
    API_CHORES_ENDPOINT,
    API_COMPLETE_CHORE_ENDPOINT,
    API_USER_ENDPOINT,
    API_WG_ENDPOINT,
    CONF_API_KEY,
    DOMAIN,
    SERVICE_COMPLETE_CHORE,
    UPDATE_INTERVAL,
)


def test_domain():
    """Test domain constant."""
    assert DOMAIN == "flatastic"


def test_api_base_url():
    """Test API base URL."""
    assert API_BASE_URL == "https://api.flatastic-app.com/index.php/api"


def test_api_endpoints_use_base_url():
    """Test all API endpoints are derived from the base URL."""
    assert API_CHORES_ENDPOINT.startswith(API_BASE_URL)
    assert API_COMPLETE_CHORE_ENDPOINT.startswith(API_BASE_URL)
    assert API_WG_ENDPOINT.startswith(API_BASE_URL)
    assert API_USER_ENDPOINT.startswith(API_BASE_URL)


def test_update_interval():
    """Test update interval is 15 minutes in seconds."""
    assert UPDATE_INTERVAL == 900


def test_conf_api_key():
    """Test API key config constant."""
    assert CONF_API_KEY == "api_key"


def test_service_name():
    """Test service name constant."""
    assert SERVICE_COMPLETE_CHORE == "complete_chore"
