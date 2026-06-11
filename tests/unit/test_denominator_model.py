"""Tests for denominator model files (pipeline/configs/denominators/*.json).

Verifies that denominator files exist, parse as valid JSON, conform to schema,
and are internally consistent with family lifecycle records.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DENOMINATOR_DIR = REPO_ROOT / "pipeline" / "configs" / "denominators"
SCHEMA_PATH = REPO_ROOT / "pipeline" / "schemas" / "denominator.schema.json"
FAMILIES_DIR = REPO_ROOT / "workspace" / "verification" / "latest" / "families"

FAMILIES = ["cells", "words", "pdf", "diagram", "email", "slides"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_denominator(family: str) -> dict:
    path = DENOMINATOR_DIR / f"{family}.json"
    assert path.exists(), f"Denominator file missing: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _load_schema() -> dict:
    assert SCHEMA_PATH.exists(), f"Denominator schema missing: {SCHEMA_PATH}"
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Existence tests (REM-001 / REM-002 / REM-003)
# ---------------------------------------------------------------------------


class TestDenominatorFilesExist:
    def test_cells_denominator_exists(self):
        assert (DENOMINATOR_DIR / "cells.json").exists()

    def test_words_denominator_exists(self):
        assert (DENOMINATOR_DIR / "words.json").exists()

    def test_pdf_denominator_exists(self):
        assert (DENOMINATOR_DIR / "pdf.json").exists()

    def test_diagram_denominator_exists(self):
        assert (DENOMINATOR_DIR / "diagram.json").exists()

    def test_email_denominator_exists(self):
        assert (DENOMINATOR_DIR / "email.json").exists()

    def test_slides_denominator_exists(self):
        assert (DENOMINATOR_DIR / "slides.json").exists()

    def test_denominator_schema_exists(self):
        assert SCHEMA_PATH.exists()


# ---------------------------------------------------------------------------
# Parse tests
# ---------------------------------------------------------------------------


class TestDenominatorFilesParseValidJson:
    @pytest.mark.parametrize("family", FAMILIES)
    def test_denominator_parses_as_valid_json(self, family: str):
        d = _load_denominator(family)
        assert isinstance(d, dict), f"{family} denominator is not a JSON object"

    def test_schema_parses_as_valid_json(self):
        s = _load_schema()
        assert isinstance(s, dict)
        assert s.get("$schema") is not None


# ---------------------------------------------------------------------------
# Schema validation tests (REM-004)
# ---------------------------------------------------------------------------


class TestDenominatorSchemaValidation:
    @pytest.mark.parametrize("family", FAMILIES)
    def test_denominator_schema_validates_for_family(self, family: str):
        """Each denominator file must have all required fields per schema."""
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed — skipping schema validation")

        schema = _load_schema()
        d = _load_denominator(family)
        jsonschema.validate(instance=d, schema=schema)

    @pytest.mark.parametrize("family", FAMILIES)
    def test_denominator_has_required_fields(self, family: str):
        d = _load_denominator(family)
        required = [
            "family",
            "source_package",
            "source_version",
            "api_catalog_sha256",
            "plugin_namespace",
            "total_lowcode_types",
            "denominator_basis",
            "runnable_scenarios",
            "published_count",
            "excluded_count",
            "evidence_sources",
            "last_verified_at",
        ]
        for field in required:
            assert field in d, f"Missing required field '{field}' in {family} denominator"

    @pytest.mark.parametrize("family", FAMILIES)
    def test_denominator_family_field_matches_filename(self, family: str):
        d = _load_denominator(family)
        assert d["family"] == family, f"family field '{d['family']}' != filename '{family}'"


# ---------------------------------------------------------------------------
# Cells-specific tests (REM-001)
# ---------------------------------------------------------------------------


class TestCellsDenominator:
    def setup_method(self):
        self.d = _load_denominator("cells")

    def test_cells_total_types_is_22(self):
        assert (
            self.d["total_lowcode_types"] == 22
        ), f"Cells total_lowcode_types should be 22 (from SOT proof), got {self.d['total_lowcode_types']}"

    def test_cells_workflow_root_types_is_9(self):
        assert (
            self.d["workflow_root_types"] == 9
        ), f"Cells workflow_root_types should be 9 (confirmed by lifecycle), got {self.d['workflow_root_types']}"

    def test_cells_published_count_is_9(self):
        assert (
            self.d["published_count"] == 9
        ), f"Cells published_count should be 9 (all scenarios reviewer_passed), got {self.d['published_count']}"

    def test_cells_excluded_count_is_13(self):
        assert self.d["excluded_count"] == 13, f"Cells excluded_count should be 13, got {self.d['excluded_count']}"

    def test_cells_runnable_scenarios_is_9(self):
        assert self.d["runnable_scenarios"] == 9

    def test_cells_denominator_basis_is_full_sot(self):
        assert self.d["denominator_basis"] == "FULL_SOT"

    def test_cells_allowed_pilot_types_is_null(self):
        assert (
            self.d["allowed_pilot_types"] is None
        ), "Cells has no allowed_types restriction; allowed_pilot_types must be null"

    def test_cells_coverage_pct_of_runnable_is_100(self):
        pct = self.d.get("coverage_pct_of_runnable")
        assert pct is not None and abs(pct - 100.0) < 0.01

    def test_cells_api_catalog_sha256_present(self):
        sha = self.d["api_catalog_sha256"]
        assert len(sha) == 64, "SHA256 must be 64 hex chars"

    def test_cells_total_equals_runnable_plus_excluded(self):
        total = self.d["total_lowcode_types"]
        runnable = self.d["runnable_scenarios"]
        excluded = self.d["excluded_count"]
        assert (
            total == runnable + excluded
        ), f"Cells: total_lowcode_types ({total}) != runnable ({runnable}) + excluded ({excluded})"

    def test_cells_runnable_scenario_ids_count_matches(self):
        ids = self.d.get("runnable_scenario_ids")
        assert ids is not None and len(ids) == self.d["runnable_scenarios"]


# ---------------------------------------------------------------------------
# Words-specific tests (REM-002)
# ---------------------------------------------------------------------------


class TestWordsDenominator:
    def setup_method(self):
        self.d = _load_denominator("words")

    def test_words_total_types_is_25(self):
        assert self.d["total_lowcode_types"] == 25

    def test_words_pilot_allowed_count_is_8(self):
        assert self.d["allowed_pilot_count"] == 8

    def test_words_allowed_pilot_types_present(self):
        types = self.d["allowed_pilot_types"]
        assert isinstance(types, list) and len(types) == 8
        for t in [
            "Converter",
            "Watermarker",
            "Splitter",
            "Replacer",
            "Merger",
            "Comparer",
            "MailMerger",
            "ReportBuilder",
        ]:
            assert t in types, f"Words allowed_pilot_types missing '{t}'"
        assert "Processor" not in types, "Processor must NOT be in allowed_pilot_types (API investigation required)"

    def test_words_published_count_is_8(self):
        assert self.d["published_count"] == 8

    def test_words_workflow_root_types_is_classified(self):
        assert self.d["workflow_root_types"] == 9
        assert self.d["non_runnable_types"] == 16

    def test_words_excluded_count_is_17(self):
        assert self.d["excluded_count"] == 17

    def test_words_runnable_scenarios_is_8(self):
        assert self.d["runnable_scenarios"] == 8

    def test_words_denominator_basis_is_pilot_allowed(self):
        assert (
            self.d["denominator_basis"] == "PILOT_ALLOWED"
        ), "Words is in pilot mode; denominator_basis must be PILOT_ALLOWED"

    def test_words_coverage_pct_of_pilot_runnable_is_100(self):
        pct = self.d.get("coverage_pct_of_pilot_runnable")
        assert pct is not None and abs(pct - 100.0) < 0.1

    def test_words_does_not_claim_full_sot_basis(self):
        assert (
            self.d["denominator_basis"] != "FULL_SOT"
        ), "Words must NOT claim FULL_SOT denominator_basis — type classification incomplete"

    def test_words_total_equals_pilot_plus_excluded(self):
        total = self.d["total_lowcode_types"]
        pilot = self.d["allowed_pilot_count"]
        excluded = self.d["excluded_count"]
        assert total == pilot + excluded, f"Words: total ({total}) != pilot ({pilot}) + excluded ({excluded})"

    def test_words_full_sot_classification_evidence_present(self):
        sources = self.d["evidence_sources"]
        assert "workspace/verification/latest/words-full-sot-type-classification.json" in sources

    def test_words_total_equals_runnable_plus_non_runnable(self):
        total = self.d["total_lowcode_types"]
        runnable = self.d["workflow_root_types"]
        non_runnable = self.d["non_runnable_types"]
        assert (
            total == runnable + non_runnable
        ), f"Words: total ({total}) != runnable ({runnable}) + non_runnable ({non_runnable})"


# ---------------------------------------------------------------------------
# PDF-specific tests (REM-003)
# ---------------------------------------------------------------------------


class TestPdfDenominator:
    def setup_method(self):
        self.d = _load_denominator("pdf")

    def test_pdf_total_types_is_101(self):
        assert self.d["total_lowcode_types"] == 101

    def test_pdf_workflow_root_types_is_22(self):
        assert self.d["workflow_root_types"] == 22, (
            "PdfExtractor reclassified ABSTRACT_BASE Sprint 7 (25->24); "
            "PdfToImage reclassified ABSTRACT_BASE Sprint 22 (24->23); "
            "SelectField reclassified PROVIDER_CALLBACK Sprint 24 (23->22)"
        )

    def test_pdf_pilot_allowed_count_is_19(self):
        assert (
            self.d["allowed_pilot_count"] == 19
        ), "PDF pilot expanded to 19 types in Sprint 26 (Wave G: Signature added to Wave A=5 + Wave B=3 + Wave C=3 + Wave D=3 + Wave E=2 + Wave F=2)"

    def test_pdf_allowed_pilot_types_present(self):
        types = self.d["allowed_pilot_types"]
        assert isinstance(types, list) and len(types) == 19
        for t in [
            "Merger",
            "TextExtractor",
            "Splitter",
            "Optimizer",
            "PdfAConverter",
            "DocConverter",
            "XlsConverter",
            "Html",
            "Jpeg",
            "Png",
            "Tiff",
            "TocGenerator",
            "TableGenerator",
            "ImageExtractor",
            "Security",
            "FormFlattener",
            "FormEditor",
            "FormExporter",
            "Signature",
        ]:
            assert t in types, f"PDF allowed_pilot_types missing '{t}'"

    def test_pdf_published_count_is_19(self):
        assert (
            self.d["published_count"] == 19
        ), f"PDF published_count should be 19 (all pilot-allowed types published via PRs #1,#2,#4,#11,#17-#21), got {self.d['published_count']}"

    def test_pdf_denominator_basis_is_pilot_allowed(self):
        assert self.d["denominator_basis"] == "PILOT_ALLOWED"

    def test_pdf_workflow_root_separates_from_pilot(self):
        wf = self.d["workflow_root_types"]
        pilot = self.d["allowed_pilot_count"]
        assert wf > pilot, f"PDF workflow_root_types ({wf}) must exceed allowed_pilot_count ({pilot})"

    def test_pdf_coverage_pct_detail_present(self):
        detail = self.d.get("coverage_pct_detail")
        assert isinstance(detail, dict), "PDF must have coverage_pct_detail dict"
        for key in ["pilot_allowed", "workflow_root", "full_sot"]:
            assert key in detail, f"coverage_pct_detail missing key: {key}"

    def test_pdf_api_catalog_sha256_present(self):
        sha = self.d["api_catalog_sha256"]
        assert len(sha) == 64

    def test_pdf_excluded_count_is_82(self):
        assert self.d["excluded_count"] == 82, "Wave G adds Signature to pilot (19 total) — excluded 101-19=82"

    def test_pdf_runnable_scenarios_is_19(self):
        assert (
            self.d["runnable_scenarios"] == 19
        ), "PDF pilot expanded to 19 types in Sprint 26 (Wave A=5 + Wave B=3 + Wave C=3 + Wave D=3 + Wave E=2 + Wave F=2 + Wave G=1)"


# ---------------------------------------------------------------------------
# Diagram-specific tests
# ---------------------------------------------------------------------------


class TestDiagramDenominator:
    def setup_method(self):
        self.d = _load_denominator("diagram")

    def test_diagram_total_types_is_5(self):
        assert self.d["total_lowcode_types"] == 5

    def test_diagram_workflow_root_types_is_2(self):
        assert self.d["workflow_root_types"] == 2

    def test_diagram_published_count_is_2(self):
        assert self.d["published_count"] == 2

    def test_diagram_excluded_count_is_3(self):
        assert self.d["excluded_count"] == 3

    def test_diagram_runnable_scenarios_is_2(self):
        assert self.d["runnable_scenarios"] == 2

    def test_diagram_denominator_basis_is_pilot_allowed(self):
        assert self.d["denominator_basis"] == "PILOT_ALLOWED"

    def test_diagram_coverage_pct_of_workflow_root_is_100(self):
        pct = self.d.get("coverage_pct_of_workflow_root")
        assert pct is not None and abs(pct - 100.0) < 0.01

    def test_diagram_total_equals_runnable_plus_excluded(self):
        total = self.d["total_lowcode_types"]
        runnable = self.d["runnable_scenarios"]
        excluded = self.d["excluded_count"]
        assert total == runnable + excluded

    def test_diagram_runnable_scenario_ids_count_matches(self):
        ids = self.d.get("runnable_scenario_ids")
        assert ids is not None and len(ids) == self.d["runnable_scenarios"]


# ---------------------------------------------------------------------------
# Email-specific tests
# ---------------------------------------------------------------------------


class TestEmailDenominator:
    def setup_method(self):
        self.d = _load_denominator("email")

    def test_email_total_types_is_3(self):
        assert self.d["total_lowcode_types"] == 3

    def test_email_workflow_root_types_is_1(self):
        assert self.d["workflow_root_types"] == 1

    def test_email_published_count_is_1(self):
        assert self.d["published_count"] == 1

    def test_email_excluded_count_is_2(self):
        assert self.d["excluded_count"] == 2

    def test_email_runnable_scenarios_is_1(self):
        assert self.d["runnable_scenarios"] == 1

    def test_email_denominator_basis_is_pilot_allowed(self):
        assert self.d["denominator_basis"] == "PILOT_ALLOWED"

    def test_email_coverage_pct_of_workflow_root_is_100(self):
        pct = self.d.get("coverage_pct_of_workflow_root")
        assert pct is not None and abs(pct - 100.0) < 0.01

    def test_email_total_equals_runnable_plus_excluded(self):
        total = self.d["total_lowcode_types"]
        runnable = self.d["runnable_scenarios"]
        excluded = self.d["excluded_count"]
        assert total == runnable + excluded


# ---------------------------------------------------------------------------
# Slides-specific tests
# ---------------------------------------------------------------------------


class TestSlidesDenominator:
    def setup_method(self):
        self.d = _load_denominator("slides")

    def test_slides_total_types_is_5(self):
        assert self.d["total_lowcode_types"] == 5

    def test_slides_workflow_root_types_is_3(self):
        assert self.d["workflow_root_types"] == 3

    def test_slides_published_count_is_3(self):
        assert self.d["published_count"] == 3

    def test_slides_excluded_count_is_2(self):
        assert self.d["excluded_count"] == 2

    def test_slides_runnable_scenarios_is_3(self):
        assert self.d["runnable_scenarios"] == 3

    def test_slides_denominator_basis_is_pilot_allowed(self):
        assert self.d["denominator_basis"] == "PILOT_ALLOWED"

    def test_slides_coverage_pct_of_workflow_root_is_100(self):
        pct = self.d.get("coverage_pct_of_workflow_root")
        assert pct is not None and abs(pct - 100.0) < 0.01

    def test_slides_allowed_pilot_types_present(self):
        types = self.d["allowed_pilot_types"]
        assert isinstance(types, list) and len(types) == 3
        for t in ["Compress", "Convert", "Merger"]:
            assert t in types

    def test_slides_total_equals_runnable_plus_excluded(self):
        total = self.d["total_lowcode_types"]
        runnable = self.d["runnable_scenarios"]
        excluded = self.d["excluded_count"]
        assert total == runnable + excluded

    def test_slides_runnable_scenario_ids_count_matches(self):
        ids = self.d.get("runnable_scenario_ids")
        assert ids is not None and len(ids) == self.d["runnable_scenarios"]


# ---------------------------------------------------------------------------
# Cross-family consistency tests
# ---------------------------------------------------------------------------


class TestDenominatorCrossFamily:
    @pytest.mark.parametrize("family", FAMILIES)
    def test_published_count_does_not_exceed_runnable(self, family: str):
        d = _load_denominator(family)
        assert (
            d["published_count"] <= d["runnable_scenarios"]
        ), f"{family}: published_count ({d['published_count']}) > runnable_scenarios ({d['runnable_scenarios']})"

    @pytest.mark.parametrize("family", FAMILIES)
    def test_evidence_sources_non_empty(self, family: str):
        d = _load_denominator(family)
        assert len(d["evidence_sources"]) >= 1

    @pytest.mark.parametrize("family", FAMILIES)
    def test_api_catalog_sha256_is_64_hex_chars_or_null(self, family: str):
        d = _load_denominator(family)
        sha = d["api_catalog_sha256"]
        if sha is None:
            pytest.skip(f"{family} has no reflection-generated catalog (sha256 is null)")
        assert len(sha) == 64 and all(c in "0123456789abcdefABCDEF" for c in sha)

    @pytest.mark.parametrize("family", FAMILIES)
    def test_denominator_basis_is_valid_value(self, family: str):
        d = _load_denominator(family)
        assert d["denominator_basis"] in {"FULL_SOT", "WORKFLOW_ROOT", "PILOT_ALLOWED"}

    def test_total_published_across_families_is_42(self):
        """Integration: total published examples across all 6 families."""
        total = sum(_load_denominator(f)["published_count"] for f in FAMILIES)
        assert total == 42, (
            f"Total published count across all 6 families should be 42 "
            f"(Cells=9, Words=8, PDF=19, Diagram=2, Email=1, Slides=3), got {total}"
        )

    @pytest.mark.parametrize("family", FAMILIES)
    def test_conservation_equation(self, family: str):
        """Sum of all terminal runnable buckets = runnable_scenarios.

        Known terminal buckets:
        - published_count: merged and verified in target repo
        - pr_ready_count: open live PRs awaiting merge
        - pr_dry_run_ready_count: validated dry-run awaiting APPROVE_LIVE_PR
        - reviewer_passed_awaiting_pr_count: reviewer passed, no PR package yet
        - blocked_count: blocked by technical issues
        """
        d = _load_denominator(family)
        buckets = {
            "published_count": d.get("published_count", 0),
            "pr_ready_count": d.get("pr_ready_count", 0) or 0,
            "pr_dry_run_ready_count": d.get("pr_dry_run_ready_count", 0) or 0,
            "reviewer_passed_awaiting_pr_count": d.get("reviewer_passed_awaiting_pr_count", 0) or 0,
            "blocked_count": d.get("blocked_count", 0) or 0,
        }
        total = sum(buckets.values())
        runnable = d["runnable_scenarios"]
        bucket_str = " + ".join(f"{k}={v}" for k, v in buckets.items() if v > 0)
        assert total == runnable, (
            f"{family}: conservation equation failed: " f"{bucket_str} = {total} != runnable_scenarios ({runnable})"
        )
