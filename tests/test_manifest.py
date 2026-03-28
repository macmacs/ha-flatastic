"""Tests to validate manifest.json and hacs.json."""
import json
from pathlib import Path


INTEGRATION_DIR = Path(__file__).parent.parent / "custom_components" / "flatastic"


class TestManifest:
    """Tests for manifest.json."""

    def setup_method(self):
        with open(INTEGRATION_DIR / "manifest.json") as f:
            self.manifest = json.load(f)

    def test_domain(self):
        assert self.manifest["domain"] == "flatastic"

    def test_name(self):
        assert self.manifest["name"] == "Flatastic"

    def test_has_version(self):
        assert "version" in self.manifest
        parts = self.manifest["version"].split(".")
        assert len(parts) == 3

    def test_config_flow_enabled(self):
        assert self.manifest["config_flow"] is True

    def test_has_codeowners(self):
        assert len(self.manifest["codeowners"]) > 0

    def test_has_documentation_url(self):
        assert self.manifest["documentation"].startswith("https://")

    def test_has_issue_tracker(self):
        assert self.manifest["issue_tracker"].startswith("https://")

    def test_iot_class(self):
        assert self.manifest["iot_class"] == "cloud_polling"

    def test_requirements(self):
        assert any("aiohttp" in r for r in self.manifest["requirements"])


class TestHacsJson:
    """Tests for hacs.json."""

    def setup_method(self):
        with open(INTEGRATION_DIR / "hacs.json") as f:
            self.hacs = json.load(f)

    def test_name(self):
        assert self.hacs["name"] == "Flatastic"

    def test_content_not_in_root(self):
        assert self.hacs["content_in_root"] is False

    def test_has_homeassistant_version(self):
        assert "homeassistant" in self.hacs

    def test_domains_includes_sensor(self):
        assert "sensor" in self.hacs["domains"]
