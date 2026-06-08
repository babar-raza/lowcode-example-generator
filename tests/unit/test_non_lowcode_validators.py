"""Tests for NonLowCodeValidatorRules mixin — TC-IMPL-006.

29 tests: 14 pass, 14 fail, 1 skip.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import yaml

from plugin_examples.evidence_validator.rules.non_lowcode import NonLowCodeValidatorRules


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_validator(
    *,
    registry_dir: Path | None = None,
    family: str = "barcode",
    fallback_strategy: str | None = "capability_registry",
    entries: list[dict] | None = None,
) -> NonLowCodeValidatorRules:
    """Build a minimal NonLowCodeValidatorRules instance for testing."""
    v = NonLowCodeValidatorRules()
    v.bundle_dir = Path(".")
    v.family = family
    plugin_detection = SimpleNamespace(fallback_strategy=fallback_strategy)
    v.config = SimpleNamespace(plugin_detection=plugin_detection)

    # Override registry dir to a tmp path if given
    if registry_dir is not None:
        v._nl_registry_dir_override = registry_dir

        # Patch _nl_registry_dir to return the override
        original_method = v._nl_registry_dir

        def _patched_registry_dir():
            return registry_dir

        v._nl_registry_dir = _patched_registry_dir  # type: ignore[method-assign]

    # If entries given, write a registry YAML in registry_dir
    if entries is not None and registry_dir is not None:
        registry_dir.mkdir(parents=True, exist_ok=True)
        registry_file = registry_dir / f"{family}.yaml"
        registry_file.write_text(
            yaml.dump({"entries": entries}), encoding="utf-8"
        )

    return v


def _good_entry(**overrides) -> dict:
    """A valid registry entry."""
    base = {
        "family": "barcode",
        "package_id": "Aspose.BarCode",
        "type_name": "BarcodeGenerator",
        "namespace": "Aspose.BarCode.Generation",
        "method_name": "Save",
        "status": "PROBE_CONFIRMED",
        "confidence_score": 0.95,
        "confidence_rationale": "test",
        "probe_evidence": "reports/test/output-validation.json",
        "failure_taxonomy": None,
        "rejection_reason": None,
        "ai_source_flag": False,
        "assembly_fingerprint": "a" * 64,
        "last_validated": "2026-06-04T00:00:00Z",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# TC-IMPL-006: test_all_rules_skip_when_no_registry_directory_exists
# ---------------------------------------------------------------------------


class TestAllRulesSkipWhenNoRegistryDirectory:
    def test_all_rules_skip_when_no_registry_directory_exists(self, tmp_path):
        """All 14 rules must return passed=True (SKIP) when registry dir absent."""
        empty_dir = tmp_path / "no-registry-here"
        v = _make_validator(registry_dir=empty_dir, entries=None)

        rules = [
            v.rule_nl_v01, v.rule_nl_v02, v.rule_nl_v03, v.rule_nl_v04,
            v.rule_nl_v05, v.rule_nl_v06, v.rule_nl_v07, v.rule_nl_v08,
            v.rule_nl_v09, v.rule_nl_v10, v.rule_nl_v11, v.rule_nl_v12,
            v.rule_nl_v13, v.rule_nl_v14,
        ]
        for rule in rules:
            result = rule()
            assert result.passed is True, f"{rule.__name__} should SKIP (registry absent)"
            assert "SKIP" in result.evidence, f"{rule.__name__}: expected SKIP in evidence"


# ---------------------------------------------------------------------------
# Passing tests (14)
# ---------------------------------------------------------------------------


class TestNLV01Passes:
    def test_nl_v01_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[_good_entry()])
        result = v.rule_nl_v01()
        assert result.passed is True


class TestNLV02Passes:
    def test_nl_v02_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[_good_entry(status="PROBE_CONFIRMED")])
        result = v.rule_nl_v02()
        assert result.passed is True


class TestNLV03Passes:
    def test_nl_v03_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[_good_entry(confidence_score=0.95)])
        result = v.rule_nl_v03()
        assert result.passed is True


class TestNLV04Passes:
    def test_nl_v04_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[_good_entry(package_id="Aspose.BarCode")])
        result = v.rule_nl_v04()
        assert result.passed is True


class TestNLV05Passes:
    def test_nl_v05_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="PROBE_CONFIRMED", probe_evidence="reports/test/out.json")
        ])
        result = v.rule_nl_v05()
        assert result.passed is True


class TestNLV06Passes:
    def test_nl_v06_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="VERIFIED_PUBLISHABLE", probe_evidence="reports/test/out.json")
        ])
        result = v.rule_nl_v06()
        assert result.passed is True


class TestNLV07Passes:
    def test_nl_v07_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="PROBE_FAILED", failure_taxonomy="PROBE_FAILED_LICENSE", probe_evidence=None)
        ])
        result = v.rule_nl_v07()
        assert result.passed is True


class TestNLV08Passes:
    def test_nl_v08_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="REJECTED_BY_VALIDATOR", rejection_reason="TYPE_NOT_IN_REFLECTION", probe_evidence=None)
        ])
        result = v.rule_nl_v08()
        assert result.passed is True


class TestNLV09Passes:
    def test_nl_v09_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(assembly_fingerprint="0" * 64)
        ])
        result = v.rule_nl_v09()
        assert result.passed is True


class TestNLV10Passes:
    def test_nl_v10_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="PROBE_CONFIRMED", last_validated="2026-06-04T00:00:00Z")
        ])
        result = v.rule_nl_v10()
        assert result.passed is True


class TestNLV11Passes:
    def test_nl_v11_passes_with_valid_evidence(self, tmp_path):
        # No PROBE_UNKNOWN entries
        v = _make_validator(registry_dir=tmp_path, entries=[_good_entry(status="PROBE_CONFIRMED")])
        result = v.rule_nl_v11()
        assert result.passed is True


class TestNLV12Passes:
    def test_nl_v12_passes_with_valid_evidence(self, tmp_path):
        # ai_source_flag=True but not VERIFIED_PUBLISHABLE
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(ai_source_flag=True, status="PROBE_CONFIRMED")
        ])
        result = v.rule_nl_v12()
        assert result.passed is True


class TestNLV13Passes:
    def test_nl_v13_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(probe_evidence="reports/test/out.json")
        ])
        result = v.rule_nl_v13()
        assert result.passed is True


class TestNLV14Passes:
    def test_nl_v14_passes_with_valid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(type_name="BarcodeGenerator", method_name="Save")
        ])
        result = v.rule_nl_v14()
        assert result.passed is True


# ---------------------------------------------------------------------------
# Failing tests (14)
# ---------------------------------------------------------------------------


class TestNLV01Fails:
    def test_nl_v01_fails_with_missing_or_invalid_evidence(self, tmp_path):
        # Registry dir exists but family YAML is absent
        (tmp_path).mkdir(parents=True, exist_ok=True)
        v = _make_validator(registry_dir=tmp_path, entries=None)
        # Don't write the YAML file
        result = v.rule_nl_v01()
        assert result.passed is False


class TestNLV02Fails:
    def test_nl_v02_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="PROBE_UNKNOWN")  # invalid status
        ])
        result = v.rule_nl_v02()
        assert result.passed is False


class TestNLV03Fails:
    def test_nl_v03_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(confidence_score=2.0)  # > 1.05
        ])
        result = v.rule_nl_v03()
        assert result.passed is False


class TestNLV04Fails:
    def test_nl_v04_fails_with_missing_or_invalid_evidence(self, tmp_path):
        # Write an aliases file and set a wrong package_id
        aliases_file = tmp_path / "package-aliases.json"
        aliases_file.write_text(json.dumps({"families": {"barcode": "Aspose.BarCode"}}))
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(package_id="Aspose.Barcode")  # wrong casing = mismatch
        ])
        result = v.rule_nl_v04()
        # Rule should pass because the exact ID "Aspose.Barcode" != "Aspose.BarCode"
        # but the rule only fires when id == slug_inferred — which is "Aspose.Barcode"
        # (slug = family.title() = "Barcode")
        # So it will compare against alias and find mismatch
        # Actually "Aspose.Barcode" == slug_inferred → violation found
        assert result.passed is False


class TestNLV05Fails:
    def test_nl_v05_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="PROBE_CONFIRMED", probe_evidence=None)
        ])
        result = v.rule_nl_v05()
        assert result.passed is False


class TestNLV06Fails:
    def test_nl_v06_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="VERIFIED_PUBLISHABLE", probe_evidence=None)
        ])
        result = v.rule_nl_v06()
        assert result.passed is False


class TestNLV07Fails:
    def test_nl_v07_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="PROBE_FAILED", failure_taxonomy=None, probe_evidence=None)
        ])
        result = v.rule_nl_v07()
        assert result.passed is False


class TestNLV08Fails:
    def test_nl_v08_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="REJECTED_BY_VALIDATOR", rejection_reason=None, probe_evidence=None)
        ])
        result = v.rule_nl_v08()
        assert result.passed is False


class TestNLV09Fails:
    def test_nl_v09_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(assembly_fingerprint="not-a-valid-sha")
        ])
        result = v.rule_nl_v09()
        assert result.passed is False


class TestNLV10Fails:
    def test_nl_v10_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="PROBE_CONFIRMED", last_validated=None)
        ])
        result = v.rule_nl_v10()
        assert result.passed is False


class TestNLV11Fails:
    def test_nl_v11_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(status="PROBE_UNKNOWN")  # forbidden
        ])
        result = v.rule_nl_v11()
        assert result.passed is False


class TestNLV12Fails:
    def test_nl_v12_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(ai_source_flag=True, status="VERIFIED_PUBLISHABLE",
                        probe_evidence="reports/test/out.json")
        ])
        result = v.rule_nl_v12()
        assert result.passed is False


class TestNLV13Fails:
    def test_nl_v13_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(probe_evidence="pipeline/format-authority/manifest.json")
        ])
        result = v.rule_nl_v13()
        assert result.passed is False


class TestNLV14Fails:
    def test_nl_v14_fails_with_missing_or_invalid_evidence(self, tmp_path):
        v = _make_validator(registry_dir=tmp_path, entries=[
            _good_entry(type_name="", method_name="Save")  # empty type_name
        ])
        result = v.rule_nl_v14()
        assert result.passed is False
