# Flatastic Custom Card Installation

The Flatastic integration includes a custom Lovelace card that displays overdue chores with completion buttons.

## Automatic Installation (Recommended)

The custom card should be automatically available after installing the integration through HACS. However, if it's not working, follow the manual installation steps below.

## Manual Installation

### Step 1: Copy the Card File

1. Navigate to your Home Assistant configuration directory
2. Create the following directory structure if it doesn't exist:
   ```
   www/community/flatastic/
   ```
3. Copy the file `custom_components/flatastic/www/flatastic-chores-card.js` to:
   ```
   www/community/flatastic/flatastic-chores-card.js
   ```

### Step 2: Register the Resource

Add the following to your Lovelace resources (Configuration → Lovelace Dashboards → Resources):

- **URL**: `/local/community/flatastic/flatastic-chores-card.js`
- **Resource Type**: JavaScript Module

Or add it manually to your `configuration.yaml`:

```yaml
lovelace:
  resources:
    - url: /local/community/flatastic/flatastic-chores-card.js
      type: module
```

### Step 3: Restart Home Assistant

Restart Home Assistant to load the new resource.

### Step 4: Add the Card

Add the card to your dashboard:

```yaml
type: custom:flatastic-chores-card
```

## Troubleshooting

### Card Not Found Error

If you get a "Custom element doesn't exist" error:

1. Check that the file exists at `www/community/flatastic/flatastic-chores-card.js`
2. Verify the resource is properly registered in Lovelace resources
3. Clear your browser cache (Ctrl+F5 or Cmd+Shift+R)
4. Check the browser console for JavaScript errors

### Card Shows But No Data

If the card shows but displays "No overdue chores":

1. Verify the Flatastic integration is properly configured
2. Check that you have sensors with `status: overdue` attribute
3. Wait for the next data refresh (up to 15 minutes)

### Completion Buttons Don't Work

If the completion buttons don't respond:

1. Check that the `flatastic.complete_chore` service is available
2. Verify the integration is properly loaded
3. Check Home Assistant logs for error messages

## Card Features

- 🚨 Automatically shows only overdue chores
- 🎯 Color-coded urgency levels (high: red, medium: orange)
- ⏰ Displays how long each chore is overdue
- 👥 Shows completion buttons for each user assigned to the chore
- 🔘 One-click completion with user names (no generic "Complete" button)
- 🎉 Shows celebration message when no chores are overdue
- 📱 Responsive design for mobile and desktop
- 🔄 Real-time updates when chores are completed

## Example Usage

```yaml
# Basic usage
type: custom:flatastic-chores-card

# In a vertical stack
type: vertical-stack
cards:
  - type: custom:flatastic-chores-card
  - type: custom:auto-entities
    card:
      type: entities
      title: All Chores
    filter:
      include:
        - attributes:
            integration: flatastic
