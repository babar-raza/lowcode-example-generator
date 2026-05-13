"""Tests for healing intelligence activation and registry loading.

Verifies:
- All 4 core registries exist on disk (committed in healing-intelligence sprint)
- HealingIntelligenceLoader loads all registries successfully
- Known failure patterns are queryable
- Semantic steering constraints are available for pdf and words
- Validator rules are available and queryable
- Repair patterns link back to failure patterns
- Registry degrades gracefully when files are missing
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from plugin_examples.healing_intelligence.loader import HealingIntelligenceLoader


REGISTRY_DIR = Path("workspace/verification/latest/healing-intelligence")

EXPECTED_FAILURE_PATTERN_IDS = {
    "FP-001", "FP-002", "FP-003", "FP-004", "FP-005",
    "FP-006", "FP-007", "FP-008", "FP-009",
}

EXPECTED_REPAIR_PATTERN_IDS = {
    "RP-001", "RP-002", "RP-003", "RP-004", "RP-005",
    "RP-006", "RP-007", "RP-008", "RP-009",
}

EXPECTED_FAMILIES_WITH_STEERING = {"pdf", "words", "cells", "diagram", "email", "slides"}


class TestRegistryFilesPresent:
    def test_failure_pattern_registry_exists(self):
        assert (REGISTRY_DIR / "failure-pattern-registry.json").exists(), \
            "failure-pattern-registry.json must exist (committed in healing-intelligence sprint)"

    def test_repair_pattern_registry_exists(self):
        assert (REGISTRY_DIR / "repair-pattern-registry.json").exists(), \
            "repair-pattern-registry.json must exist"

    def test_semantic_steering_registry_exists(self):
        assert (REGISTRY_DIR / "semantic-steering-registry.json").exists(), \
            "semantic-steering-registry.json must exist"

    def test_validator_pattern_registry_exists(self):
        assert (REGISTRY_DIR / "validator-pattern-registry.json").exists(), \
            "validator-pattern-registry.json must exist"

    def test_bootstrap_exists(self):
        assert (REGISTRY_DIR / "healing-intelligence-bootstrap.json").exists(), \
            "healing-intelligence-bootstrap.json must exist"

    def test_all_registry_json_files_are_valid_json(self):
        for path in REGISTRY_DIR.glob("*.json"):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                pytest.fail(f"{path.name} is not valid JSON: {e}")


class TestLoaderLoadsSuccessfully:
    def test_loader_loads_without_error(self):
        loader = HealingIntelligenceLoader()
        loader.load()
        assert loader.is_loaded()

    def test_loader_idempotent_double_load(self):
        loader = HealingIntelligenceLoader()
        loader.load()
        loader.load()  # second call must not raise or reset
        assert loader.is_loaded()

    def test_all_core_registries_present(self):
        loader = HealingIntelligenceLoader()
        assert loader.all_core_registries_present(), \
            "All 4 core registries must be present on disk"

    def test_summary_reports_loaded_state(self):
        loader = HealingIntelligenceLoader()
        loader.load()
        s = loader.summary()
        assert s["loaded"] is True
        assert s["failure_patterns_count"] >= 9
        assert s["repair_patterns_count"] >= 9
        assert s["validator_rules_count"] >= 12

    def test_families_with_steering_covers_all_active(self):
        loader = HealingIntelligenceLoader()
        loader.load()
        s = loader.summary()
        covered = set(s["families_with_steering"])
        assert EXPECTED_FAMILIES_WITH_STEERING.issubset(covered), \
            f"Missing families in steering: {EXPECTED_FAMILIES_WITH_STEERING - covered}"


class TestFailurePatternQueries:
    @pytest.fixture(autouse=True)
    def loader(self):
        self._loader = HealingIntelligenceLoader()
        self._loader.load()

    def test_all_expected_failure_patterns_present(self):
        patterns = self._loader.get_failure_patterns()
        ids = {p["id"] for p in patterns}
        missing = EXPECTED_FAILURE_PATTERN_IDS - ids
        assert not missing, f"Missing failure patterns: {missing}"

    def test_fp001_is_catalog_hash_mismatch(self):
        p = self._loader.get_failure_pattern("FP-001")
        assert p is not None
        assert p["name"] == "catalog_hash_mismatch_stale_denominator"
        assert p["category"] == "INFRASTRUCTURE"

    def test_fp008_is_processor_api_paradox(self):
        p = self._loader.get_failure_pattern("FP-008")
        assert p is not None
        assert p["name"] == "processor_api_access_paradox"
        assert p["severity"] == "PERMANENTLY_BLOCKED"

    def test_is_known_failure_returns_true_for_known(self):
        assert self._loader.is_known_failure("catalog_hash_mismatch_stale_denominator")
        assert self._loader.is_known_failure("processor_api_access_paradox")

    def test_is_known_failure_returns_false_for_unknown(self):
        assert not self._loader.is_known_failure("does_not_exist_failure_pattern")

    def test_get_failures_for_type_pdf_merger(self):
        failures = self._loader.get_failures_for_type("pdf", "Merger")
        assert len(failures) >= 2, "Merger should have at least FP-002 and FP-005"
        ids = {f["id"] for f in failures}
        assert "FP-002" in ids, "FP-002 (missing Aspose.Pdf.Text namespace) must affect Merger"
        assert "FP-005" in ids, "FP-005 (repair regression lost AddInput) must affect Merger"

    def test_get_failures_for_type_pdf_pdfa_converter(self):
        failures = self._loader.get_failures_for_type("pdf", "PdfAConverter")
        ids = {f["id"] for f in failures}
        assert "FP-004" in ids, "FP-004 (wrong options class) must affect PdfAConverter"
        assert "FP-009" in ids, "FP-009 (LowCodeLoadOptions wrong) must affect PdfAConverter"


class TestRepairPatternQueries:
    @pytest.fixture(autouse=True)
    def loader(self):
        self._loader = HealingIntelligenceLoader()
        self._loader.load()

    def test_all_expected_repair_patterns_present(self):
        ids = {self._loader.get_repair_pattern(rid)["id"]
               for rid in EXPECTED_REPAIR_PATTERN_IDS
               if self._loader.get_repair_pattern(rid)}
        missing = EXPECTED_REPAIR_PATTERN_IDS - ids
        assert not missing, f"Missing repair patterns: {missing}"

    def test_repair_for_fp001_is_denominator_update(self):
        rp = self._loader.get_repair_for_failure("FP-001")
        assert rp is not None
        assert rp["strategy"] == "DENOMINATOR_UPDATE"

    def test_repair_for_fp008_is_type_exclusion(self):
        rp = self._loader.get_repair_for_failure("FP-008")
        assert rp is not None
        assert rp["strategy"] == "TYPE_EXCLUSION"

    def test_every_failure_has_a_repair(self):
        for fp_id in EXPECTED_FAILURE_PATTERN_IDS:
            rp = self._loader.get_repair_for_failure(fp_id)
            assert rp is not None, f"No repair pattern found for {fp_id}"


class TestSemanticSteeringQueries:
    @pytest.fixture(autouse=True)
    def loader(self):
        self._loader = HealingIntelligenceLoader()
        self._loader.load()

    def test_pdf_merger_has_required_constraints(self):
        c = self._loader.get_steering_constraints("pdf", "Merger")
        assert len(c["required"]) >= 4, "Merger must have at least 4 REQUIRED constraints"

    def test_pdf_merger_has_addinput_constraint(self):
        c = self._loader.get_steering_constraints("pdf", "Merger")
        required_text = " ".join(c["required"])
        assert "AddInput" in required_text, "Merger REQUIRED constraints must include AddInput"

    def test_pdf_pdfa_converter_required_includes_options_class(self):
        c = self._loader.get_steering_constraints("pdf", "PdfAConverter")
        required_text = " ".join(c["required"])
        assert "PdfAConvertOptions" in required_text, \
            "PdfAConverter REQUIRED must include PdfAConvertOptions"

    def test_pdf_pdfa_converter_forbidden_includes_plugin_options(self):
        c = self._loader.get_steering_constraints("pdf", "PdfAConverter")
        forbidden_text = " ".join(c["forbidden"])
        assert "PluginOptions" in forbidden_text, \
            "PdfAConverter FORBIDDEN must include PluginOptions"

    def test_words_mail_merger_has_required_insert_field(self):
        c = self._loader.get_steering_constraints("words", "MailMerger")
        required_text = " ".join(c["required"])
        assert "InsertField" in required_text, \
            "MailMerger REQUIRED must include InsertField"

    def test_global_steering_returns_for_all_active_families(self):
        for family in ["pdf", "words", "cells", "diagram"]:
            gs = self._loader.get_global_steering(family)
            assert "global_required" in gs
            assert "global_forbidden" in gs


class TestValidatorRuleQueries:
    @pytest.fixture(autouse=True)
    def loader(self):
        self._loader = HealingIntelligenceLoader()
        self._loader.load()

    def test_validator_rules_load_as_list(self):
        rules = self._loader._validator_patterns
        assert isinstance(rules, list)
        assert len(rules) >= 12

    def test_pdf_merger_has_validator_rules(self):
        rules = self._loader.get_validator_rules("pdf", "Merger")
        assert len(rules) >= 2, "Merger should have at least addinput and addoutput rules"

    def test_text_extractor_has_add_output_forbidden_rule(self):
        rules = self._loader.get_validator_rules("pdf", "TextExtractor")
        names = [r.get("name") for r in rules]
        assert "add_output_absent_text_extractor" in names, \
            "TextExtractor must have rule forbidding AddOutput call"

    def test_implemented_rules_subset_of_all_rules(self):
        all_rules = self._loader._validator_patterns
        impl_rules = self._loader.get_implemented_validator_rules()
        assert len(impl_rules) <= len(all_rules)
        assert len(impl_rules) >= 1


class TestGracefulDegradation:
    def test_loader_with_missing_registry_dir_warns_not_raises(self):
        loader = HealingIntelligenceLoader(registry_dir="/nonexistent/path/xyz")
        loader.load()  # must not raise
        assert loader.is_loaded()
        s = loader.summary()
        assert s["failure_patterns_count"] == 0

    def test_loader_with_empty_dir_degrades_gracefully(self, tmp_path):
        loader = HealingIntelligenceLoader(registry_dir=tmp_path)
        loader.load()  # no files in tmp_path
        assert loader.is_loaded()
        assert loader.get_failure_patterns() == []
        assert loader.is_known_failure("anything") is False
        assert not loader.all_core_registries_present()
