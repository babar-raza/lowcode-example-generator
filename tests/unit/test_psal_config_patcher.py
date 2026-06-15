"""Tests for PSAL config patcher — ephemeral config enablement."""

from __future__ import annotations

import pytest
import yaml

from plugin_examples.psal.config_patcher import ensure_runnable_config


@pytest.fixture
def family_config_dir(tmp_path):
    """Create a minimal family config directory structure."""
    families_dir = tmp_path / "pipeline" / "configs" / "families"
    families_dir.mkdir(parents=True)
    return families_dir


class TestEnsureRunnableConfig:
    def test_already_enabled_returns_original(self, tmp_path, family_config_dir):
        config = {"family": "barcode", "enabled": True, "status": "discovery_only"}
        config_path = family_config_dir / "barcode.yml"
        config_path.write_text(yaml.dump(config), encoding="utf-8")

        result = ensure_runnable_config("barcode", tmp_path)

        assert result == config_path

    def test_disabled_creates_patched_copy(self, tmp_path, family_config_dir):
        config = {
            "family": "drawing",
            "enabled": False,
            "status": "disabled",
            "plugin_detection": {"namespace_patterns": ["Aspose.Drawing.LowCode"]},
        }
        config_path = family_config_dir / "drawing.yml"
        config_path.write_text(yaml.dump(config), encoding="utf-8")

        result = ensure_runnable_config("drawing", tmp_path)

        assert result != config_path
        assert ".local/psal/configs" in str(result).replace("\\", "/")

        patched = yaml.safe_load(result.read_text(encoding="utf-8"))
        assert patched["enabled"] is True
        assert patched["status"] == "discovery_only"
        assert patched["plugin_detection"]["fallback_strategy"] == "capability_registry"

    def test_original_not_modified(self, tmp_path, family_config_dir):
        config = {"family": "gis", "enabled": False, "status": "disabled"}
        config_path = family_config_dir / "gis.yml"
        config_path.write_text(yaml.dump(config), encoding="utf-8")

        ensure_runnable_config("gis", tmp_path)

        original = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert original["enabled"] is False

    def test_missing_config_returns_original_path(self, tmp_path, family_config_dir):
        result = ensure_runnable_config("nonexistent", tmp_path)

        assert result == family_config_dir / "nonexistent.yml"

    def test_fallback_strategy_added_when_missing(self, tmp_path, family_config_dir):
        config = {
            "family": "tex",
            "enabled": False,
            "status": "disabled",
            "plugin_detection": {"namespace_patterns": ["Aspose.TeX.LowCode"]},
        }
        config_path = family_config_dir / "tex.yml"
        config_path.write_text(yaml.dump(config), encoding="utf-8")

        result = ensure_runnable_config("tex", tmp_path)
        patched = yaml.safe_load(result.read_text(encoding="utf-8"))

        assert patched["plugin_detection"]["fallback_strategy"] == "capability_registry"
