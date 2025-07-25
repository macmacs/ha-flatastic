"""Constants for the Flatastic integration."""

DOMAIN = "flatastic"
VERSION = "0.0.1"

# API Configuration
API_BASE_URL = "https://api.flatastic-app.com/index.php/api"
API_CHORES_ENDPOINT = f"{API_BASE_URL}/chores"
API_COMPLETE_CHORE_ENDPOINT = f"{API_BASE_URL}/chores/next"
API_WG_ENDPOINT = f"{API_BASE_URL}/wg"
API_USER_ENDPOINT = f"{API_BASE_URL}/user"

# Update intervals
UPDATE_INTERVAL = 900  # 15 minutes

# Configuration keys
CONF_API_KEY = "api_key"

# Services
SERVICE_COMPLETE_CHORE = "complete_chore"
