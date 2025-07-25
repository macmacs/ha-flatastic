# Flatastic Home Assistant Integration

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

This integration can be installed through HACS (Home Assistant Community Store).

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://codeberg.org/thegroove/ha-flatastic`
6. Select "Integration" as the category
7. Click "Add"
8. Find "Flatastic" in the integration list and install it
9. Restart Home Assistant

## Configuration

After installation:

1. Go to Configuration > Integrations in Home Assistant
2. Click "Add Integration"
3. Search for "Flatastic"
4. Enter your Flatastic API key
5. Click "Submit"

## What you get

- Individual sensors for each chore with current assigned user as state
- Rich attributes including status, urgency, and timing information
- Custom Lovelace card for managing overdue chores
- Services for completing chores and cleaning up entities
- Full compatibility with Auto Entities card for advanced filtering

For detailed documentation, see the [README](https://codeberg.org/thegroove/ha-flatastic/src/branch/main/README.md).
