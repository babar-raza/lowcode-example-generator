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
    ALLOWED_VERDICTS_V2,
    COMBINED_CATEGORIES_V2,
    MIN_CATEGORIES_REQUIRED_V2,
    REQUIRED_CATEGORIES,
    StrictEvidenceContract,
    StrictEvidenceContractV2,
    contract_definition,
    contract_definition_v2,
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


# ---------------------------------------------------------------------------
# Helper for v2 complete bundle
# ---------------------------------------------------------------------------

def _minimal_v2_complete_files() -> dict[str, str]:
    """Return files satisfying all 45 v2 required categories with valid content."""
    return {
        # v1 categories (updated/kept)
        "git-status-initial.txt": "?? plans/\n M workspace/manifests/example-index.json",
        "git-status-final.txt": "?? plans/\n M workspace/manifests/example-index.json",
        "git-diff-initial.patch": "diff --git a/x b/x\nindex 000..111\n+added",
        "git-diff-final.patch": "diff --git a/x b/x\nindex 000..111\n+added",
        "git-log-proof.txt": "20686d3 feat(sprint28): SPRINT28_STRICT_EVIDENCE_CONTRACT\n774f516 feat(sprint27)\n",
        "changed-files.txt": "src/plugin_examples/evidence_contract.py",
        "source-state-classification.json": json.dumps({"source_dirty": False}),
        "test-summary.json": json.dumps({"passed": 1650, "failed": 0, "total": 1650}),
        "test-full.log": "1650 passed in 35s",
        "test-targeted.log": "10 passed in 1s",
        "final-verdict.md": "# SPRINT29_APPROVAL_BLOCKED_EVIDENCE_CONTRACT_V2_COMPLETE",
        "final-state-summary.yaml": "sprint: sprint29\nverdict: APPROVAL_BLOCKED_V2\nhead: 20686d3",
        "bundle-contract-definition.json": json.dumps({"contract_version": "2.0.0"}),
        "bundle-contract-validation-report.json": json.dumps({
            "passed": True, "categories_missing": [], "verdict": "BUNDLE_CONTRACT_PASSED"
        }),
        "publication-mode-decision.json": json.dumps({"mode": "APPROVAL_BLOCKED"}),
        "github-token-readiness-report.json": json.dumps({"status": "TOKEN_VALID"}),
        "pdf-pr3-final-package-audit.json": json.dumps({"status": "PASS"}),
        "pdf-pr3-version-policy-report.json": json.dumps({"version": "26.4.0", "policy": "PUBLISH_AS_IS"}),
        "pdf-pr3-approval-blocked.md": "# PR#3 approval blocked",
        "pdf-pr5-final-package-audit.json": json.dumps({"status": "PASS"}),
        "pdf-pr5-version-policy-report.json": json.dumps({"version": "26.4.0", "policy": "PUBLISH_AS_IS"}),
        "pdf-pr5-approval-blocked.md": "# PR#5 approval blocked",
        "pdf-pr6-final-package-audit.json": json.dumps({"status": "PASS"}),
        "pdf-pr6-version-policy-report.json": json.dumps({"version": "26.4.0", "policy": "PUBLISH_AS_IS"}),
        "pdf-pr6-approval-blocked.md": "# PR#6 approval blocked",
        "pdf-pr7-final-package-audit.json": json.dumps({"status": "PASS"}),
        "pdf-pr7-approval-blocked.md": "# PR#7 approval blocked",
        "pdf-pr8-final-package-audit.json": json.dumps({"status": "PASS"}),
        "pdf-pr8-approval-blocked.md": "# PR#8 approval blocked",
        "pdf-pr9-final-package-audit.json": json.dumps({"status": "PASS"}),
        "pdf-pr9-approval-blocked.md": "# PR#9 approval blocked",
        "post-publication-not-run-approval-blocked.md": "# Post-pub not run",
        "pdf-formimporter-defect-package-final-report.json": json.dumps({"status": "WAVE_H_DEFERRED"}),
        "pdf-formimporter-defect-package-final-check.json": json.dumps({"status": "CONFIRMED"}),
        "pdf-formimporter-upstream-issue-final.md": "# FormImporter upstream issue",
        "pdf-final-denominator-closeout-matrix.json": json.dumps({"total": 101}),
        "email-final-runtime-status.json": json.dumps({"status": "5/5 PASS"}),
        "slides-final-runtime-status.json": json.dumps({"status": "6/6 PASS"}),
        "words-final-guard-report.json": json.dumps({"verdict": "REGRESSION_FREE"}),
        "cells-final-guard-report.json": json.dumps({"verdict": "REGRESSION_FREE"}),
        "diagram-final-guard-report.json": json.dumps({"verdict": "REGRESSION_FREE"}),
        "all-family-launch-scoreboard.json": json.dumps({"families": 6}),
        "all-family-launch-scoreboard.md": "# All-Family Scoreboard Sprint 29",
        "families-needing-launch-work.json": json.dumps({"families": []}),
        "release-state-reconciliation-report.json": json.dumps({"state": "OK"}),
        "taskcard-reconciliation-report.json": json.dumps({"open": 2}),
        "taskcard-state-after-sprint29.json": json.dumps({"sprint": "sprint29"}),
        # New Sprint 29-only categories
        "sprint28-commit-proof.json": json.dumps({"sprint28_commit_is_head": True, "head_short": "20686d3"}),
        "sprint28-bundle-vs-commit-reconciliation.md": "# Sprint 28 reconciliation — VERIFIED",
        "evidence-contract-v2-implementation-report.json": json.dumps({"version": "2.0.0"}),
        "evidence-contract-v2-test-report.json": json.dumps({"passed": 15, "failed": 0}),
    }


