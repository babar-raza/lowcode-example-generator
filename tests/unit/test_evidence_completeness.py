"""Tests for the evidence completeness gate (REM-008).

Verifies:
- check_completeness returns COMPLETE when all expected files exist
- check_completeness returns INCOMPLETE when files are missing
- CompletionResult schema is correct
- write_completeness_report writes valid JSON
- GLOBAL_AGGREGATE_ALLOWLIST and FAMILY_SCOPED_EVIDENCE_FILES are consistent
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from plugin_examples.gates.evidence_completeness import (
    ALWAYS_EXPECTED,
    EXPECTED_FAMILY_EVIDENCE_FILES,
    CompletionResult,
    check_completeness,
    write_completeness_report,
)
from plugin_examples.evidence_layout import (
    FAMILY_SCOPED_EVIDENCE_FILES,
    GLOBAL_AGGREGATE_ALLOWLIST,
)


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_evidence_dir(tmp_path: Path) -> Path:
    """Create a temporary evidence_dir/latest/ with all expected files."""
    latest = tmp_path / "evidence" / "latest"
    latest.mkdir(parents=True)
    return tmp_path / "evidence"


def _populate_all_files(evidence_dir: Path) -> None:
    """Populate evidence_dir/latest/ with all expected evidence files."""
    latest = evidence_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    for filename in EXPECTED_FAMILY_EVIDENCE_FILES:
        (latest / filename).write_text("{}", encoding="utf-8")


def _populate_partial_files(evidence_dir: Path, skip: list[str]) -> None:
    """Populate evidence_dir/latest/ with all files EXCEPT those in skip."""
    latest = evidence_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    for filename in EXPECTED_FAMILY_EVIDENCE_FILES:
        if filename not in skip:
            (latest / filename).write_text("{}", encoding="utf-8")


# ---------------------------------------------------------------------------
# TestEvidenceCompleteness
# ---------------------------------------------------------------------------


class TestEvidenceCompletenessGate:
    def test_complete_when_all_files_present(self, tmp_evidence_dir: Path):
        _populate_all_files(tmp_evidence_dir)
        result = check_completeness("cells", tmp_evidence_dir, run_id="test-run")
        assert result.status == "COMPLETE"
        assert result.total_missing == 0
        assert result.completeness_pct == 100.0
        assert len(result.missing_files) == 0

    def test_incomplete_when_file_missing(self, tmp_evidence_dir: Path):
        missing = ["aggregate-gate-results.json", "validation-results.json"]
        _populate_partial_files(tmp_evidence_dir, skip=missing)
        result = check_completeness("cells", tmp_evidence_dir, run_id="test-run")
        assert result.status == "INCOMPLETE"
        assert result.total_missing == 2
        for f in missing:
            assert f in result.missing_files

    def test_error_when_latest_dir_missing(self, tmp_path: Path):
        # No evidence_dir/latest/ created
        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir()
        result = check_completeness("words", evidence_dir, run_id="test-run")
        assert result.status == "ERROR"
        assert result.total_found == 0
        assert result.total_missing == len(EXPECTED_FAMILY_EVIDENCE_FILES)

    def test_result_family_field_matches_input(self, tmp_evidence_dir: Path):
        _populate_all_files(tmp_evidence_dir)
        result = check_completeness("pdf", tmp_evidence_dir, run_id="test-run")
        assert result.family == "pdf"

    def test_result_run_id_field_matches_input(self, tmp_evidence_dir: Path):
        _populate_all_files(tmp_evidence_dir)
        result = check_completeness("cells", tmp_evidence_dir, run_id="pilot-cells-20260508-133932")
        assert result.run_id == "pilot-cells-20260508-133932"

    def test_completeness_pct_partial(self, tmp_evidence_dir: Path):
        # Skip half the files
        all_files = list(EXPECTED_FAMILY_EVIDENCE_FILES)
        skip = all_files[:11]  # Skip 11 of 22
        _populate_partial_files(tmp_evidence_dir, skip=skip)
        result = check_completeness("cells", tmp_evidence_dir, run_id="test-run")
        expected_pct = ((len(EXPECTED_FAMILY_EVIDENCE_FILES) - 11) / len(EXPECTED_FAMILY_EVIDENCE_FILES)) * 100
        assert abs(result.completeness_pct - expected_pct) < 0.1

    def test_blocking_mode_raises_on_always_expected_missing(self, tmp_evidence_dir: Path):
        # Skip an always-expected file
        always_file = next(iter(ALWAYS_EXPECTED))
        _populate_partial_files(tmp_evidence_dir, skip=[always_file])
        with pytest.raises(RuntimeError, match="Evidence completeness gate FAILED"):
            check_completeness("cells", tmp_evidence_dir, run_id="test-run", mode="BLOCKING")

    def test_warning_mode_does_not_raise_on_missing(self, tmp_evidence_dir: Path):
        # Missing always-expected file — WARNING mode should not raise
        always_file = next(iter(ALWAYS_EXPECTED))
        _populate_partial_files(tmp_evidence_dir, skip=[always_file])
        result = check_completeness("cells", tmp_evidence_dir, run_id="test-run", mode="WARNING")
        assert result.status == "INCOMPLETE"
        assert result.mode == "WARNING"

    def test_to_dict_has_required_keys(self, tmp_evidence_dir: Path):
        _populate_all_files(tmp_evidence_dir)
        result = check_completeness("cells", tmp_evidence_dir, run_id="test-run")
        d = result.to_dict()
        for key in [
            "family",
            "run_id",
            "checked_at",
            "evidence_dir",
            "total_expected",
            "total_found",
            "total_missing",
            "missing_files",
            "found_files",
            "completeness_pct",
            "status",
            "mode",
        ]:
            assert key in d, f"Missing key in CompletionResult.to_dict(): {key}"


# ---------------------------------------------------------------------------
# TestWriteCompletenessReport
# ---------------------------------------------------------------------------


class TestWriteCompletenessReport:
    def test_writes_valid_json(self, tmp_path: Path, tmp_evidence_dir: Path):
        _populate_all_files(tmp_evidence_dir)
        result = check_completeness("cells", tmp_evidence_dir, run_id="test-run")
        out_path = write_completeness_report(result, tmp_path)
        assert out_path.exists()
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert data["status"] == "COMPLETE"
        assert data["family"] == "cells"

    def test_creates_output_dir_if_missing(self, tmp_path: Path, tmp_evidence_dir: Path):
        _populate_all_files(tmp_evidence_dir)
        result = check_completeness("cells", tmp_evidence_dir, run_id="test-run")
        nested_dir = tmp_path / "families" / "cells"
        assert not nested_dir.exists()
        write_completeness_report(result, nested_dir)
        assert nested_dir.exists()
        assert (nested_dir / "evidence-completeness-check.json").exists()

    def test_filename_is_standard(self, tmp_path: Path, tmp_evidence_dir: Path):
        _populate_all_files(tmp_evidence_dir)
        result = check_completeness("cells", tmp_evidence_dir, run_id="test-run")
        out_path = write_completeness_report(result, tmp_path)
        assert out_path.name == "evidence-completeness-check.json"


# ---------------------------------------------------------------------------
# TestEvidenceLayoutConsistency (REM-007)
# ---------------------------------------------------------------------------


class TestEvidenceLayoutConsistency:
    def test_global_aggregate_allowlist_is_frozenset(self):
        assert isinstance(GLOBAL_AGGREGATE_ALLOWLIST, frozenset)

    def test_global_aggregate_allowlist_non_empty(self):
        assert len(GLOBAL_AGGREGATE_ALLOWLIST) > 0

    def test_family_scoped_files_do_not_overlap_with_allowlist(self):
        overlap = FAMILY_SCOPED_EVIDENCE_FILES & GLOBAL_AGGREGATE_ALLOWLIST
        assert len(overlap) == 0, (
            f"Files should not be in both FAMILY_SCOPED_EVIDENCE_FILES and " f"GLOBAL_AGGREGATE_ALLOWLIST: {overlap}"
        )

    def test_expected_evidence_files_matches_family_scoped(self):
        """EXPECTED_FAMILY_EVIDENCE_FILES must match FAMILY_SCOPED_EVIDENCE_FILES."""
        assert EXPECTED_FAMILY_EVIDENCE_FILES == FAMILY_SCOPED_EVIDENCE_FILES, (
            "EXPECTED_FAMILY_EVIDENCE_FILES in evidence_completeness.py must match "
            "FAMILY_SCOPED_EVIDENCE_FILES in evidence_layout.py. "
            f"Diff: {EXPECTED_FAMILY_EVIDENCE_FILES ^ FAMILY_SCOPED_EVIDENCE_FILES}"
        )

    def test_always_expected_is_subset_of_expected(self):
        assert ALWAYS_EXPECTED.issubset(EXPECTED_FAMILY_EVIDENCE_FILES), (
            f"ALWAYS_EXPECTED must be a subset of EXPECTED_FAMILY_EVIDENCE_FILES. "
            f"Extra: {ALWAYS_EXPECTED - EXPECTED_FAMILY_EVIDENCE_FILES}"
        )
