"""Contract tests for config-guard unified plugin."""

import json
from pathlib import Path

HOME = Path(__file__).resolve().parents[1]
UNIFIED_DIR = HOME / "plugins" / "config-guard"
DESKTOP_DIR = HOME / "desktop-plugins" / "config-guard"


def test_config_guard_manifest_and_yaml():
    manifest_file = UNIFIED_DIR / "dashboard" / "manifest.json"
    plugin_yaml = UNIFIED_DIR / "plugin.yaml"

    assert manifest_file.exists(), "dashboard/manifest.json must exist"
    assert plugin_yaml.exists(), "plugin.yaml must exist"

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest.get("name") == "config-guard"

    yaml_text = plugin_yaml.read_text(encoding="utf-8")
    assert "name: config-guard" in yaml_text
    assert "has_desktop_half: true" in yaml_text


def test_config_guard_desktop_plugin_js_exists():
    unified_js = UNIFIED_DIR / "desktop" / "plugin.js"
    assert unified_js.exists(), "plugins/config-guard/desktop/plugin.js must exist"

    content = unified_js.read_text(encoding="utf-8")
    assert "id: ID" in content or "id: 'config-guard'" in content
    assert "statusBar.right" in content
    assert "/result" in content
