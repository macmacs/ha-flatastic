# Flatastic Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant integration for monitoring Flatastic chores.

## Features

- 🏠 Fetches chore data from the Flatastic API
- 📊 Creates individual sensors for each chore
- 🔄 Automatic updates every 15 minutes
- 📋 Each sensor shows the current assigned user name as its state value
- 📝 All chore attributes available as sensor attributes
- 🎯 Filterable attributes for use with Auto Entities card
- 🚨 Custom Lovelace card for interactive chore management
- 🔧 Services for completing chores and cleaning up orphaned entities

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

1. Go to Configuration > Integrations in Home Assistant
2. Click "Add Integration"
3. Search for "Flatastic"
4. Enter your Flatastic API key
5. Click "Submit"

## API Key

You'll need a Flatastic API key to use this integration. The API key should be obtained from your Flatastic account or by contacting Flatastic support.

## Sensors

The integration creates one sensor for each chore returned by the Flatastic API. Each sensor:

- Has a unique ID based on the chore ID
- Shows the current assigned user name as its state value
- Contains all chore data as attributes (title, id, details, users, points, rotationTime, currentUser, lastDoneDate, creationDate, fixed, timeLeftNext)
- Includes additional filterable attributes for use with Auto Entities card

### Filterable Attributes

The integration adds several attributes specifically designed for filtering with the Auto Entities card:

- **`integration`**: Always set to "flatastic" for easy filtering
- **`chore_type`**: Always set to "household" for categorization
- **`status`**: Dynamic status based on due date
  - `overdue`: Task is past due (timeLeftNext < 0)
  - `due_soon`: Task is due within 24 hours (0 ≤ timeLeftNext < 86400)
  - `pending`: Task is not due yet (timeLeftNext ≥ 86400)
- **`urgency`**: Priority level for task completion
  - `high`: More than 1 week overdue
  - `medium`: Overdue but less than 1 week
  - `low`: Not overdue

### Example Auto Entities Configuration

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
  exclude: []
sort:
  method: attribute
  attribute: timeLeftNext
```

## Services

The integration provides services for chore management:

### `flatastic.complete_chore`

Marks a chore as completed by a specific user.

**Parameters:**
- `chore_id` (required): The ID of the chore to complete
- `completed_by` (required): The user ID who completed the chore

**Example:**
```yaml
service: flatastic.complete_chore
data:
  chore_id: 3431881
  completed_by: 1665048
```

### `flatastic.cleanup_orphaned_entities`

Remove sensor entities for chores that no longer exist in Flatastic. This service helps clean up "unavailable" sensors that remain after chores are deleted from the Flatastic app.

**Parameters:** None

## Custom Card

The integration includes a custom Lovelace card that displays overdue chores with buttons to complete them.

### Installation

The custom card is automatically available after installing the integration. Add it to your dashboard:

```yaml
type: custom:flatastic-chores-card
```

### Features

- 🚨 Shows only overdue chores automatically
- 🎯 Color-coded urgency levels (high: red, medium: orange)
- ⏰ Displays how long each chore is overdue
- 👥 Shows completion buttons for each user assigned to the chore
- 🔘 One-click completion with user names (no generic "Complete" button)
- 🎉 Shows celebration message when no chores are overdue
- 📱 Responsive design that works on mobile and desktop

### Card Configuration

The card works automatically without configuration, but you can customize it:

```yaml
type: custom:flatastic-chores-card
title: "My Overdue Tasks"  # Optional custom title
```

## Entity Cleanup

When chores are deleted from Flatastic, the integration automatically removes the corresponding sensor entities. However, in some cases, orphaned entities may remain as "unavailable" with `restored: true`. 

To address this issue:

1. **Automatic Cleanup**: The integration includes enhanced logic to force-remove entities when chores are deleted
2. **Manual Cleanup**: Use the `flatastic.cleanup_orphaned_entities` service to manually clean up any remaining orphaned entities
3. **Automated Cleanup**: Set up an automation to regularly run the cleanup service (see examples folder)

### Example Automation

```yaml
- id: flatastic_cleanup_orphaned_entities
  alias: "Flatastic: Cleanup Orphaned Entities"
  description: "Regularly clean up sensor entities for chores that no longer exist in Flatastic"
  trigger:
    - platform: time
      at: "03:00:00"  # Daily at 3 AM
  action:
    - service: flatastic.cleanup_orphaned_entities
      data: {}
```

See `custom_components/flatastic/examples/cleanup_automation.yaml` for more automation examples.

## Support

For issues and feature requests, please use the [repository's issue tracker](https://codeberg.org/thegroove/ha-flatastic/issues).

## License

This project is licensed under the MIT License.
