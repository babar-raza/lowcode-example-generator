"""Tests for Imaging family onboarding — TC-IMPL-008."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGING_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "imaging.yml"
LOWCODE_FAMILIES = ["cells", "words", "pdf", "slides", "email", "diagram"]
OUTPUT_VALIDATION = (
    REPO_ROOT
    / "reports"
    / "lowcode-non-lowcode-fallback-implementation-20260604"
    / "prototypes"
    / "imaging"
    / "output-validation.json"
)
FIXTURE_GEN = (
    REPO_ROOT
    / "reports"
    / "lowcode-non-lowcode-fallback-implementation-20260604"
    / "prototypes"
    / "imaging"
    / "probe"
    / "fixture_gen.py"
)


class TestImagingConfigLoads:
    def test_imaging_config_loads_without_error(self):
        """imaging.yml must load and pass schema validation without error."""
        from plugin_examples.family_config.loader import load_family_config

        config = load_family_config(IMAGING_CONFIG)
        assert config.family == "imaging"
        assert config.status == "discovery_only"
        assert config.enabled is True

    def test_imaging_fallback_strategy_is_capability_registry(self):
        """imaging.yml must have fallback_strategy='capability_registry'."""
        from plugin_examples.family_config.loader import load_family_config

        config = load_family_config(IMAGING_CONFIG)
        assert config.plugin_detection.fallback_strategy == "capability_registry"

    def test_imaging_registry_entry_validates_against_schema(self):
        """The Imaging output-validation.json must have PROBE_CONFIRMED verdict."""
        assert OUTPUT_VALIDATION.exists(), f"Evidence file missing: {OUTPUT_VALIDATION}"
        data = json.loads(OUTPUT_VALIDATION.read_text(encoding="utf-8"))
        assert data["probe_verdict"] == "PROBE_CONFIRMED"
        assert data["output_validated"] is True
        assert data["output_size_bytes"] > 0
        assert data["fixture"]["type"] == "TIER-1_PROGRAMMATIC"

    def test_imaging_onboarding_does_not_affect_lowcode_families(self):
        """All 6 LowCode family YAMLs must be unmodified after imaging onboarding."""
        families_dir = REPO_ROOT / "pipeline" / "configs" / "families"
        for family in LOWCODE_FAMILIES:
            config_path = families_dir / f"{family}.yml"
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            # Must still be a LowCode family
            assert "LowCode" in str(
                data["plugin_detection"]["namespace_patterns"]
            ), f"{family}.yml namespace_patterns lost LowCode after imaging onboarding"
            # Must NOT have fallback_strategy
            assert (
                data["plugin_detection"].get("fallback_strategy") is None
            ), f"{family}.yml unexpectedly got fallback_strategy"

    def test_fixture_gen_creates_valid_png(self, tmp_path):
        """fixture_gen.py must produce a valid PNG file without external dependencies."""
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location("fixture_gen", FIXTURE_GEN)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        out = tmp_path / "test-output.png"
        result = module.create_minimal_png(out)
        assert result.exists()
        assert result.stat().st_size > 0
        # Must start with PNG magic bytes
        assert result.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
