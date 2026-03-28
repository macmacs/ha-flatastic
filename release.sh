#!/bin/bash

# Flatastic Home Assistant Integration Release Script
# Usage: ./release.sh <version>
# Example: ./release.sh 0.0.1

set -e

# Check if version is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.0.1"
    exit 1
fi

VERSION=$1
DATE=$(date +"%Y-%m-%d")

# Validate semver format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in semver format (e.g., 0.0.1)"
    exit 1
fi

echo "Creating release $VERSION..."

# Update manifest.json
echo "Updating manifest.json..."
sed -i.bak "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" custom_components/flatastic/manifest.json
rm custom_components/flatastic/manifest.json.bak

# Update const.py if it has a version constant
if grep -q "VERSION" custom_components/flatastic/const.py; then
    echo "Updating const.py..."
    sed -i.bak "s/VERSION = \".*\"/VERSION = \"$VERSION\"/" custom_components/flatastic/const.py
    rm custom_components/flatastic/const.py.bak
fi

# Create/update CHANGELOG.md
echo "Updating CHANGELOG.md..."
if [ ! -f CHANGELOG.md ]; then
    cat > CHANGELOG.md << EOF
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [$VERSION] - $DATE

### Added
- Initial release of Flatastic Home Assistant Integration
- Sensor platform for individual chore monitoring
- Configuration flow for easy setup
- Services for chore completion and entity cleanup
- Custom Lovelace card for interactive chore management
- HACS compatibility
- Translations (English and German)
- Example configurations and automations

EOF
else
    # Insert new version at the top of existing changelog
    temp_file=$(mktemp)
    head -n 6 CHANGELOG.md > "$temp_file"
    echo "" >> "$temp_file"
    echo "## [$VERSION] - $DATE" >> "$temp_file"
    echo "" >> "$temp_file"
    echo "### Changed" >> "$temp_file"
    echo "- Version bump to $VERSION" >> "$temp_file"
    echo "" >> "$temp_file"
    tail -n +7 CHANGELOG.md >> "$temp_file"
    mv "$temp_file" CHANGELOG.md
fi

# Note: Version badge removed from README.md as per user preference

# Commit changes
echo "Committing changes..."
git add .
git commit -m "Release version $VERSION

- Updated version in manifest.json
- Updated CHANGELOG.md"

# Create git tag
echo "Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "Release version $VERSION

See CHANGELOG.md for details."

echo ""
echo "Release $VERSION created successfully!"
echo ""
echo "Next steps:"
echo "1. Review the changes: git show v$VERSION"
echo "2. Push the changes: git push origin main"
echo "3. Push the tag: git push origin v$VERSION"
echo "4. Create a release on Codeberg with the tag v$VERSION"
echo ""
echo "HACS will automatically detect the new version from the git tag."
