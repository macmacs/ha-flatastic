# Release Process

This document describes how to create a new release of the Flatastic Home Assistant Integration.

## Using the Release Script

The repository includes a `release.sh` script that automates the release process.

### Prerequisites

- Ensure you have committed all your changes
- Make sure you're on the main branch
- Have write access to the repository

### Creating a Release

1. Make the script executable (first time only):
   ```bash
   chmod +x release.sh
   ```

2. Run the release script with the desired version:
   ```bash
   ./release.sh 0.0.2
   ```

### What the Script Does

The release script automatically:

1. **Validates** the version format (must be semver: x.y.z)
2. **Updates** `custom_components/flatastic/manifest.json` with the new version
3. **Updates** `custom_components/flatastic/const.py` VERSION constant
4. **Updates** `CHANGELOG.md` with the new version entry
5. **Updates** `README.md` with a new version badge
6. **Commits** all changes with a release commit message
7. **Creates** a git tag `vX.Y.Z` with release notes

### After Running the Script

The script will provide next steps:

1. **Review the changes**: `git show vX.Y.Z`
2. **Push the changes**: `git push origin main`
3. **Push the tag**: `git push origin vX.Y.Z`
4. **Create a release** on Codeberg with the tag

### HACS Integration

HACS automatically detects new versions from git tags. Once you push the tag, HACS users will see the update available in their HACS interface.

### Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality in a backwards compatible manner
- **PATCH** version (0.0.X): Backwards compatible bug fixes

### Example Release Flow

```bash
# Make changes to the code
git add .
git commit -m "Add new feature"

# Create a release
./release.sh 0.1.0

# Push everything
git push origin main
git push origin v0.1.0

# Create release on Codeberg (optional but recommended)
```

### Manual Release (if script fails)

If the script doesn't work, you can create a release manually:

1. Update version in `manifest.json`
2. Update VERSION in `const.py`
3. Update `CHANGELOG.md`
4. Update version badge in `README.md`
5. Commit changes
6. Create and push git tag
