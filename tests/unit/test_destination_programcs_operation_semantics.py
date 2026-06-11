"""Sprint 67 Phase 5 — Destination Program.cs operation semantics tests.

Verifies that sprint67 content-audit records have correct operation_kind,
that API type names are consistent with operation_kind, and that records
for multi-cardinality types have appropriate cardinality markers.
"""

import json
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[2]
AUDIT_PATH = REPO / "reports/sprint67/destination/content-audit-sprint67.json"

VALID_OPERATION_KINDS = {"converter", "transform", "merger", "splitter", "extractor", "exporter", "processor"}

# Expected operation_kind per API type (selected known cases)
EXPECTED_OP_KINDS = {
    "HtmlConverter": "converter",
    "ImageConverter": "converter",
    "JsonConverter": "converter",
    "PdfConverter": "converter",
    "SpreadsheetConverter": "converter",
    "TextConverter": "converter",
    "SpreadsheetMerger": "merger",
    "SpreadsheetSplitter": "splitter",
    "SpreadsheetLocker": "transform",
    "Merger": "merger",
    "Splitter": "splitter",
    "Converter": "converter",
    "Watermarker": "transform",
    "Replacer": "transform",
    "MailMerger": "processor",
    "ReportBuilder": "processor",
    "Comparer": "converter",
    "TextExtractor": "extractor",
    "ImageExtractor": "extractor",
    "FormFlattener": "transform",
    "FormEditor": "transform",
    "FormExporter": "exporter",
    "Optimizer": "transform",
    "Security": "transform",
    "TocGenerator": "processor",
    "TableGenerator": "processor",
    "Signature": "transform",
}


def load_audit():
    if not AUDIT_PATH.exists():
        pytest.skip(f"content-audit-sprint67.json not found at {AUDIT_PATH}")
    data = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    return data.get("records", [])


class TestContentAuditOperationSemantics:
    """content-audit-sprint67.json must have correct operation semantics."""

    def test_audit_has_42_records(self):
        records = load_audit()
        assert len(records) == 42, f"Expected 42 records, got {len(records)}"

    def test_all_records_have_scenario_id(self):
        records = load_audit()
        missing = [r for r in records if not r.get("scenario_id")]
        assert not missing, f"{len(missing)} records missing scenario_id"

    def test_all_records_have_operation_kind(self):
        records = load_audit()
        missing = [r.get("scenario_id", "?") for r in records if not r.get("operation_kind")]
        assert not missing, f"Records missing operation_kind: {missing}"

    def test_all_operation_kinds_are_valid(self):
        records = load_audit()
        invalid = [
            (r.get("scenario_id"), r.get("operation_kind"))
            for r in records
            if r.get("operation_kind") not in VALID_OPERATION_KINDS
        ]
        assert not invalid, f"Invalid operation_kind values: {invalid}"

    def test_expected_operation_kinds_match(self):
        """Known API types must have the expected operation_kind."""
        records = load_audit()
        violations = []
        for rec in records:
            api_type = rec.get("api_type", "")
            expected = EXPECTED_OP_KINDS.get(api_type)
            if expected is not None:
                actual = rec.get("operation_kind", "")
                if actual != expected:
                    violations.append(
                        f"{rec['scenario_id']}: api_type={api_type!r} " f"expected={expected!r} actual={actual!r}"
                    )
        assert not violations, f"operation_kind mismatches:\n" + "\n".join(violations)

    def test_pdf_records_have_26_5_version(self):
        """After S66-D2 resolution, all PDF records must use 26.5.0."""
        records = load_audit()
        pdf_old = [r["scenario_id"] for r in records if r["family"] == "pdf" and r.get("package_version") == "26.4.0"]
        assert not pdf_old, f"PDF records still have old version 26.4.0: {pdf_old}"

    def test_no_sprint64_paths_in_handoff_path(self):
        """S66-D3 fix: handoff_path must not reference sprint64."""
        records = load_audit()
        stale = [
            r["scenario_id"]
            for r in records
            if "sprint64" in r.get("handoff_path", "") or "sprint66" in r.get("handoff_path", "")
        ]
        assert not stale, f"Records with stale handoff_path refs: {stale}"

    def test_no_sprint64_paths_in_local_package_path(self):
        """S66-D3 fix: local_package_path must not reference sprint64."""
        records = load_audit()
        stale = [
            r["scenario_id"]
            for r in records
            if "sprint64" in r.get("local_package_path", "") or "sprint66" in r.get("local_package_path", "")
        ]
        assert not stale, f"Records with stale local_package_path refs: {stale}"

    def test_merger_records_have_merger_operation_kind(self):
        """All records with 'merger' in scenario_id must have operation_kind=merger."""
        records = load_audit()
        violations = [
            (r["scenario_id"], r.get("operation_kind"))
            for r in records
            if "-merger" in r["scenario_id"]
            and r.get("operation_kind") != "merger"
            and "mail-merger" not in r["scenario_id"]
        ]
        assert not violations, f"Merger scenarios with wrong operation_kind: {violations}"

    def test_splitter_records_have_splitter_operation_kind(self):
        """All records with 'splitter' in scenario_id must have operation_kind=splitter."""
        records = load_audit()
        violations = [
            (r["scenario_id"], r.get("operation_kind"))
            for r in records
            if "-splitter" in r["scenario_id"] and r.get("operation_kind") != "splitter"
        ]
        assert not violations, f"Splitter scenarios with wrong operation_kind: {violations}"

    def test_output_kind_not_blank_for_all_records(self):
        """All records must have non-blank output_kind (S65-D4 guard)."""
        records = load_audit()
        blank = [r["scenario_id"] for r in records if not r.get("output_kind")]
        assert not blank, f"Records with blank output_kind: {blank}"
