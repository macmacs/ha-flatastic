# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-03-28

- Register card static path from integration's own www/ directory


## [0.1.1] - 2026-03-28

- Fixed bug in card: use Math.trunc in formatOverdueTime to correctly show hours for sub-day overdue chores
- Add ESLint and vitest for the custom card JS
- Upgrade actions to Node.js 24 compatible versions
- Increase readability of card's contents

## [0.1.0] - 2026-03-28

- Replace release.sh with GitHub Actions release workflow
- Add test suite and GitHub Actions CI workflow
- Rewrite README and fix documentation
- Bump aiohttp requirement to >=3.11.0
- Remove emojis from all files
- Fix logging to use %-formatting instead of f-strings


## [0.0.1] - 2025-01-25

### Added
- Initial release of Flatastic Home Assistant Integration
- Sensor platform for individual chore monitoring with rich attributes
- Configuration flow for easy setup through Home Assistant UI
- Services for chore completion and entity cleanup
- Custom Lovelace card for interactive chore management
- HACS compatibility with proper manifest and configuration
- Translations support (English and German)
- Example configurations and automations
- Filterable attributes for use with Auto Entities card
- Status and urgency indicators for chores
- Automatic entity cleanup when chores are deleted
- Comprehensive documentation and installation instructions

### Features
- Fetches chore data from the Flatastic API
- Creates individual sensors for each chore
- Automatic updates every 15 minutes
- Shows current assigned user name as sensor state
- All chore attributes available as sensor attributes
- Filterable attributes for dashboard automation
- Custom card with color-coded urgency levels
- Services for chore management and cleanup