# ---------------------------------------------------------------------------
# v2 contract rejects invalid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV2Rejects:
    """v2 contract must reject bundles that pass v1 but fail state-correctness checks."""

    def test_v2_rejects_bundle_missing_sprint28_commit_in_log(self, tmp_path):
        """git-log-proof.txt without Sprint 28 commit 20686d3 must fail v2."""
        files = _minimal_v2_complete_files()
        # Replace git log with one that does NOT contain 20686d3
        files["git-log-proof.txt"] = "abc1234 feat(old): old sprint only\n"
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed
        assert any("20686d3" in f for f in result.failures)

    def test_v2_rejects_staged_source_files_in_final_status(self, tmp_path):
        """git-status-final.txt with staged src/ files must fail v2."""
        files = _minimal_v2_complete_files()
        # Staged source file line: 'A  src/plugin_examples/foo.py'
        files["git-status-final.txt"] = "A  src/plugin_examples/foo.py\n?? plans/"
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed
        assert any("staged" in f.lower() or "src/" in f for f in result.failures)

    def test_v2_rejects_staged_test_files_in_final_status(self, tmp_path):
        """git-status-final.txt with staged tests/ files must fail v2."""
        files = _minimal_v2_complete_files()
        files["git-status-final.txt"] = "M  tests/unit/test_evidence_contract.py\n"
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed

    def test_v2_rejects_in_progress_verdict(self, tmp_path):
        """final-verdict.md containing IN_PROGRESS must fail v2."""
        files = _minimal_v2_complete_files()
        files["final-verdict.md"] = "# SPRINT29_IN_PROGRESS — work not done"
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed
        assert any("IN_PROGRESS" in f for f in result.failures)

    def test_v2_rejects_unknown_verdict(self, tmp_path):
        """final-verdict.md without any allowed Sprint 29 verdict must fail v2."""
        files = _minimal_v2_complete_files()
        files["final-verdict.md"] = "# SOME_UNKNOWN_VERDICT_COMPLETELY_INVALID"
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed

    def test_v2_rejects_failed_tests_in_summary(self, tmp_path):
        """test-summary.json with failed>0 must fail v2."""
        files = _minimal_v2_complete_files()
        files["test-summary.json"] = json.dumps({"passed": 1640, "failed": 5})
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed
        assert any("failed" in f.lower() for f in result.failures)

    def test_v2_rejects_zero_passed_tests(self, tmp_path):
        """test-summary.json with passed==0 must fail v2."""
        files = _minimal_v2_complete_files()
        files["test-summary.json"] = json.dumps({"passed": 0, "failed": 0})
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed

    def test_v2_rejects_bundle_contract_report_with_false_passed(self, tmp_path):
        """bundle-contract-validation-report.json with passed=false must fail v2."""
        files = _minimal_v2_complete_files()
        files["bundle-contract-validation-report.json"] = json.dumps({
            "passed": False, "categories_missing": ["test_full_log"],
            "verdict": "BUNDLE_CONTRACT_FAILED"
        })
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed

    def test_v2_rejects_missing_pr3_version_policy(self, tmp_path):
        """Missing pdf-pr3-version-policy-report.json must fail v2."""
        files = _minimal_v2_complete_files()
        del files["pdf-pr3-version-policy-report.json"]
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed
        assert "pr3_version_policy" in result.categories_missing

    def test_v2_rejects_missing_sprint28_commit_proof(self, tmp_path):
        """Missing sprint28-commit-proof.json must fail v2."""
        files = _minimal_v2_complete_files()
        del files["sprint28-commit-proof.json"]
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed
        assert "sprint28_commit_proof" in result.categories_missing

    def test_v2_requires_more_categories_than_v1(self):
        """v2 must require more categories than v1 (stricter)."""
        assert MIN_CATEGORIES_REQUIRED_V2 > len(REQUIRED_CATEGORIES), (
            f"v2 ({MIN_CATEGORIES_REQUIRED_V2}) must have more categories than v1 ({len(REQUIRED_CATEGORIES)})"
        )

    def test_v2_min_categories_matches_combined(self):
        """MIN_CATEGORIES_REQUIRED_V2 must equal len(COMBINED_CATEGORIES_V2)."""
        assert MIN_CATEGORIES_REQUIRED_V2 == len(COMBINED_CATEGORIES_V2)

    def test_v2_rejects_relative_zip_path(self, tmp_path):
        """v2 validate_zip must fail if given a relative path."""
        files = _minimal_v2_complete_files()
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        import os
        rel_path = os.path.relpath(str(zip_path))
        result = StrictEvidenceContractV2().validate_zip(rel_path)
        # Relative path should produce a failure
        assert not result.passed

    def test_v2_rejects_sprint28_style_bundle_missing_new_categories(self, tmp_path):
        """A Sprint 28-style bundle (v1 complete, v2 incomplete) must fail v2."""
        files = _minimal_complete_files()  # v1 complete set
        zip_path = tmp_path / "sprint28-style.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert not result.passed
        # Must be missing at least the v2-only categories
        missing = set(result.categories_missing)
        assert "sprint28_commit_proof" in missing or "pr3_version_policy" in missing


