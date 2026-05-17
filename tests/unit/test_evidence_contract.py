"""
Tests for the strict evidence contract.

Verifies that:
- A thin 17-file bundle like Sprint 27 fails validation.
- Missing final git status causes failure.
- Missing final verdict causes failure.
- Missing PR package audits cause failure.
- Missing raw test log causes failure.
- Missing all-family scoreboard causes failure.
- Missing taskcard reconciliation causes failure.
- A complete bundle passes validation.
- Secret scanning works.
"""

import json
import zipfile
from pathlib import Path

import pytest

from plugin_examples.evidence_contract import (
    REQUIRED_CATEGORIES,
    StrictEvidenceContract,
    contract_definition,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_zip(tmp_path: Path, files: dict[str, str]) -> Path:
    """Create a ZIP at tmp_path/bundle.zip with the given filename→content map."""
    zip_path = tmp_path / "bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return zip_path


def _minimal_complete_files() -> dict[str, str]:
    """Return a file dict satisfying every required category."""
    files = {
        "git-status-initial.txt": "## clean",
        "git-status-final.txt": "## clean",
        "git-diff-initial.patch": "diff --git a/x b/x",
        "git-diff-final.patch": "diff --git a/x b/x",
        "git-log-proof.txt": "abc1234 feat: sprint28",
        "changed-files.txt": "src/plugin_examples/evidence_contract.py",
        "source-state-classification.json": json.dumps({"verdict": "CLEAN"}),
        "test-summary.json": json.dumps({"passed": 1616, "failed": 0}),
        "test-full.log": "1616 passed in 30s",
        "final-verdict.md": "# SPRINT28_APPROVAL_BLOCKED_FINAL_CLOSEOUT_COMPLETE",
        "final-state-summary.yaml": "sprint: sprint28\nverdict: APPROVAL_BLOCKED",
        "bundle-contract-definition.json": json.dumps({"contract_version": "1.0.0"}),
        "bundle-contract-validation-report.json": json.dumps({"verdict": "BUNDLE_CONTRACT_PASSED"}),
        "publication-mode-decision.json": json.dumps({"gate": "BLOCKED"}),
        "github-token-readiness-report.json": json.dumps({"gh_token": "SET"}),
        "pdf-pr3-approval-blocked.md": "# PR#3 approval blocked",
        "pdf-pr5-approval-blocked.md": "# PR#5 approval blocked",
        "pdf-pr6-approval-blocked.md": "# PR#6 approval blocked",
        "pdf-pr7-approval-blocked.md": "# PR#7 approval blocked",
        "pdf-pr8-approval-blocked.md": "# PR#8 approval blocked",
        "pdf-pr9-approval-blocked.md": "# PR#9 approval blocked",
        "post-publication-not-run-approval-blocked.md": "# Post-pub not run",
        "pdf-formimporter-defect-package-final-report.json": json.dumps({"status": "CONFIRMED"}),
        "pdf-formimporter-upstream-issue-final.md": "# FormImporter bug",
        "pdf-final-denominator-closeout-matrix.json": json.dumps({"total": 101}),
        "pdf-maximum-achievable-coverage-report.md": "# Max coverage",
        "email-final-runtime-status.json": json.dumps({"status": "5/5 PASS"}),
        "slides-final-runtime-status.json": json.dumps({"status": "6/6 PASS"}),
        "words-final-guard-report.json": json.dumps({"verdict": "REGRESSION_FREE"}),
        "cells-final-guard-report.json": json.dumps({"verdict": "REGRESSION_FREE"}),
        "diagram-final-guard-report.json": json.dumps({"verdict": "REGRESSION_FREE"}),
        "all-family-launch-scoreboard.json": json.dumps({"families": 6}),
        "all-family-launch-scoreboard.md": "# All-Family Scoreboard",
        "families-needing-launch-work.json": json.dumps({"families": []}),
        "release-state-reconciliation-report.json": json.dumps({"state": "OK"}),
        "taskcard-reconciliation-report.json": json.dumps({"open": 5}),
        "taskcard-state-after-sprint28.json": json.dumps({"sprint": "sprint28"}),
    }
    return files


# ---------------------------------------------------------------------------
# Sprint 27 thin bundle test
# ---------------------------------------------------------------------------

class TestThinBundleFailsSprint27:
    def test_sprint27_17_file_bundle_fails(self, tmp_path):
        """Sprint 27 thin 17-file bundle must fail the strict contract."""
        sprint27_files = {
            "Program.cs": "using System;",
            "formimporter-repro.csproj": "<Project/>",
            "template-first-registry-audit.json": "{}",
            "all-family-scoreboard.json": "{}",
            "signature-wave-g-pr9-evidence.json": "{}",
            "formimporter-wave-h-assessment.json": "{}",
            "pdf-denominator-closeout-matrix.json": "{}",
            "sprint26-bundle-contract-validation-report.json": "{}",
            "sprint26-evidence-bundle-audit.json": "{}",
            "sprint26-commit-proof.json": "{}",
            "email-converttohtml-cleanup-hardening-report.json": "{}",
            "publication-mode-decision.json": "{}",
            "pdf-formimporter-defect-repro-report.json": "{}",
            "pdf-formimporter-upstream-issue-draft.md": "# draft",
            "pdf-final-denominator-closeout-matrix.json": "{}",
            "slides-target-runtime-verification-report.json": "{}",
            "test-summary.json": "{}",
        }
        zip_path = _make_zip(tmp_path, sprint27_files)
        result = StrictEvidenceContract().validate_zip(zip_path)

        assert not result.passed, "Sprint 27 thin bundle should fail"
        assert result.verdict == "BUNDLE_CONTRACT_FAILED"
        # Must fail on multiple categories
        assert len(result.categories_missing) >= 10, (
            f"Expected ≥10 missing categories, got {len(result.categories_missing)}"
        )


# ---------------------------------------------------------------------------
# Individual requirement tests
# ---------------------------------------------------------------------------

class TestMissingRequiredArtifacts:
    def test_missing_git_status_final_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["git-status-final.txt"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "git_status_final" in result.categories_missing

    def test_missing_git_diff_final_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["git-diff-final.patch"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "git_diff_final" in result.categories_missing

    def test_missing_final_verdict_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["final-verdict.md"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "final_verdict" in result.categories_missing

    def test_missing_final_state_summary_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["final-state-summary.yaml"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "final_state_summary" in result.categories_missing

    def test_missing_pr3_audit_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["pdf-pr3-approval-blocked.md"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "pr3_audit_or_result" in result.categories_missing

    def test_missing_pr5_audit_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["pdf-pr5-approval-blocked.md"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "pr5_audit_or_result" in result.categories_missing

    def test_missing_pr6_audit_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["pdf-pr6-approval-blocked.md"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "pr6_audit_or_result" in result.categories_missing

    def test_missing_pr7_audit_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["pdf-pr7-approval-blocked.md"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "pr7_audit_or_result" in result.categories_missing

    def test_missing_pr8_audit_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["pdf-pr8-approval-blocked.md"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "pr8_audit_or_result" in result.categories_missing

    def test_missing_pr9_audit_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["pdf-pr9-approval-blocked.md"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "pr9_audit_or_result" in result.categories_missing

    def test_missing_raw_test_log_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["test-full.log"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "test_full_log" in result.categories_missing

    def test_missing_all_family_scoreboard_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["all-family-launch-scoreboard.json"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "all_family_scoreboard_json" in result.categories_missing

    def test_missing_taskcard_reconciliation_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["taskcard-reconciliation-report.json"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "taskcard_reconciliation" in result.categories_missing

    def test_missing_git_status_initial_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["git-status-initial.txt"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "git_status_initial" in result.categories_missing

    def test_missing_bundle_contract_definition_fails(self, tmp_path):
        files = _minimal_complete_files()
        del files["bundle-contract-definition.json"]
        result = StrictEvidenceContract().validate_zip(_make_zip(tmp_path, files))
        assert not result.passed
        assert "bundle_contract_definition" in result.categories_missing


# ---------------------------------------------------------------------------
# Complete bundle passes
# ---------------------------------------------------------------------------

class TestCompleteBundlePasses:
    def test_complete_bundle_passes(self, tmp_path):
        """A bundle with all required artifacts must pass validation."""
        files = _minimal_complete_files()
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContract().validate_zip(zip_path)

        assert result.passed, f"Expected pass but got failures: {result.failures}"
        assert result.verdict == "BUNDLE_CONTRACT_PASSED"
        assert len(result.categories_missing) == 0
        assert len(result.categories_found) == len(REQUIRED_CATEGORIES)

    def test_complete_bundle_with_publication_result_passes(self, tmp_path):
        """Bundle with pdf-pr3-publication-result.json (not approval-blocked) also passes."""
        files = _minimal_complete_files()
        del files["pdf-pr3-approval-blocked.md"]
        files["pdf-pr3-publication-result.json"] = json.dumps({"pr_url": "https://github.com/..."})
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContract().validate_zip(zip_path)
        assert result.passed, f"Expected pass but got: {result.failures}"

    def test_test_full_not_run_md_satisfies_test_log_category(self, tmp_path):
        """test-full-not-run.md can substitute for test-full.log."""
        files = _minimal_complete_files()
        del files["test-full.log"]
        files["test-full-not-run.md"] = "# Test full not run — approval blocked sprint"
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContract().validate_zip(zip_path)
        assert result.passed, f"Expected pass but got: {result.failures}"

    def test_post_publication_verification_satisfies_post_pub_category(self, tmp_path):
        """post-publication-pr-verification-report.json can satisfy post_publication category."""
        files = _minimal_complete_files()
        del files["post-publication-not-run-approval-blocked.md"]
        files["post-publication-pr-verification-report.json"] = json.dumps({"prs": []})
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContract().validate_zip(zip_path)
        assert result.passed


# ---------------------------------------------------------------------------
# Secret scanning
# ---------------------------------------------------------------------------

class TestSecretScanning:
    def test_raw_github_classic_pat_causes_failure(self, tmp_path):
        files = _minimal_complete_files()
        # Inject a fake classic PAT pattern (not a real token)
        files["git-log-proof.txt"] = "ghp_" + "A" * 36
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContract().validate_zip(zip_path)
        assert not result.passed
        assert len(result.secret_violations) >= 1

    def test_clean_content_no_secret_violations(self, tmp_path):
        files = _minimal_complete_files()
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContract().validate_zip(zip_path)
        assert result.secret_violations == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_nonexistent_zip_fails(self, tmp_path):
        result = StrictEvidenceContract().validate_zip(tmp_path / "nonexistent.zip")
        assert not result.passed
        assert result.verdict == "BUNDLE_CONTRACT_FAILED"

    def test_bad_zip_fails(self, tmp_path):
        bad = tmp_path / "bad.zip"
        bad.write_text("not a zip file")
        result = StrictEvidenceContract().validate_zip(bad)
        assert not result.passed

    def test_contract_definition_has_all_categories(self):
        defn = contract_definition()
        assert defn["contract_version"] == "1.0.0"
        assert set(defn["required_categories"].keys()) == set(REQUIRED_CATEGORIES.keys())
        assert defn["min_categories_required"] == len(REQUIRED_CATEGORIES)

    def test_required_categories_count(self):
        """Ensure contract has at least 36 required categories for completeness."""
        assert len(REQUIRED_CATEGORIES) >= 36, (
            f"Contract only has {len(REQUIRED_CATEGORIES)} categories — too few"
        )
