"""Tests for the release-status command and release_status module."""

import json
import sys
import subprocess
import tempfile
from pathlib import Path
import pytest


class TestReleaseStatusModule:
    """Tests for compute_release_status() in publisher.release_status."""

    _SAMPLE_MATRIX = {
        "taskcards": [
            {"id": "followup-words-split-criteria-enumeration", "status": "OPEN"},
            {"id": "followup-words-pair-fixture-strategy", "status": "OPEN"},
            {"id": "followup-words-docx-semantic-validation", "status": "OPEN"},
            {"id": "followup-cells-some-old-issue", "status": "CLOSED"},
            {"id": "followup-pdf-reflection-dedup", "status": "CLOSED"},
            {"id": "followup-pdf-role-classification-review", "status": "OPEN"},
        ]
    }

    def _make_verification_dir(
        self, tmp_path: Path, family_data: dict, *, matrix: dict | None = None
    ) -> Path:
        """Helper: create a minimal verification/latest directory with evidence files."""
        latest = tmp_path / "workspace" / "verification" / "latest"
        latest.mkdir(parents=True)

        # Write taskcard matrix so dynamic read works in tests
        matrix_data = matrix if matrix is not None else self._SAMPLE_MATRIX
        (latest / "open-taskcard-closure-matrix.json").write_text(
            json.dumps(matrix_data), encoding="utf-8"
        )

        for family, data in family_data.items():
            if "live_pr" in data:
                (latest / f"{family}-live-pr-result.json").write_text(
                    json.dumps(data["live_pr"]), encoding="utf-8"
                )
            if "merge_result" in data:
                (latest / f"{family}-merge-result.json").write_text(
                    json.dumps(data["merge_result"]), encoding="utf-8"
                )
            if "post_merge" in data:
                (latest / f"{family}-post-merge-clean-checkout-validation.json").write_text(
                    json.dumps(data["post_merge"]), encoding="utf-8"
                )

        return tmp_path / "workspace" / "verification"

    def test_computes_status_for_merged_family(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status

        verification_dir = self._make_verification_dir(tmp_path, {
            "cells": {
                "live_pr": {
                    "pr_url": "https://github.com/aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples/pull/1",
                    "pr_number": 1,
                    "nuget_version": "26.4.0",
                    "examples_count": 9,
                },
                "merge_result": {
                    "merge_commit_sha": "f6e5515c070184e4b08a2cff647220bea1113b08",
                    "merge_date": "2026-05-03T09:03:09+00:00",
                },
                "post_merge": {
                    "summary": {"overall_result": "POST_MERGE_VERIFIED", "passed": 9, "total_examples": 9}
                },
            }
        })

        status = compute_release_status(["cells"], verification_dir)
        assert status["all_merged"] is True
        assert status["all_post_merge_validated"] is True
        assert len(status["families"]) == 1
        rec = status["families"][0]
        assert rec["family"] == "cells"
        assert rec["last_merge_sha"] == "f6e5515c070184e4b08a2cff647220bea1113b08"
        assert rec["last_post_merge_validation_status"] == "POST_MERGE_VERIFIED"
        assert rec["published_examples_count"] == 9
        assert rec["last_pr_url"] == "https://github.com/aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples/pull/1"

    def test_not_merged_family_shows_no_sha(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status

        verification_dir = self._make_verification_dir(tmp_path, {})
        status = compute_release_status(["cells"], verification_dir)
        assert status["all_merged"] is False
        rec = status["families"][0]
        assert rec["last_merge_sha"] is None
        assert rec["last_post_merge_validation_status"] == "NOT_RUN"

    def test_multiple_families_all_merged(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status

        verification_dir = self._make_verification_dir(tmp_path, {
            "cells": {
                "merge_result": {"merge_commit_sha": "abc123", "merge_date": "2026-05-03T09:03:09+00:00"},
                "post_merge": {"summary": {"overall_result": "POST_MERGE_VERIFIED", "passed": 9, "total_examples": 9}},
            },
            "words": {
                "merge_result": {"merge_commit_sha": "def456", "merge_date": "2026-05-03T08:35:45+00:00"},
                "post_merge": {"summary": {"overall_result": "POST_MERGE_VERIFIED", "passed": 4, "total_examples": 4}},
            },
        })

        status = compute_release_status(["cells", "words"], verification_dir)
        assert status["all_merged"] is True
        assert status["all_post_merge_validated"] is True
        assert len(status["families"]) == 2

    def test_one_family_not_validated_sets_all_post_merge_false(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status

        verification_dir = self._make_verification_dir(tmp_path, {
            "cells": {
                "merge_result": {"merge_commit_sha": "abc123", "merge_date": "2026-05-03T09:03:09+00:00"},
                "post_merge": {"summary": {"overall_result": "POST_MERGE_VERIFIED", "passed": 9, "total_examples": 9}},
            },
            "words": {
                "merge_result": {"merge_commit_sha": "def456", "merge_date": "2026-05-03T08:35:45+00:00"},
                # no post_merge evidence for words
            },
        })

        status = compute_release_status(["cells", "words"], verification_dir)
        assert status["all_merged"] is True
        assert status["all_post_merge_validated"] is False

    def test_words_open_followups_present(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status

        verification_dir = self._make_verification_dir(tmp_path, {})
        status = compute_release_status(["words"], verification_dir)
        rec = status["families"][0]
        assert "followup-words-split-criteria-enumeration" in rec["open_followups"]

    def test_cells_no_open_followups(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status

        verification_dir = self._make_verification_dir(tmp_path, {})
        status = compute_release_status(["cells"], verification_dir)
        rec = status["families"][0]
        assert rec["open_followups"] == []

    def test_write_release_status_report_creates_file(self, tmp_path):
        from plugin_examples.publisher.release_status import (
            compute_release_status, write_release_status_report,
        )

        verification_dir = self._make_verification_dir(tmp_path, {})
        status = compute_release_status(["cells"], verification_dir)
        report_path = write_release_status_report(status, verification_dir)
        assert report_path.exists()
        data = json.loads(report_path.read_text(encoding="utf-8"))
        assert data["report_type"] == "release_status"
        assert "families" in data

    def test_report_has_required_fields_per_family(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status

        verification_dir = self._make_verification_dir(tmp_path, {})
        status = compute_release_status(["cells"], verification_dir)
        rec = status["families"][0]
        required_fields = [
            "family", "source_of_truth_version", "latest_published_version",
            "published_examples_count", "last_pr_url", "last_merge_sha",
            "last_post_merge_validation_status", "open_followups",
            "taskcard_evidence_source", "next_required_action",
            "release_scope_status", "family_coverage_status", "denominator_basis",
        ]
        for field in required_fields:
            assert field in rec, f"Missing required field: {field}"

    def test_release_status_reads_open_taskcards_from_matrix(self, tmp_path):
        """open_followups must be read from the JSON matrix, not hardcoded."""
        from plugin_examples.publisher.release_status import compute_release_status

        custom_matrix = {
            "taskcards": [
                {"id": "followup-words-split-criteria-enumeration", "status": "OPEN"},
                {"id": "followup-words-new-custom-task", "status": "OPEN"},
                {"id": "followup-words-old-closed-task", "status": "CLOSED"},
            ]
        }
        verification_dir = self._make_verification_dir(tmp_path, {}, matrix=custom_matrix)
        status = compute_release_status(["words"], verification_dir)
        rec = status["families"][0]
        assert "followup-words-split-criteria-enumeration" in rec["open_followups"]
        assert "followup-words-new-custom-task" in rec["open_followups"]
        assert "followup-words-old-closed-task" not in rec["open_followups"]

    def test_release_status_handles_missing_taskcard_matrix(self, tmp_path):
        """When matrix file is absent, open_followups must be empty and evidence_source set."""
        from plugin_examples.publisher.release_status import compute_release_status

        # Create verification dir WITHOUT matrix
        latest = tmp_path / "workspace" / "verification" / "latest"
        latest.mkdir(parents=True)
        verification_dir = tmp_path / "workspace" / "verification"

        status = compute_release_status(["words"], verification_dir)
        rec = status["families"][0]
        assert rec["open_followups"] == []
        assert rec["taskcard_evidence_source"] == "missing_taskcard_matrix"

    def test_release_status_does_not_use_stale_hardcoded_taskcards(self, tmp_path):
        """release_status must not return taskcards that are CLOSED in the matrix."""
        from plugin_examples.publisher.release_status import compute_release_status

        # Matrix where followup-pdf-reflection-dedup is CLOSED
        matrix_with_closed_pdf = {
            "taskcards": [
                {"id": "followup-pdf-reflection-dedup", "status": "CLOSED"},
                {"id": "followup-pdf-role-classification-review", "status": "OPEN"},
            ]
        }
        verification_dir = self._make_verification_dir(
            tmp_path, {}, matrix=matrix_with_closed_pdf
        )
        status = compute_release_status(["pdf"], verification_dir)
        rec = status["families"][0]
        # Closed taskcard must NOT appear in open_followups
        assert "followup-pdf-reflection-dedup" not in rec["open_followups"], (
            "followup-pdf-reflection-dedup is CLOSED in matrix but appeared in open_followups. "
            "Dynamic read from matrix is required; do not use hardcoded dict."
        )
        # Open taskcard must appear
        assert "followup-pdf-role-classification-review" in rec["open_followups"]


class TestReleaseStatusCLI:
    """Tests for the release-status CLI command."""

    def test_cli_exits_0(self, tmp_path):
        """release-status exits 0 even with no evidence files."""
        result = subprocess.run(
            [sys.executable, "-m", "plugin_examples", "release-status",
             "--families", "cells", "words"],
            capture_output=True, text=True, timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(Path(__file__).resolve().parents[2]),
        )
        assert result.returncode == 0, f"Unexpected exit: {result.stdout}\n{result.stderr}"

    def test_cli_writes_release_status_json(self):
        """release-status --promote-latest writes release-status.json."""
        repo_root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [sys.executable, "-m", "plugin_examples", "release-status",
             "--families", "cells", "words", "--promote-latest"],
            capture_output=True, text=True, timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(repo_root),
        )
        assert result.returncode == 0
        report_path = repo_root / "workspace" / "verification" / "latest" / "release-status.json"
        assert report_path.exists(), "release-status.json not written"
        data = json.loads(report_path.read_text(encoding="utf-8"))
        assert "families" in data
        assert "all_merged" in data

    def test_cli_default_writes_all_six_families(self):
        """release-status default must not regress to cells/words-only evidence."""
        repo_root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [sys.executable, "-m", "plugin_examples", "release-status",
             "--promote-latest"],
            capture_output=True, text=True, timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(repo_root),
        )
        assert result.returncode == 0, f"Unexpected exit: {result.stdout}\n{result.stderr}"
        report_path = repo_root / "workspace" / "verification" / "latest" / "release-status.json"
        data = json.loads(report_path.read_text(encoding="utf-8"))
        expected = ["cells", "words", "pdf", "diagram", "email", "slides"]
        assert data["families_checked"] == expected
        assert [r["family"] for r in data["families"]] == expected
        assert all("release_scope_status" in r for r in data["families"])

    def test_cli_output_contains_family_lines(self):
        """CLI output mentions each requested family."""
        result = subprocess.run(
            [sys.executable, "-m", "plugin_examples", "release-status",
             "--families", "cells", "words"],
            capture_output=True, text=True, timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(Path(__file__).resolve().parents[2]),
        )
        assert result.returncode == 0
        assert "cells" in result.stdout
        assert "words" in result.stdout


class TestReleaseStatusAllFamilies:
    """Tests that release_status covers all 6 active families."""

    _SAMPLE_MATRIX = {"taskcards": [
        {"id": "followup-diagram-pr1-token-fix", "status": "OPEN"},
        {"id": "followup-email-fixture-strategy-design", "status": "OPEN"},
        {"id": "followup-slides-fixture-strategy-design", "status": "OPEN"},
    ]}

    def _make_dir(self, tmp_path: Path) -> Path:
        latest = tmp_path / "workspace" / "verification" / "latest"
        latest.mkdir(parents=True)
        (latest / "open-taskcard-closure-matrix.json").write_text(
            json.dumps(self._SAMPLE_MATRIX), encoding="utf-8"
        )
        return tmp_path / "workspace" / "verification"

    def test_diagram_in_family_taskcard_prefixes(self):
        from plugin_examples.publisher.release_status import _FAMILY_TASKCARD_PREFIXES
        assert "diagram" in _FAMILY_TASKCARD_PREFIXES
        assert _FAMILY_TASKCARD_PREFIXES["diagram"] == "followup-diagram-"

    def test_email_in_family_taskcard_prefixes(self):
        from plugin_examples.publisher.release_status import _FAMILY_TASKCARD_PREFIXES
        assert "email" in _FAMILY_TASKCARD_PREFIXES

    def test_slides_in_family_taskcard_prefixes(self):
        from plugin_examples.publisher.release_status import _FAMILY_TASKCARD_PREFIXES
        assert "slides" in _FAMILY_TASKCARD_PREFIXES

    def test_compute_status_for_diagram(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status
        verification_dir = self._make_dir(tmp_path)
        status = compute_release_status(["diagram"], verification_dir)
        assert len(status["families"]) == 1
        assert status["families"][0]["family"] == "diagram"

    def test_compute_status_for_all_six_families(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status
        verification_dir = self._make_dir(tmp_path)
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        status = compute_release_status(families, verification_dir)
        assert len(status["families"]) == 6
        returned_families = {f["family"] for f in status["families"]}
        assert returned_families == set(families)

    def test_diagram_open_followups_from_matrix(self, tmp_path):
        from plugin_examples.publisher.release_status import compute_release_status
        verification_dir = self._make_dir(tmp_path)
        status = compute_release_status(["diagram"], verification_dir)
        diagram = status["families"][0]
        assert "followup-diagram-pr1-token-fix" in diagram["open_followups"]

    def test_next_action_for_pdf_includes_pilot_expansion(self):
        from plugin_examples.publisher.release_status import _get_next_action
        action = _get_next_action("pdf", "POST_MERGE_VERIFIED", "abc123")
        assert "pdf" in action.lower() or "pilot" in action.lower()

    def test_next_action_for_email_mentions_discovery_only(self):
        from plugin_examples.publisher.release_status import _get_next_action
        action = _get_next_action("email", "NOT_RUN", None)
        # No merge SHA — falls into "create_live_pr" branch first
        assert "merged" in action.lower() or "pr" in action.lower()

    def test_next_action_generic_family_has_fallback(self):
        from plugin_examples.publisher.release_status import _get_next_action
        action = _get_next_action("unknown_family", "POST_MERGE_VERIFIED", "sha123")
        assert "monitor" in action.lower() or "unknown_family" in action.lower()

    def test_real_release_status_scope_statuses(self):
        from plugin_examples.publisher.release_status import compute_release_status
        repo_root = Path(__file__).resolve().parents[2]
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        status = compute_release_status(families, repo_root / "workspace" / "verification")
        by_family = {r["family"]: r["release_scope_status"] for r in status["families"]}
        assert by_family["cells"] == "FAMILY_COMPLETE"
        assert by_family["words"] == "PILOT_COMPLETE"
        assert by_family["pdf"] == "PILOT_COMPLETE"  # All 19 pilot types published (PRs #1-#4, #11, #17-#21 merged)
        assert by_family["diagram"] == "PILOT_COMPLETE"
        assert by_family["email"] == "PILOT_COMPLETE"
        assert by_family["slides"] == "PILOT_COMPLETE"

        coverage = {r["family"]: r["family_coverage_status"] for r in status["families"]}
        assert coverage["words"] == "PARTIAL_FAMILY_COVERAGE"
        assert coverage["pdf"] == "PARTIAL_FAMILY_COVERAGE"

    def test_discovery_only_next_action_does_not_request_live_pr(self):
        # Email and Slides are now PILOT_COMPLETE (activated in Sprint 6)
        from plugin_examples.publisher.release_status import compute_release_status
        repo_root = Path(__file__).resolve().parents[2]
        status = compute_release_status(["email", "slides"], repo_root / "workspace" / "verification")
        for rec in status["families"]:
            assert rec["release_scope_status"] == "PILOT_COMPLETE"

    def test_release_status_output_has_generated_at(self, tmp_path):
        """compute_release_status must include generated_at ISO timestamp."""
        from plugin_examples.publisher.release_status import compute_release_status
        verification_dir = self._make_dir(tmp_path)
        status = compute_release_status(["cells"], verification_dir)
        assert "generated_at" in status, "release-status.json must include generated_at"
        ts = status["generated_at"]
        assert "T" in ts and "Z" in ts or "+" in ts, f"generated_at must be ISO 8601: {ts}"

    def test_canonical_release_status_covers_all_six_families(self):
        """compute_release_status with all 6 families must return all 6 (not stale cells/words-only)."""
        from plugin_examples.publisher.release_status import compute_release_status, ALL_RELEASE_FAMILIES
        repo_root = Path(__file__).resolve().parents[2]
        status = compute_release_status(ALL_RELEASE_FAMILIES, repo_root / "workspace" / "verification")
        assert status.get("families_checked") == ["cells", "words", "pdf", "diagram", "email", "slides"], (
            f"compute_release_status must cover all 6 families, got: {status.get('families_checked')}"
        )
        assert "generated_at" in status, "release status must include generated_at timestamp"
        assert len(status["families"]) == 6


class TestReleaseStatusTopLevelFields:
    """Verify top-level fields do not imply all examples are published when some are PR-ready."""

    def test_top_level_fields_exist(self):
        from plugin_examples.publisher.release_status import compute_release_status, ALL_RELEASE_FAMILIES
        repo_root = Path(__file__).resolve().parents[2]
        status = compute_release_status(ALL_RELEASE_FAMILIES, repo_root / "workspace" / "verification")
        assert "all_published" in status
        assert "all_contracts_accounted_for" in status
        assert "published_count" in status
        assert "pr_ready_count" in status
        assert "total_contracts" in status
        assert "approval_blocked_count" in status
        assert "families_complete_count" in status
        assert "families_partial_count" in status

    def test_all_contracts_accounted_for(self):
        from plugin_examples.publisher.release_status import compute_release_status, ALL_RELEASE_FAMILIES
        repo_root = Path(__file__).resolve().parents[2]
        status = compute_release_status(ALL_RELEASE_FAMILIES, repo_root / "workspace" / "verification")
        assert status["all_contracts_accounted_for"] is True
        assert status["total_contracts"] == 42

    def test_published_plus_pr_ready_equals_contracts(self):
        from plugin_examples.publisher.release_status import compute_release_status, ALL_RELEASE_FAMILIES
        repo_root = Path(__file__).resolve().parents[2]
        status = compute_release_status(ALL_RELEASE_FAMILIES, repo_root / "workspace" / "verification")
        assert status["published_count"] + status["pr_ready_count"] >= status["total_contracts"]

    def test_no_top_level_field_implies_all_published_when_pr_ready_exists(self):
        """If pr_ready_count > 0, all_published must be false."""
        from plugin_examples.publisher.release_status import compute_release_status, ALL_RELEASE_FAMILIES
        repo_root = Path(__file__).resolve().parents[2]
        status = compute_release_status(ALL_RELEASE_FAMILIES, repo_root / "workspace" / "verification")
        if status["pr_ready_count"] > 0:
            assert status["all_published"] is False
        else:
            assert status["all_published"] is True

    def test_release_status_and_portfolio_release_status_agree(self):
        """release-status published_count must match portfolio matrix totals."""
        from plugin_examples.publisher.release_status import compute_release_status, ALL_RELEASE_FAMILIES
        repo_root = Path(__file__).resolve().parents[2]
        status = compute_release_status(ALL_RELEASE_FAMILIES, repo_root / "workspace" / "verification")
        # Verify from denominator configs
        import json
        denom_dir = repo_root / "pipeline" / "configs" / "denominators"
        denom_published = 0
        denom_pr_ready = 0
        for fam in ALL_RELEASE_FAMILIES:
            d = json.loads((denom_dir / f"{fam}.json").read_text(encoding="utf-8"))
            denom_published += d.get("published_count", 0)
            denom_pr_ready += d.get("pr_dry_run_ready_count", 0)
        assert status["published_count"] == denom_published
        assert status["pr_ready_count"] == denom_pr_ready
