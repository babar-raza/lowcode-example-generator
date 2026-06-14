"""Unit tests for the HealingIntelligenceLoader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.healing_intelligence.loader import (
    _REGISTRY_FILES,
    HealingIntelligenceLoader,
)


@pytest.fixture
def registry_dir(tmp_path: Path) -> Path:
    """Create a temporary registry directory with all 5 registries."""
    d = tmp_path / "healing-intelligence"
    d.mkdir()

    # Bootstrap
    (d / "healing-intelligence-bootstrap.json").write_text(
        json.dumps({"bootstrap_version": "1.0", "families": ["cells", "words"]}),
        encoding="utf-8",
    )
    # Failure patterns
    (d / "failure-pattern-registry.json").write_text(
        json.dumps(
            {
                "patterns": [
                    {
                        "id": "FP-001",
                        "name": "missing_namespace_using_directive",
                        "affected_families": ["cells"],
                        "affected_types": ["SpreadsheetConverter"],
                    },
                    {
                        "id": "FP-002",
                        "name": "wrong_static_call",
                        "affected_families": ["pdf"],
                        "affected_types": ["Merger"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    # Repair patterns
    (d / "repair-pattern-registry.json").write_text(
        json.dumps(
            {
                "patterns": [
                    {
                        "id": "RP-001",
                        "resolves_failure": "FP-001",
                        "strategy": "add_using_directive",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    # Semantic steering
    (d / "semantic-steering-registry.json").write_text(
        json.dumps(
            {
                "families": {
                    "cells": {
                        "global_required": ["using Aspose.Cells"],
                        "global_forbidden": ["using Aspose.Words"],
                        "per_type": {
                            "SpreadsheetConverter": {
                                "required": ["Process("],
                                "forbidden": ["new SpreadsheetConverter()"],
                            }
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    # Validator patterns
    (d / "validator-pattern-registry.json").write_text(
        json.dumps(
            {
                "rules": [
                    {
                        "id": "VR-001",
                        "applies_to": {"families": ["cells"], "types": "all"},
                        "current_status": "IMPLEMENTED",
                        "check": "namespace_present",
                    },
                    {
                        "id": "VR-002",
                        "applies_to": {"families": "all", "types": ["Merger"]},
                        "current_status": "NOT_IMPLEMENTED",
                        "check": "output_file_check",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    return d


class TestLoaderInit:
    def test_default_registry_dir(self):
        loader = HealingIntelligenceLoader()
        assert "healing-intelligence" in str(loader._registry_dir)

    def test_custom_registry_dir(self, tmp_path):
        loader = HealingIntelligenceLoader(registry_dir=tmp_path)
        assert loader._registry_dir == tmp_path

    def test_not_loaded_initially(self):
        loader = HealingIntelligenceLoader()
        assert loader.is_loaded() is False


class TestLoaderLoad:
    def test_load_all_registries(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir)
        result = loader.load()
        assert result is loader  # chaining
        assert loader.is_loaded() is True

    def test_idempotent_load(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir)
        loader.load()
        loader.load()  # second call should not raise
        assert loader.is_loaded() is True

    def test_missing_registries_degrade_gracefully(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        loader = HealingIntelligenceLoader(registry_dir=empty_dir)
        loader.load()  # should not raise
        assert loader.is_loaded() is True
        assert loader.get_failure_patterns() == []


class TestRegistryPresence:
    def test_all_core_present(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir)
        assert loader.all_core_registries_present() is True

    def test_missing_core_detected(self, tmp_path):
        d = tmp_path / "partial"
        d.mkdir()
        (d / "failure-pattern-registry.json").write_text("[]", encoding="utf-8")
        loader = HealingIntelligenceLoader(registry_dir=d)
        assert loader.all_core_registries_present() is False

    def test_registries_present_dict(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir)
        presence = loader.registries_present()
        assert all(presence.values())


class TestFailurePatternQueries:
    def test_get_all_failure_patterns(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        patterns = loader.get_failure_patterns()
        assert len(patterns) == 2

    def test_get_failure_pattern_by_id(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        p = loader.get_failure_pattern("FP-001")
        assert p is not None
        assert p["name"] == "missing_namespace_using_directive"

    def test_get_failure_pattern_not_found(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        assert loader.get_failure_pattern("FP-999") is None

    def test_is_known_failure(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        assert loader.is_known_failure("missing_namespace_using_directive") is True
        assert loader.is_known_failure("unknown_failure") is False

    def test_get_failures_for_type(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        failures = loader.get_failures_for_type("cells", "SpreadsheetConverter")
        assert len(failures) == 1
        assert failures[0]["id"] == "FP-001"

    def test_get_failures_for_type_no_match(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        assert loader.get_failures_for_type("diagram", "Converter") == []


class TestRepairPatternQueries:
    def test_get_repair_pattern_by_id(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        p = loader.get_repair_pattern("RP-001")
        assert p is not None
        assert p["strategy"] == "add_using_directive"

    def test_get_repair_for_failure(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        repair = loader.get_repair_for_failure("FP-001")
        assert repair is not None
        assert repair["id"] == "RP-001"

    def test_get_repair_for_unknown_failure(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        assert loader.get_repair_for_failure("FP-999") is None


class TestSemanticSteeringQueries:
    def test_get_steering_constraints(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        constraints = loader.get_steering_constraints("cells", "SpreadsheetConverter")
        assert "Process(" in constraints["required"]
        assert "new SpreadsheetConverter()" in constraints["forbidden"]
        assert "using Aspose.Cells" in constraints["global_required"]

    def test_get_global_steering(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        global_s = loader.get_global_steering("cells")
        assert "using Aspose.Cells" in global_s["global_required"]
        assert "using Aspose.Words" in global_s["global_forbidden"]

    def test_unknown_family_returns_empty(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        constraints = loader.get_steering_constraints("unknown", "Type")
        assert constraints["required"] == []
        assert constraints["forbidden"] == []


class TestValidatorRuleQueries:
    def test_get_validator_rules_for_type(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        rules = loader.get_validator_rules("cells", "SpreadsheetConverter")
        assert len(rules) == 1
        assert rules[0]["id"] == "VR-001"

    def test_get_validator_rules_all_families(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        rules = loader.get_validator_rules("pdf", "Merger")
        assert any(r["id"] == "VR-002" for r in rules)

    def test_get_implemented_rules_only(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        implemented = loader.get_implemented_validator_rules()
        assert len(implemented) == 1
        assert implemented[0]["id"] == "VR-001"


class TestSummary:
    def test_summary_keys(self, registry_dir):
        loader = HealingIntelligenceLoader(registry_dir=registry_dir).load()
        s = loader.summary()
        assert s["loaded"] is True
        assert s["failure_patterns_count"] == 2
        assert s["repair_patterns_count"] == 1
        assert "cells" in s["families_with_steering"]
