# Flatastic Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant custom integration for the [Flatastic](https://www.flatastic-app.com/) chore management app. It creates sensors for each chore, provides services to complete chores, and includes a custom Lovelace card for interactive management.

## Features

- Fetches chore data from the Flatastic API
- Creates individual sensors for each chore
- Automatic updates every 15 minutes
- Each sensor shows the current assigned user name as its state value
- All chore attributes available as sensor attributes
- Filterable attributes for use with Auto Entities card
- Custom Lovelace card for interactive chore management
- Services for completing chores and cleaning up orphaned entities

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://codeberg.org/thegroove/ha-flatastic`
6. Select "Integration" as the category
7. Click "Add"
8. Find "Flatastic" in the integration list and install it
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/flatastic` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings > Devices & Services** in Home Assistant
2. Click "Add Integration"
3. Search for "Flatastic"
4. Enter your Flatastic API key
5. Click "Submit"

### API Key

You need a Flatastic API key to use this integration. The API key can be obtained from your Flatastic account or by contacting Flatastic support.

## Sensors

The integration creates one sensor per chore. Each sensor:

- Has a unique ID based on the chore ID
- Shows the current assigned user name as its state value
- Contains all chore data as attributes (title, id, details, users, points, rotationTime, currentUser, lastDoneDate, creationDate, fixed, timeLeftNext)
- Includes filterable attributes for use with Auto Entities card
- Is automatically added/removed when chores change in Flatastic

### Filterable Attributes

The integration adds several attributes designed for filtering with the Auto Entities card:

| Attribute    | Values                                      | Description                          |
|-------------|----------------------------------------------|--------------------------------------|
| `integration` | `flatastic`                                | Always set, for easy filtering       |
| `chore_type`  | `household`                                | Always set, for categorization       |
| `status`      | `overdue`, `due_soon`, `pending`           | Based on `timeLeftNext`              |
| `urgency`     | `high`, `medium`, `low`                    | Based on how far overdue             |

Status thresholds:
- `overdue`: `timeLeftNext < 0`
- `due_soon`: `0 <= timeLeftNext < 86400` (within 24 hours)
- `pending`: `timeLeftNext >= 86400`

Urgency thresholds:
- `high`: more than 1 week overdue
- `medium`: overdue but less than 1 week
- `low`: not overdue

### Auto Entities Example

```yaml
type: custom:auto-entities
card:
  type: entities
  title: Overdue Chores
filter:
  include:
    - attributes:
        integration: flatastic
        status: overdue
sort:
  method: attribute
  attribute: timeLeftNext
```

## Services

### `flatastic.complete_chore`

Marks a chore as completed by a specific user.

| Parameter     | Type | Required | Description                        |
|--------------|------|----------|------------------------------------|
| `chore_id`    | int  | yes      | The ID of the chore to complete    |
| `completed_by`| int  | yes      | The user ID who completed the chore|

```yaml
service: flatastic.complete_chore
data:
  chore_id: 3431881
  completed_by: 1665048
```

### `flatastic.cleanup_orphaned_entities`

Removes sensor entities for chores that no longer exist in Flatastic. Useful for cleaning up "unavailable" sensors that remain after chores are deleted.

No parameters required.

## Custom Card

The integration includes a custom Lovelace card that displays overdue chores with completion buttons. It is automatically available after installation.

```yaml
type: custom:flatastic-chores-card
```

Features:
- Shows only overdue chores
- Color-coded urgency levels (high: red, medium: orange)
- Displays how long each chore is overdue
- Completion buttons per user
- Celebration message when no chores are overdue

Optional configuration:

```yaml
type: custom:flatastic-chores-card
title: "My Overdue Tasks"
```

## Entity Cleanup

When chores are deleted from Flatastic, the integration automatically removes the corresponding sensors. If orphaned entities remain:

1. **Manual**: Call the `flatastic.cleanup_orphaned_entities` service
2. **Automated**: Set up a daily automation (see `custom_components/flatastic/examples/cleanup_automation.yaml`)

```yaml
- id: flatastic_cleanup_orphaned_entities
  alias: "Flatastic: Cleanup Orphaned Entities"
  trigger:
    - platform: time
      at: "03:00:00"
  action:
    - service: flatastic.cleanup_orphaned_entities
      data: {}
```

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Running Tests

```bash
uv run --with pytest --with pytest-asyncio --with aiohttp pytest tests/ -v
```

### Linting

```bash
uv run --with ruff ruff check custom_components/flatastic/
```

### Project Structure

```
custom_components/flatastic/
  __init__.py          # Integration entry point, service registration
  config_flow.py       # UI-based configuration flow
  coordinator.py       # Data update coordinator (API communication)
  sensor.py            # Sensor platform (entity management)
  cleanup_service.py   # Orphaned entity cleanup service
  const.py             # Constants and API endpoints
  manifest.json        # Integration metadata
  services.yaml        # Service definitions
  strings.json         # UI strings
  translations/        # Translations (en, de)
  www/                 # Custom Lovelace card
  examples/            # Example automations and dashboards
tests/                 # Test suite
```

## Support

For issues and feature requests, use the [issue tracker](https://codeberg.org/thegroove/ha-flatastic/issues).

## License

MIT License
