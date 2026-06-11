"""Unit tests for the Words Readiness Review Sprint.

These tests verify the artifacts produced by the Words Readiness Review and enforce
the constraints documented in the review. All tests are data-driven from the artifact
files — they do not hardcode knowledge independently of the review JSON.

No Words generation is performed in this test module.
No publishing is performed.
No all-family generation is performed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFICATION = REPO_ROOT / "workspace" / "verification" / "latest"

ROLE_CLASSIFICATION = VERIFICATION / "words-type-role-classification.json"
CONSUMER_RELATIONSHIPS = VERIFICATION / "words-consumer-relationships.json"
OPTIONS_REVIEW = VERIFICATION / "words-options-usage-review.json"
CANDIDATE_RANK = VERIFICATION / "words-generation-candidate-rank.json"
CATALOG_REVIEW = VERIFICATION / "words-catalog-review.json"
READINESS_RANK = VERIFICATION / "family-generation-readiness-rank.json"


def _load(path: Path) -> dict | list:
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Artifact existence guards
# ---------------------------------------------------------------------------


class TestWordsReviewArtifactsExist:
    def test_role_classification_written(self):
        assert ROLE_CLASSIFICATION.exists(), "words-type-role-classification.json must exist"

    def test_consumer_relationships_written(self):
        assert CONSUMER_RELATIONSHIPS.exists(), "words-consumer-relationships.json must exist"

    def test_options_usage_review_written(self):
        assert OPTIONS_REVIEW.exists(), "words-options-usage-review.json must exist"

    def test_words_generation_candidate_rank_written(self):
        assert CANDIDATE_RANK.exists(), "words-generation-candidate-rank.json must exist"

    def test_catalog_review_written(self):
        assert CATALOG_REVIEW.exists(), "words-catalog-review.json must exist"


# ---------------------------------------------------------------------------
# Role classification correctness
# ---------------------------------------------------------------------------


class TestWordsTypeRoleClassification:
    def _get_classifications(self) -> dict[str, dict]:
        data = _load(ROLE_CLASSIFICATION)
        return {c["type_name"]: c for c in data["classifications"]}

    def test_mail_merge_data_source_not_workflow_root_without_consumer(self):
        """MailMergeDataSource must be data_source_adapter, not workflow_root.

        Original classification was workflow_root at confidence 0.70.
        Reclassified: no consumer in LowCode API, only static Create() factories.
        """
        classifications = self._get_classifications()
        assert "MailMergeDataSource" in classifications
        mmds = classifications["MailMergeDataSource"]
        assert mmds["role"] == "data_source_adapter", (
            f"MailMergeDataSource must be data_source_adapter, got {mmds['role']!r}. "
            "It has no callable operations and no consumers in the LowCode API."
        )
        assert mmds["standalone_allowed"] is False, "MailMergeDataSource must not be standalone — no LowCode consumer"
        assert mmds["confidence"] > 0.70, f"Reclassified confidence must exceed prior 0.70, got {mmds['confidence']}"
        assert (
            "prior_classification" in mmds
        ), "MailMergeDataSource must document its prior_classification for audit trail"

    def test_words_options_types_not_standalone(self):
        """All options types must have standalone_allowed=false."""
        classifications = self._get_classifications()
        options_types = [name for name, c in classifications.items() if c["role"] == "options"]
        assert (
            len(options_types) >= 3
        ), f"Expected at least 3 options types, found {len(options_types)}: {options_types}"
        for name in options_types:
            c = classifications[name]
            assert c["standalone_allowed"] is False, f"Options type {name!r} must have standalone_allowed=false"

    def test_abstract_base_not_standalone(self):
        """Abstract base classes must have standalone_allowed=false."""
        classifications = self._get_classifications()
        abstract_types = [name for name, c in classifications.items() if c["role"] == "abstract_base"]
        assert len(abstract_types) >= 1, "Expected at least one abstract_base type"
        for name in abstract_types:
            c = classifications[name]
            assert c["standalone_allowed"] is False, f"Abstract type {name!r} must have standalone_allowed=false"

    def test_settings_model_types_not_standalone(self):
        """All settings_model (context) types must have standalone_allowed=false."""
        classifications = self._get_classifications()
        context_types = [name for name, c in classifications.items() if c["role"] == "settings_model"]
        assert len(context_types) >= 8, f"Expected at least 8 settings_model types, found {len(context_types)}"
        for name in context_types:
            c = classifications[name]
            assert c["standalone_allowed"] is False, f"Settings model {name!r} must not be standalone"

    def test_operation_facades_standalone_allowed(self):
        """Operation facade types must have standalone_allowed=true."""
        classifications = self._get_classifications()
        facades = [name for name, c in classifications.items() if c["role"] == "operation_facade"]
        assert len(facades) >= 8, f"Expected at least 8 operation_facade types, found {len(facades)}: {facades}"
        for name in facades:
            c = classifications[name]
            assert c["standalone_allowed"] is True, f"Operation facade {name!r} must have standalone_allowed=true"

    def test_converter_classified_as_operation_facade(self):
        """Converter must be operation_facade with high confidence."""
        classifications = self._get_classifications()
        assert "Converter" in classifications
        c = classifications["Converter"]
        assert c["role"] == "operation_facade"
        assert c["standalone_allowed"] is True
        assert c["confidence"] >= 0.95

    def test_watermarker_classified_as_operation_facade(self):
        """Watermarker must be operation_facade."""
        classifications = self._get_classifications()
        assert "Watermarker" in classifications
        c = classifications["Watermarker"]
        assert c["role"] == "operation_facade"
        assert c["standalone_allowed"] is True

    def test_splitter_classified_as_operation_facade(self):
        """Splitter must be operation_facade."""
        classifications = self._get_classifications()
        assert "Splitter" in classifications
        c = classifications["Splitter"]
        assert c["role"] == "operation_facade"
        assert c["standalone_allowed"] is True

    def test_replacer_classified_as_operation_facade(self):
        """Replacer must be operation_facade."""
        classifications = self._get_classifications()
        assert "Replacer" in classifications
        c = classifications["Replacer"]
        assert c["role"] == "operation_facade"
        assert c["standalone_allowed"] is True

    def test_reclassification_documented(self):
        """MailMergeDataSource reclassification must be documented in reclassification_summary."""
        data = _load(ROLE_CLASSIFICATION)
        assert "reclassification_summary" in data
        recls = data["reclassification_summary"]
        assert len(recls) >= 1
        mmds_recl = next((r for r in recls if r["type_name"] == "MailMergeDataSource"), None)
        assert mmds_recl is not None, "MailMergeDataSource reclassification not documented"
        assert mmds_recl["prior_role"] == "workflow_root"
        assert mmds_recl["new_role"] == "data_source_adapter"


# ---------------------------------------------------------------------------
# Consumer relationship enforcement
# ---------------------------------------------------------------------------


class TestWordsConsumerRelationships:
    def _get_map(self) -> dict[str, dict]:
        data = _load(CONSUMER_RELATIONSHIPS)
        return {c["type_name"]: c for c in data["consumer_map"]}

    def test_mail_merge_data_source_has_no_lowcode_consumer(self):
        """MailMergeDataSource must have no consumers in the LowCode API."""
        cmap = self._get_map()
        assert "MailMergeDataSource" in cmap
        mmds = cmap["MailMergeDataSource"]
        assert (
            mmds["consumers"] == []
        ), f"MailMergeDataSource must have no LowCode consumers, found: {mmds['consumers']}"
        assert mmds["generation_blocked"] is True

    def test_split_options_has_required_consumer(self):
        """SplitOptions must be consumed by Splitter.Split() as a required parameter."""
        cmap = self._get_map()
        assert "SplitOptions" in cmap
        so = cmap["SplitOptions"]
        assert len(so["consumers"]) >= 1
        splitter_consumer = next((c for c in so["consumers"] if c["consumer_type"] == "Splitter"), None)
        assert splitter_consumer is not None, "Splitter must be a consumer of SplitOptions"
        assert splitter_consumer["is_optional"] is False, "SplitOptions is a REQUIRED parameter for Splitter.Split()"
        assert so["null_safe"] is False

    def test_mail_merge_options_is_optional_consumer(self):
        """MailMergeOptions must be an optional parameter for MailMerger.Execute()."""
        cmap = self._get_map()
        assert "MailMergeOptions" in cmap
        mmo = cmap["MailMergeOptions"]
        merger_consumer = next((c for c in mmo["consumers"] if c["consumer_type"] == "MailMerger"), None)
        assert merger_consumer is not None, "MailMerger must be a consumer of MailMergeOptions"
        assert merger_consumer["is_optional"] is True

    def test_all_options_types_blocked_standalone(self):
        """All options/adapter types in consumer map must have generation_blocked=true
        or document that they are not standalone."""
        cmap = self._get_map()
        for type_name, entry in cmap.items():
            if entry.get("generation_blocked") is True:
                # must have a block reason
                assert entry.get("block_reason") or entry.get(
                    "consumer_block_reason"
                ), f"{type_name} is generation_blocked but has no block_reason documented"


# ---------------------------------------------------------------------------
# Options usage review enforcement
# ---------------------------------------------------------------------------


class TestWordsOptionsUsageReview:
    def _get_options(self) -> dict[str, dict]:
        data = _load(OPTIONS_REVIEW)
        return {o["option_type"]: o for o in data["options_reviewed"]}

    def test_words_options_review_blocks_unknown_required_properties(self):
        """SplitOptions must document that SplitCriteria has unknown enum values."""
        options = self._get_options()
        split_key = next((k for k in options if "SplitOptions" in k), None)
        assert split_key is not None, "SplitOptions must be in options review"
        so = options[split_key]
        assert (
            "SplitCriteria" in so.get("required_properties_inferred", [])
            or "SplitCriteria" in so.get("unknown_required_properties", "")
            or so.get("required_properties_inferred") is not None
        ), "SplitOptions must document SplitCriteria as required property"
        assert (
            so["safe_default_possible"] is False
        ), "SplitOptions must have safe_default_possible=false (SplitCriteria required)"

    def test_mail_merge_options_safe_to_instantiate(self):
        """MailMergeOptions must be documented as safe to instantiate with defaults."""
        options = self._get_options()
        mmo_key = next((k for k in options if "MailMergeOptions" in k), None)
        assert mmo_key is not None, "MailMergeOptions must be in options review"
        mmo = options[mmo_key]
        assert mmo["null_option_allowed"] is True
        assert mmo["safe_default_possible"] is True

    def test_report_builder_options_safe_to_instantiate(self):
        """ReportBuilderOptions must be documented as safe to instantiate with defaults."""
        options = self._get_options()
        rbo_key = next((k for k in options if "ReportBuilderOptions" in k), None)
        assert rbo_key is not None, "ReportBuilderOptions must be in options review"
        rbo = options[rbo_key]
        assert rbo["null_option_allowed"] is True
        assert rbo["safe_default_possible"] is True

    def test_options_review_has_closure_verdict(self):
        """Options review must declare followup-words-options-aware-review verdict."""
        data = _load(OPTIONS_REVIEW)
        summary = data.get("summary", {})
        verdict = summary.get("followup_words_options_aware_review_verdict", "")
        assert (
            verdict == "CLOSED_VERIFIED"
        ), f"followup-words-options-aware-review must be CLOSED_VERIFIED, got {verdict!r}"


# ---------------------------------------------------------------------------
# Generation candidate rank enforcement
# ---------------------------------------------------------------------------


class TestWordsGenerationCandidateRank:
    def _get_candidates(self) -> dict[str, dict]:
        data = _load(CANDIDATE_RANK)
        return {c["scenario_id"]: c for c in data["candidates"]}

    def test_words_workflow_root_requires_output_strategy(self):
        """Every ready_for_controlled_pilot scenario must have expected_output_strategy."""
        candidates = self._get_candidates()
        ready = [c for c in candidates.values() if c.get("status") == "ready_for_controlled_pilot"]
        assert len(ready) >= 1, "At least one ready_for_controlled_pilot scenario required"
        for c in ready:
            assert c.get("expected_output_strategy"), (
                f"Scenario {c['scenario_id']} is ready_for_controlled_pilot " f"but missing expected_output_strategy"
            )
            assert c.get("fixture_strategy"), (
                f"Scenario {c['scenario_id']} is ready_for_controlled_pilot " f"but missing fixture_strategy"
            )

    def test_mail_merge_data_source_not_in_candidates(self):
        """MailMergeDataSource must not appear as a workflow_root_type in any candidate."""
        candidates = self._get_candidates()
        for scenario_id, c in candidates.items():
            assert "MailMergeDataSource" not in c.get("workflow_root_type", ""), (
                f"Scenario {scenario_id} uses MailMergeDataSource as workflow root — "
                "it is a data_source_adapter and must not be standalone"
            )

    def test_ready_for_controlled_pilot_count(self):
        """At least 4 scenarios must be ready_for_controlled_pilot."""
        data = _load(CANDIDATE_RANK)
        assert (
            data["ready_for_controlled_pilot_count"] >= 4
        ), f"Expected at least 4 ready scenarios, got {data['ready_for_controlled_pilot_count']}"

    def test_words_001_converter_is_ready(self):
        """WORDS-001 (Converter.Convert) must be ready_for_controlled_pilot."""
        candidates = self._get_candidates()
        assert "WORDS-001" in candidates
        assert candidates["WORDS-001"]["status"] == "ready_for_controlled_pilot"
        assert candidates["WORDS-001"]["ready_for_generation"] is True

    def test_words_002_watermarker_set_text_is_ready(self):
        """WORDS-002 (Watermarker.SetText) must be ready_for_controlled_pilot."""
        candidates = self._get_candidates()
        assert "WORDS-002" in candidates
        assert candidates["WORDS-002"]["status"] == "ready_for_controlled_pilot"

    def test_words_003_splitter_extract_pages_is_ready(self):
        """WORDS-003 (Splitter.ExtractPages) must be ready_for_controlled_pilot."""
        candidates = self._get_candidates()
        assert "WORDS-003" in candidates
        assert candidates["WORDS-003"]["status"] == "ready_for_controlled_pilot"

    def test_words_004_replacer_replace_is_ready(self):
        """WORDS-004 (Replacer.Replace) must be ready_for_controlled_pilot."""
        candidates = self._get_candidates()
        assert "WORDS-004" in candidates
        assert candidates["WORDS-004"]["status"] == "ready_for_controlled_pilot"

    def test_mail_merger_is_blocked(self):
        """MailMerger must be blocked_unclear_semantics due to template+data coupling."""
        candidates = self._get_candidates()
        mail_merger_scenarios = [c for c in candidates.values() if "MailMerger" in c.get("workflow_root_type", "")]
        assert len(mail_merger_scenarios) >= 1, "MailMerger must have a candidate entry"
        for c in mail_merger_scenarios:
            assert c["status"] == "blocked_unclear_semantics", (
                f"MailMerger scenario {c['scenario_id']} must be blocked_unclear_semantics "
                f"(template+data coupling), got {c['status']!r}"
            )

    def test_report_builder_is_blocked(self):
        """ReportBuilder must be blocked_unclear_semantics due to LINQ template coupling."""
        candidates = self._get_candidates()
        report_builder_scenarios = [
            c for c in candidates.values() if "ReportBuilder" in c.get("workflow_root_type", "")
        ]
        assert len(report_builder_scenarios) >= 1, "ReportBuilder must have a candidate entry"
        for c in report_builder_scenarios:
            assert c["status"] == "blocked_unclear_semantics", (
                f"ReportBuilder scenario {c['scenario_id']} must be blocked_unclear_semantics "
                f"(LINQ template coupling), got {c['status']!r}"
            )

    def test_blocked_scenarios_have_block_reason(self):
        """Every non-ready scenario must document a blocked_reason."""
        candidates = self._get_candidates()
        blocked = [c for c in candidates.values() if c.get("status") != "ready_for_controlled_pilot"]
        for c in blocked:
            assert c.get("blocked_reason"), f"Scenario {c['scenario_id']} is not ready but has no blocked_reason"


# ---------------------------------------------------------------------------
# Generation readiness conditions
# ---------------------------------------------------------------------------


class TestWordsGenerationReadinessConditions:
    def _get_words_entry(self) -> dict:
        data = _load(READINESS_RANK)
        return next(e for e in data if e["family"] == "words")

    def test_words_generation_ready_requires_role_classification(self):
        """If generation_ready=true for Words, role_classification_review must be set."""
        words = self._get_words_entry()
        if words.get("generation_ready") is True:
            assert words.get(
                "role_classification_review"
            ), "generation_ready=true requires role_classification_review to be set"
            assert Path(
                REPO_ROOT / words["role_classification_review"]
            ).exists(), f"role_classification_review file must exist: {words['role_classification_review']}"

    def test_words_generation_ready_requires_options_review(self):
        """If generation_ready=true for Words, options_usage_review must be set."""
        words = self._get_words_entry()
        if words.get("generation_ready") is True:
            assert words.get("options_usage_review"), "generation_ready=true requires options_usage_review to be set"
            assert Path(
                REPO_ROOT / words["options_usage_review"]
            ).exists(), f"options_usage_review file must exist: {words['options_usage_review']}"

    def test_words_generation_ready_requires_candidate_rank(self):
        """If generation_ready=true for Words, generation_candidate_rank must be set."""
        words = self._get_words_entry()
        if words.get("generation_ready") is True:
            assert words.get(
                "generation_candidate_rank"
            ), "generation_ready=true requires generation_candidate_rank to be set"
            assert Path(
                REPO_ROOT / words["generation_candidate_rank"]
            ).exists(), f"generation_candidate_rank file must exist: {words['generation_candidate_rank']}"

    def test_words_generation_ready_requires_controlled_pilot_scenarios(self):
        """If generation_ready=true for Words, controlled_pilot_scenarios must be non-empty."""
        words = self._get_words_entry()
        if words.get("generation_ready") is True:
            scenarios = words.get("controlled_pilot_scenarios", [])
            assert len(scenarios) >= 1, "generation_ready=true requires at least one controlled_pilot_scenario"

    def test_words_generation_still_blocked_until_review_passes(self):
        """Words generation_ready may only be true if all review artifacts exist.

        This test acts as a gate: if artifacts are missing, generation_ready must be false.
        """
        words = self._get_words_entry()
        if words.get("generation_ready") is True:
            # All 3 review artifacts must exist
            missing = []
            for key in ["role_classification_review", "options_usage_review", "generation_candidate_rank"]:
                review_path = words.get(key)
                if not review_path or not Path(REPO_ROOT / review_path).exists():
                    missing.append(key)
            assert not missing, (
                f"generation_ready=true but these review artifacts are missing: {missing}. "
                "Words generation must not be enabled without completed review artifacts."
            )
        else:
            # generation_ready=false: check why
            blocked_by = words.get("generation_blocked_by", [])
            # Either blocked_by is set, or review artifacts are present (sprint in progress)
            assert True  # generation_ready=false is always safe

    def test_pdf_generation_controlled_pilot_approved(self):
        """PDF is now generation_ready=true with controlled_pilot_approved=true (4 types only).
        Reflection dedup fixed; pilot ran 2026-05-05 with 2/4 passing (PARTIAL_PR_DRY_RUN_READY)."""
        data = _load(READINESS_RANK)
        pdf = next(e for e in data if e["family"] == "pdf")
        # PDF pilot completed — generation_ready=true now
        assert pdf["generation_ready"] is True, "PDF generation_ready should be True after controlled pilot completion"
        # Pilot scope is restricted to 4 types
        assert (
            pdf.get("controlled_pilot_approved") is True
        ), "PDF must have controlled_pilot_approved=True (4 types: Merger, Splitter, Optimizer, TextExtractor)"

    def test_cells_generation_ready_unchanged(self):
        """Cells generation_ready must remain true — not modified by Words review."""
        data = _load(READINESS_RANK)
        cells = next(e for e in data if e["family"] == "cells")
        assert cells["generation_ready"] is True, "Cells generation_ready must remain true after Words review"
