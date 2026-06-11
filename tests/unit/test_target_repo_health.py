"""Tests for the target repo health checker module (Sprint 36 SYS-2)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.publisher.target_repo_health import (
    TARGET_REPOS,
    RepoHealthResult,
    TargetRepoHealthReport,
    run_target_repo_health_check,
)


# ---------------------------------------------------------------------------
# Unit tests for TARGET_REPOS configuration
# ---------------------------------------------------------------------------


class TestTargetReposConfiguration:
    def test_all_six_lowcode_families_defined(self):
        expected = {"cells", "words", "pdf", "diagram", "email", "slides"}
        assert expected == set(TARGET_REPOS.keys())

    def test_cells_expected_count(self):
        assert TARGET_REPOS["cells"]["expected_examples"] == 9

    def test_words_expected_count(self):
        assert TARGET_REPOS["words"]["expected_examples"] == 8

    def test_pdf_expected_count(self):
        assert TARGET_REPOS["pdf"]["expected_examples"] == 5

    def test_pdf_has_pending_count(self):
        assert TARGET_REPOS["pdf"]["pending_examples"] == 14

    def test_diagram_expected_count(self):
        assert TARGET_REPOS["diagram"]["expected_examples"] == 2

    def test_email_expected_count(self):
        assert TARGET_REPOS["email"]["expected_examples"] == 1

    def test_slides_expected_count(self):
        assert TARGET_REPOS["slides"]["expected_examples"] == 3

    def test_all_have_main_branch(self):
        for family, cfg in TARGET_REPOS.items():
            assert cfg["branch"] == "main", f"{family} branch should be main"

    def test_pdf_status_partial_canary(self):
        assert TARGET_REPOS["pdf"]["status"] == "PARTIAL_CANARY"

    def test_cells_status_family_complete(self):
        assert TARGET_REPOS["cells"]["status"] == "FAMILY_COMPLETE"


# ---------------------------------------------------------------------------
# Tests for run_target_repo_health_check
# ---------------------------------------------------------------------------


def _write_readme_audit_evidence(tmp_path: Path, family: str) -> None:
    """Create evidence file that target_repo_health falls back to."""
    latest_dir = tmp_path / "workspace" / "verification" / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)
    audit_file = latest_dir / f"{family}-root-readme-audit.json"
    audit_file.write_text(
        json.dumps({"family": family, "passed": True, "source": "evidence"}),
        encoding="utf-8",
    )


class TestRunTargetRepoHealthCheck:
    def test_evidence_based_fallback_when_gh_unavailable(self, tmp_path):
        """When gh CLI is unavailable, falls back to README audit evidence."""
        _write_readme_audit_evidence(tmp_path, "cells")

        with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
            report = run_target_repo_health_check(families=["cells"], repo_root=tmp_path)

        assert len(report.families) == 1
        r = report.families[0]
        assert r.family == "cells"
        assert r.verification_method == "EVIDENCE_BASED"
        assert r.status == "EVIDENCE_BASED"
        assert report.evidence_based_count == 1

    def test_no_evidence_marks_inaccessible(self, tmp_path):
        """When gh fails AND no evidence files exist, marks repo as INACCESSIBLE."""
        with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
            report = run_target_repo_health_check(families=["cells"], repo_root=tmp_path)

        assert report.inaccessible_count == 1
        assert report.families[0].status == "INACCESSIBLE"

    def test_gh_cli_success_marks_healthy(self, tmp_path):
        """When gh CLI returns successfully, marks repo as HEALTHY."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"name": "Aspose.Cells.LowCode-for-.NET-Examples"})

        with patch("subprocess.run", return_value=mock_result):
            report = run_target_repo_health_check(families=["cells"], repo_root=tmp_path)

        assert report.healthy_count == 1
        assert report.families[0].status == "HEALTHY"
        assert report.families[0].verification_method == "GH_CLI"

    def test_unknown_family_skipped(self, tmp_path):
        report = run_target_repo_health_check(families=["nonexistent_family"], repo_root=tmp_path)
        assert len(report.families) == 0

    def test_all_families_checked_by_default(self, tmp_path):
        """Default run checks all six LowCode families."""
        with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
            report = run_target_repo_health_check(repo_root=tmp_path)

        assert len(report.families) == 6

    def test_to_dict_structure(self, tmp_path):
        _write_readme_audit_evidence(tmp_path, "words")

        with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
            report = run_target_repo_health_check(families=["words"], repo_root=tmp_path)

        d = report.to_dict()
        assert "generated_at" in d
        assert "families" in d
        assert d["families"][0]["family"] == "words"
        assert "expected_examples" in d["families"][0]

    def test_overall_verdict_all_verified_when_healthy(self, tmp_path):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"name": "repo"})

        with patch("subprocess.run", return_value=mock_result):
            report = run_target_repo_health_check(families=["cells", "words"], repo_root=tmp_path)

        assert report.overall_verdict == "ALL_VERIFIED"

    def test_partial_verification_when_some_evidence(self, tmp_path):
        """Mix of evidence-based and inaccessible → PARTIAL_VERIFICATION."""
        _write_readme_audit_evidence(tmp_path, "cells")
        # No evidence for words

        with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
            report = run_target_repo_health_check(families=["cells", "words"], repo_root=tmp_path)

        assert report.overall_verdict == "PARTIAL_VERIFICATION"
        assert report.inaccessible_count >= 1

    def test_pdf_expected_examples_is_5_not_19(self, tmp_path):
        """PDF target repo currently has 5 published examples, not the full 19."""
        cfg = TARGET_REPOS["pdf"]
        assert cfg["expected_examples"] == 5
        assert cfg["pending_examples"] == 14
