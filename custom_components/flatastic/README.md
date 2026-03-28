# Flatastic Home Assistant Integration

This integration allows you to monitor your Flatastic chores in Home Assistant.

## Features

- Fetches chore data from the Flatastic API
- Creates individual sensors for each chore
- Each sensor shows the current assigned user name as its state value
- All other chore attributes are available as sensor attributes
- Automatic updates every 15 minutes

## Installation

### Via HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Add"
7. Find "Flatastic" in the integration list and install it
8. Restart Home Assistant

### Manual Installation

1. Copy the `flatastic` folder to your `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click "Add Integration"
5. Search for "Flatastic"

## Configuration

1. Go to Configuration > Integrations
2. Click "Add Integration"
3. Search for "Flatastic"
4. Enter your Flatastic API key
5. Click "Submit"

## API Key

To get your API key, you'll need to contact Flatastic support or check your account settings in the Flatastic app.

## Sensors

The integration will create one sensor for each chore returned by the API. Each sensor:

- Has a unique ID based on the chore ID
- Shows the assigned user as its state value
- Contains all chore data (including title) as attributes
- Automatically updates when chores are added, modified, or removed

## Services

### flatastic.complete_chore

Mark a chore as completed by a specific user.

**Parameters:**
- `chore_id` (required): The ID of the chore to complete
- `completed_by` (required): The user ID who completed the chore

### flatastic.cleanup_orphaned_entities

Remove sensor entities for chores that no longer exist in Flatastic. This service helps clean up "unavailable" sensors that remain after chores are deleted from the Flatastic app.

**Parameters:** None

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

See `examples/cleanup_automation.yaml` for more automation examples.

## Support

For issues and feature requests, please use the [issue tracker](https://codeberg.org/thegroove/ha-flatastic/issues).
