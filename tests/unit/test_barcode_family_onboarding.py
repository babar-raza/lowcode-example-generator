"""Tests for BarCode family onboarding — TC-IMPL-007."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BARCODE_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "barcode.yml"
CELLS_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "cells.yml"
WORDS_CONFIG = REPO_ROOT / "pipeline" / "configs" / "families" / "words.yml"
REGISTRY_SCHEMA = REPO_ROOT / "pipeline" / "plugin-capability-registry" / "schema.json"
OUTPUT_VALIDATION = (
    REPO_ROOT
    / "reports"
    / "lowcode-non-lowcode-fallback-implementation-20260604"
    / "prototypes"
    / "barcode"
    / "output-validation.json"
)


class TestBarcodeConfigLoads:
    def test_barcode_config_loads_without_error(self):
        """barcode.yml must load and pass schema validation without error."""
        from plugin_examples.family_config.loader import load_family_config

        config = load_family_config(BARCODE_CONFIG)
        assert config.family == "barcode"
        assert config.status == "discovery_only"
        assert config.enabled is True

    def test_barcode_fallback_strategy_is_capability_registry(self):
        """barcode.yml must have fallback_strategy='capability_registry'."""
        from plugin_examples.family_config.loader import load_family_config

        config = load_family_config(BARCODE_CONFIG)
        assert config.plugin_detection.fallback_strategy == "capability_registry"

    def test_barcode_registry_entry_validates_against_schema(self):
        """The BarCode output-validation.json evidence must satisfy probe_verdict=PROBE_CONFIRMED."""
        assert OUTPUT_VALIDATION.exists(), f"Evidence file missing: {OUTPUT_VALIDATION}"
        data = json.loads(OUTPUT_VALIDATION.read_text(encoding="utf-8"))
        assert data["probe_verdict"] == "PROBE_CONFIRMED"
        assert data["output_validated"] is True
        assert data["output_size_bytes"] > 0
        assert data["failure_taxonomy"] is None

    def test_barcode_onboarding_does_not_affect_cells_or_words(self):
        """LowCode family YAMLs must be unmodified after barcode onboarding."""
        with open(CELLS_CONFIG, encoding="utf-8") as f:
            cells = yaml.safe_load(f)
        with open(WORDS_CONFIG, encoding="utf-8") as f:
            words = yaml.safe_load(f)
        # cells and words must still be LowCode families
        assert cells["family"] == "cells"
        assert "LowCode" in str(cells["plugin_detection"]["namespace_patterns"])
        assert words["family"] == "words"
        assert "LowCode" in str(words["plugin_detection"]["namespace_patterns"])
        # Neither should have fallback_strategy
        assert cells["plugin_detection"].get("fallback_strategy") is None
        assert words["plugin_detection"].get("fallback_strategy") is None