# ---------------------------------------------------------------------------
# v2 contract accepts valid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV2Accepts:
    """v2 contract must accept correctly formed approval-blocked and published bundles."""

    def test_v2_accepts_complete_approval_blocked_bundle(self, tmp_path):
        """A complete approval-blocked bundle satisfying all v2 checks must pass."""
        files = _minimal_v2_complete_files()
        zip_path = tmp_path / "sprint29-complete.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert result.passed, f"v2 should pass but failed: {result.failures}"
        assert result.verdict == "BUNDLE_CONTRACT_PASSED"
        assert result.categories_missing == []

    def test_v2_accepts_published_verdict(self, tmp_path):
        """A bundle with a published verdict (PR URLs in final-verdict) must pass."""
        files = _minimal_v2_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT29_PUBLISHED_AND_EVIDENCE_CONTRACT_V2_COMPLETE\n\n"
            "PR#3: https://github.com/aspose-pdf-net/pull/10\n"
            "PR#5: https://github.com/aspose-pdf-net/pull/11"
        )
        files["post-publication-not-run-approval-blocked.md"] = ""
        # Add publication results
        for pr in ["pr3", "pr5", "pr6", "pr7", "pr8", "pr9"]:
            files[f"pdf-{pr}-approval-blocked.md"] = ""
            files[f"pdf-{pr}-final-package-audit.json"] = json.dumps({"status": "PASS"})
        zip_path = tmp_path / "sprint29-published.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        assert result.passed, f"v2 should pass but failed: {result.failures}"

    def test_v2_contract_definition_version(self):
        """contract_definition_v2 must return version 2.0.0."""
        defn = contract_definition_v2()
        assert defn["contract_version"] == "2.0.0"

    def test_v2_contract_definition_has_all_combined_categories(self):
        """contract_definition_v2 must include all COMBINED_CATEGORIES_V2 keys."""
        defn = contract_definition_v2()
        assert set(defn["required_categories"].keys()) == set(COMBINED_CATEGORIES_V2.keys())

    def test_v2_contract_definition_lists_allowed_verdicts(self):
        """contract_definition_v2 must list all allowed Sprint 29 verdicts."""
        defn = contract_definition_v2()
        assert set(defn["allowed_verdicts"]) == set(ALLOWED_VERDICTS_V2)

    def test_v2_accepts_clean_git_status_with_only_untracked_and_binary(self, tmp_path):
        """git-status-final.txt with only untracked/binary lines must pass."""
        files = _minimal_v2_complete_files()
        files["git-status-final.txt"] = (
            "?? plans/\n"
            " M workspace/fixture-validation/pdf-signature-harness/bin/Debug/net8.0/harness.dll\n"
            " M workspace/manifests/example-index.json\n"
        )
        zip_path = tmp_path / "clean-status.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV2().validate_zip(zip_path)
        # Should not fail on git status check (no staged src/ tests/ pipeline/ files)
        status_failures = [f for f in result.failures if "staged" in f.lower() and "src/" in f]
        assert len(status_failures) == 0
