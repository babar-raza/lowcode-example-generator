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
    ALLOWED_VERDICTS_V3,
    ALLOWED_VERDICTS_V4,
    ALLOWED_VERDICTS_V5,
    ALLOWED_VERDICTS_V6,
    ALLOWED_VERDICTS_V7,
    COMBINED_CATEGORIES_V2,
    COMBINED_CATEGORIES_V3,
    COMBINED_CATEGORIES_V4,
    COMBINED_CATEGORIES_V5,
    COMBINED_CATEGORIES_V6,
    COMBINED_CATEGORIES_V7,
    MIN_CATEGORIES_REQUIRED_V2,
    MIN_CATEGORIES_REQUIRED_V3,
    MIN_CATEGORIES_REQUIRED_V4,
    MIN_CATEGORIES_REQUIRED_V5,
    MIN_CATEGORIES_REQUIRED_V6,
    MIN_CATEGORIES_REQUIRED_V7,
    REQUIRED_CATEGORIES,
    StrictEvidenceContract,
    StrictEvidenceContractV2,
    StrictEvidenceContractV3,
    StrictEvidenceContractV4,
    StrictEvidenceContractV5,
    StrictEvidenceContractV6,
    StrictEvidenceContractV7,
    ALLOWED_VERDICTS_V8,
    COMBINED_CATEGORIES_V8,
    MIN_CATEGORIES_REQUIRED_V8,
    StrictEvidenceContractV8,
    PLANNER_SPRINT_CATEGORIES,
    MIN_PLANNER_CATEGORIES_REQUIRED,
    ALLOWED_PLANNER_VERDICTS,
    PlannerSprintEvidenceContract,
    generate_validation_proof,
    generate_companion_proof,
    check_head_consistency,
    contract_definition,
    contract_definition_v2,
    contract_definition_v3,
    contract_definition_v4,
    contract_definition_v5,
    contract_definition_v6,
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


# ---------------------------------------------------------------------------
# Helper for v3 complete bundle
# ---------------------------------------------------------------------------

def _minimal_v3_complete_files() -> dict[str, str]:
    """Return files satisfying all 45 v3 required categories with valid content."""
    files = dict(_minimal_v2_complete_files())
    # Remove v2 sprint28 keys (renamed in v3)
    files.pop("sprint28-commit-proof.json", None)
    files.pop("sprint28-bundle-vs-commit-reconciliation.md", None)
    # Update taskcard state to sprint30
    files.pop("taskcard-state-after-sprint29.json", None)
    files["taskcard-state-after-sprint30.json"] = json.dumps({"sprint": "sprint30"})
    # v3 new categories
    files["sprint29-commit-proof.json"] = json.dumps({
        "head_commit": {"short": "ef74d9b"},
        "ancestry_chain": ["ef74d9b", "4be32c1", "20686d3"],
        "verdict": "SPRINT29_COMMITS_VERIFIED",
    })
    files["sprint29-bundle-vs-commit-reconciliation.md"] = (
        "# Sprint 29 Bundle vs Commit Reconciliation\nBOOTSTRAP_PATTERN_EXPECTED"
    )
    files["all-pr-packages-audit-post-cleanup.json"] = json.dumps({
        "summary": {
            "packages_with_blocking_flags": 0,
            "packages_publication_safe": 6,
            "all_clean": True,
        }
    })
    # v3 git log must contain ef74d9b (Sprint 29 HEAD)
    files["git-log-proof.txt"] = (
        "ef74d9b chore(sprint29-bundle): add v2-validated evidence bundle\n"
        "4be32c1 feat(sprint29): SPRINT29_APPROVAL_BLOCKED_EVIDENCE_CONTRACT_V2_COMPLETE\n"
        "20686d3 feat(sprint28): SPRINT28_STRICT_EVIDENCE_CONTRACT\n"
    )
    # v3 final verdict must be a Sprint 30 verdict
    files["final-verdict.md"] = (
        "# SPRINT30_APPROVAL_BLOCKED_PACKAGES_CLEAN_EVIDENCE_V3_COMPLETE\n\nAll packages clean."
    )
    # v3 source-state-classification.json must have sprint30_start_state
    files["source-state-classification.json"] = json.dumps({
        "sprint30_start_state": "CLEAN_FOR_SPRINT_EXECUTION",
        "source_changes_check": {"src_modified": False},
    })
    return files


# ---------------------------------------------------------------------------
# v3 contract rejects invalid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV3Rejects:
    """v3 contract must reject bundles missing v3-specific requirements."""

    def test_v3_rejects_missing_sprint29_commit_proof(self, tmp_path):
        """Missing sprint29-commit-proof.json must fail v3."""
        files = _minimal_v3_complete_files()
        del files["sprint29-commit-proof.json"]
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        assert "sprint29_commit_proof" in result.categories_missing

    def test_v3_rejects_missing_sprint29_reconciliation(self, tmp_path):
        """Missing sprint29-bundle-vs-commit-reconciliation.md must fail v3."""
        files = _minimal_v3_complete_files()
        del files["sprint29-bundle-vs-commit-reconciliation.md"]
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        assert "sprint29_reconciliation" in result.categories_missing

    def test_v3_rejects_missing_bin_obj_cleanup_audit(self, tmp_path):
        """Missing all-pr-packages-audit-post-cleanup.json must fail v3."""
        files = _minimal_v3_complete_files()
        del files["all-pr-packages-audit-post-cleanup.json"]
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        assert "bin_obj_cleanup" in result.categories_missing

    def test_v3_rejects_missing_sprint30_taskcard_state(self, tmp_path):
        """Missing taskcard-state-after-sprint30.json must fail v3."""
        files = _minimal_v3_complete_files()
        del files["taskcard-state-after-sprint30.json"]
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        assert "taskcard_state" in result.categories_missing

    def test_v3_rejects_git_log_without_sprint29_commit(self, tmp_path):
        """git-log-proof.txt without ef74d9b must fail v3."""
        files = _minimal_v3_complete_files()
        files["git-log-proof.txt"] = "20686d3 feat(sprint28): only sprint28 here\n"
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        assert any("ef74d9b" in f for f in result.failures)

    def test_v3_rejects_package_audit_with_blocking_flags(self, tmp_path):
        """Package audit with packages_with_blocking_flags > 0 must fail v3."""
        files = _minimal_v3_complete_files()
        files["all-pr-packages-audit-post-cleanup.json"] = json.dumps({
            "summary": {
                "packages_with_blocking_flags": 2,
                "packages_publication_safe": 4,
            }
        })
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        assert any("packages_with_blocking_flags" in f for f in result.failures)

    def test_v3_rejects_dirty_source_state_classification(self, tmp_path):
        """source-state-classification.json with wrong sprint30_start_state must fail v3."""
        files = _minimal_v3_complete_files()
        files["source-state-classification.json"] = json.dumps({
            "sprint30_start_state": "DIRTY_SOURCE_MODIFICATIONS_PRESENT"
        })
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        assert any("sprint30_start_state" in f for f in result.failures)

    def test_v3_rejects_sprint29_verdict_in_final_verdict(self, tmp_path):
        """final-verdict.md with a Sprint 29 verdict (not Sprint 30) must fail v3."""
        files = _minimal_v3_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT29_APPROVAL_BLOCKED_EVIDENCE_CONTRACT_V2_COMPLETE"
        )
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        assert any("Sprint 30" in f for f in result.failures)

    def test_v3_rejects_in_progress_verdict(self, tmp_path):
        """final-verdict.md with IN_PROGRESS must fail v3."""
        files = _minimal_v3_complete_files()
        files["final-verdict.md"] = "# SPRINT30_IN_PROGRESS — still running"
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        assert any("IN_PROGRESS" in f for f in result.failures)

    def test_v3_rejects_sprint29_style_bundle(self, tmp_path):
        """A Sprint 29 v2-complete bundle must fail v3 (missing sprint30 categories)."""
        files = _minimal_v2_complete_files()
        zip_path = tmp_path / "sprint29-style.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert not result.passed
        missing = set(result.categories_missing)
        assert "bin_obj_cleanup" in missing or "sprint29_commit_proof" in missing

    def test_v3_requires_more_categories_than_v2(self):
        """v3 must require more categories than v2."""
        assert MIN_CATEGORIES_REQUIRED_V3 > MIN_CATEGORIES_REQUIRED_V2, (
            f"v3 ({MIN_CATEGORIES_REQUIRED_V3}) must have more categories than v2 ({MIN_CATEGORIES_REQUIRED_V2})"
        )

    def test_v3_min_categories_matches_combined(self):
        """MIN_CATEGORIES_REQUIRED_V3 must equal len(COMBINED_CATEGORIES_V3)."""
        assert MIN_CATEGORIES_REQUIRED_V3 == len(COMBINED_CATEGORIES_V3)

    def test_v3_has_exactly_45_categories(self):
        """v3 must have exactly 45 categories (resolves 44-vs-45 discrepancy)."""
        assert MIN_CATEGORIES_REQUIRED_V3 == 45, (
            f"v3 must have 45 categories, got {MIN_CATEGORIES_REQUIRED_V3}"
        )

    def test_v3_rejects_relative_zip_path(self, tmp_path):
        """v3 validate_zip must fail if given a relative path."""
        files = _minimal_v3_complete_files()
        zip_path = tmp_path / "bundle.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        import os
        rel_path = os.path.relpath(str(zip_path))
        result = StrictEvidenceContractV3().validate_zip(rel_path)
        assert not result.passed


# ---------------------------------------------------------------------------
# v3 contract accepts valid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV3Accepts:
    """v3 contract must accept correctly formed Sprint 30 bundles."""

    def test_v3_accepts_complete_approval_blocked_bundle(self, tmp_path):
        """A complete Sprint 30 approval-blocked bundle must pass v3."""
        files = _minimal_v3_complete_files()
        zip_path = tmp_path / "sprint30-complete.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert result.passed, f"v3 should pass but failed: {result.failures}"
        assert result.verdict == "BUNDLE_CONTRACT_PASSED"
        assert result.categories_missing == []
        assert len(result.categories_found) == MIN_CATEGORIES_REQUIRED_V3

    def test_v3_accepts_published_verdict(self, tmp_path):
        """A bundle with a Sprint 30 published verdict must pass v3."""
        files = _minimal_v3_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT30_ALL_PRS_PUBLISHED_EVIDENCE_V3_COMPLETE\n\n"
            "All 6 PRs published successfully."
        )
        zip_path = tmp_path / "sprint30-published.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV3().validate_zip(zip_path)
        assert result.passed, f"v3 should pass but failed: {result.failures}"

    def test_v3_contract_definition_version(self):
        """contract_definition_v3 must return version 3.0.0."""
        defn = contract_definition_v3()
        assert defn["contract_version"] == "3.0.0"

    def test_v3_contract_definition_has_all_combined_categories(self):
        """contract_definition_v3 must include all COMBINED_CATEGORIES_V3 keys."""
        defn = contract_definition_v3()
        assert set(defn["required_categories"].keys()) == set(COMBINED_CATEGORIES_V3.keys())

    def test_v3_contract_definition_lists_allowed_verdicts(self):
        """contract_definition_v3 must list all allowed Sprint 30 verdicts."""
        defn = contract_definition_v3()
        assert set(defn["allowed_verdicts"]) == set(ALLOWED_VERDICTS_V3)

    def test_v3_contract_definition_documents_category_reconciliation(self):
        """contract_definition_v3 must document the 44-vs-45 reconciliation."""
        defn = contract_definition_v3()
        recon = defn["category_count_reconciliation"]
        assert recon["v2_categories"] == 44
        assert recon["v3_categories"] == 45
        assert "sprint28_commit_proof" in recon["categories_removed_from_v2"]
        assert "bin_obj_cleanup" in recon["categories_added_in_v3"]


# ---------------------------------------------------------------------------
# Helper for v4 complete bundle
# ---------------------------------------------------------------------------

def _minimal_v4_complete_files() -> dict[str, str]:
    """Return files satisfying all 49 v4 required categories with valid content."""
    files = dict(_minimal_v3_complete_files())
    # Remove v3 sprint29 keys (replaced in v4)
    files.pop("sprint29-commit-proof.json", None)
    files.pop("sprint29-bundle-vs-commit-reconciliation.md", None)
    # Update taskcard state to sprint31
    files.pop("taskcard-state-after-sprint30.json", None)
    files["taskcard-state-after-sprint31.json"] = json.dumps({"sprint": "sprint31"})
    # v4 new categories
    files["sprint30-commit-proof.json"] = json.dumps({
        "head_commit": {"short": "e379cdf"},
        "ancestry_chain": ["e379cdf", "8094a46", "ef74d9b"],
        "verdict": "SPRINT30_COMMITS_VERIFIED",
    })
    files["sprint30-bundle-vs-commit-reconciliation.md"] = (
        "# Sprint 30 Bundle vs Commit Reconciliation\nBOOTSTRAP_PATTERN_EXPECTED"
    )
    files["pdf-security-inventory-reconciliation.json"] = json.dumps({
        "finding": "SECURITY_PRESENT_IN_PR7_NEVER_MISSING",
        "security_in_pr7": True,
        "root_cause": "audit_omission",
    })
    files["pdf-pr-package-count-reconciliation.json"] = json.dumps({
        "total_pr_ready": 14,
        "pr_breakdown": {"PR3": 3, "PR5": 3, "PR6": 3, "PR7": 2, "PR8": 2, "PR9": 1},
        "verdict": "COUNT_CONSISTENT",
    })
    files["pdf-pr8-clean-final-audit.json"] = json.dumps({
        "package": "pdf-controlled-pilot-pr8",
        "bin_obj_count": 0,
        "status": "CLEAN",
    })
    files["pdf-pr9-clean-final-audit.json"] = json.dumps({
        "package": "pdf-controlled-pilot-pr9",
        "bin_obj_count": 0,
        "status": "CLEAN",
    })
    # v4 git log must contain e379cdf (Sprint 30 HEAD)
    files["git-log-proof.txt"] = (
        "e379cdf chore(sprint30-bundle): add v3-validated evidence bundle\n"
        "8094a46 feat(sprint30): SPRINT30_APPROVAL_BLOCKED_PACKAGES_CLEAN\n"
        "ef74d9b chore(sprint29-bundle): add v2-validated evidence bundle\n"
    )
    # v4 final verdict must be a Sprint 31 verdict
    files["final-verdict.md"] = (
        "# SPRINT31_APPROVAL_BLOCKED_SECURITY_RECONCILED_EVIDENCE_V4_COMPLETE\n\n"
        "Security present in PR#7. PR count=14 confirmed."
    )
    # v4 source-state-classification.json must have sprint31_start_state
    files["source-state-classification.json"] = json.dumps({
        "sprint31_start_state": "CLEAN_FOR_SPRINT_EXECUTION",
        "source_changes_check": {"src_modified": False},
    })
    return files


# ---------------------------------------------------------------------------
# v4 contract rejects invalid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV4Rejects:
    """v4 contract must reject bundles missing v4-specific requirements."""

    def test_v4_rejects_missing_sprint30_commit_proof(self, tmp_path):
        """Missing sprint30-commit-proof.json must fail v4."""
        files = _minimal_v4_complete_files()
        del files["sprint30-commit-proof.json"]
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert "sprint30_commit_proof" in result.categories_missing

    def test_v4_rejects_missing_security_inventory(self, tmp_path):
        """Missing pdf-security-inventory-reconciliation.json must fail v4."""
        files = _minimal_v4_complete_files()
        del files["pdf-security-inventory-reconciliation.json"]
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert "security_inventory" in result.categories_missing

    def test_v4_rejects_missing_pr_package_count_reconciliation(self, tmp_path):
        """Missing pdf-pr-package-count-reconciliation.json must fail v4."""
        files = _minimal_v4_complete_files()
        del files["pdf-pr-package-count-reconciliation.json"]
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert "pr_package_count_reconciliation" in result.categories_missing

    def test_v4_rejects_pr_count_not_14(self, tmp_path):
        """pdf-pr-package-count-reconciliation.json with total_pr_ready!=14 must fail v4."""
        files = _minimal_v4_complete_files()
        files["pdf-pr-package-count-reconciliation.json"] = json.dumps({
            "total_pr_ready": 13,
            "pr_breakdown": {"PR3": 3, "PR5": 3, "PR6": 3, "PR7": 1, "PR8": 2, "PR9": 1},
            "verdict": "COUNT_INCONSISTENT",
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert any("total_pr_ready" in f or "14" in f for f in result.failures)

    def test_v4_rejects_git_log_without_sprint30_commit(self, tmp_path):
        """git-log-proof.txt without e379cdf must fail v4."""
        files = _minimal_v4_complete_files()
        files["git-log-proof.txt"] = "ef74d9b chore(sprint29-bundle): only sprint29 here\n"
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert any("e379cdf" in f for f in result.failures)

    def test_v4_rejects_sprint30_verdict_in_final_verdict(self, tmp_path):
        """final-verdict.md with a Sprint 30 verdict (not Sprint 31) must fail v4."""
        files = _minimal_v4_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT30_APPROVAL_BLOCKED_PACKAGES_CLEAN_EVIDENCE_V3_COMPLETE"
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert any("Sprint 31" in f for f in result.failures)

    def test_v4_rejects_staged_pr_package_deletion(self, tmp_path):
        """git-status-final.txt with staged workspace/pr-dry-run/ deletion must fail v4."""
        files = _minimal_v4_complete_files()
        files["git-status-final.txt"] = (
            "D  workspace/pr-dry-run/pdf-controlled-pilot-pr7/security/Program.cs\n"
            "?? plans/\n"
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert any("pr-dry-run" in f for f in result.failures)

    def test_v4_rejects_dirty_sprint31_source_state(self, tmp_path):
        """source-state-classification.json with wrong sprint31_start_state must fail v4."""
        files = _minimal_v4_complete_files()
        files["source-state-classification.json"] = json.dumps({
            "sprint31_start_state": "DIRTY_SOURCE_MODIFICATIONS_PRESENT"
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert any("sprint31_start_state" in f for f in result.failures)

    def test_v4_rejects_sprint30_style_bundle(self, tmp_path):
        """A Sprint 30 v3-complete bundle must fail v4 (missing sprint31 categories)."""
        files = _minimal_v3_complete_files()
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        missing = set(result.categories_missing)
        assert "sprint30_commit_proof" in missing or "security_inventory" in missing

    def test_v4_requires_more_categories_than_v3(self):
        """v4 must require more categories than v3 (stricter)."""
        assert MIN_CATEGORIES_REQUIRED_V4 > MIN_CATEGORIES_REQUIRED_V3, (
            f"v4 ({MIN_CATEGORIES_REQUIRED_V4}) must have more categories than v3 ({MIN_CATEGORIES_REQUIRED_V3})"
        )

    def test_v4_min_categories_matches_combined(self):
        """MIN_CATEGORIES_REQUIRED_V4 must equal len(COMBINED_CATEGORIES_V4)."""
        assert MIN_CATEGORIES_REQUIRED_V4 == len(COMBINED_CATEGORIES_V4)

    def test_v4_has_exactly_49_categories(self):
        """v4 must have exactly 49 categories (45 v3 - 2 removed + 6 added)."""
        assert MIN_CATEGORIES_REQUIRED_V4 == 49, (
            f"v4 must have 49 categories, got {MIN_CATEGORIES_REQUIRED_V4}"
        )

    def test_v4_rejects_missing_sprint31_taskcard_state(self, tmp_path):
        """Missing taskcard-state-after-sprint31.json must fail v4."""
        files = _minimal_v4_complete_files()
        del files["taskcard-state-after-sprint31.json"]
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert "taskcard_state" in result.categories_missing

    def test_v4_rejects_in_progress_verdict(self, tmp_path):
        """final-verdict.md with IN_PROGRESS must fail v4."""
        files = _minimal_v4_complete_files()
        files["final-verdict.md"] = "# SPRINT31_IN_PROGRESS — still running"
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert not result.passed
        assert any("IN_PROGRESS" in f for f in result.failures)


# ---------------------------------------------------------------------------
# v4 contract accepts valid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV4Accepts:
    """v4 contract must accept correctly formed Sprint 31 bundles."""

    def test_v4_accepts_complete_approval_blocked_bundle(self, tmp_path):
        """A complete Sprint 31 approval-blocked bundle must pass v4."""
        files = _minimal_v4_complete_files()
        zip_path = tmp_path / "sprint31-complete.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert result.passed, f"v4 should pass but failed: {result.failures}"
        assert result.verdict == "BUNDLE_CONTRACT_PASSED"
        assert result.categories_missing == []
        assert len(result.categories_found) == MIN_CATEGORIES_REQUIRED_V4

    def test_v4_accepts_published_verdict(self, tmp_path):
        """A bundle with a Sprint 31 published verdict must pass v4."""
        files = _minimal_v4_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT31_ALL_PRS_PUBLISHED_EVIDENCE_V4_COMPLETE\n\n"
            "All 6 PRs published successfully."
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV4().validate_zip(zip_path)
        assert result.passed, f"v4 should pass but failed: {result.failures}"

    def test_v4_contract_definition_version(self):
        """contract_definition_v4 must return version 4.0.0."""
        defn = contract_definition_v4()
        assert defn["contract_version"] == "4.0.0"

    def test_v4_contract_definition_has_all_combined_categories(self):
        """contract_definition_v4 must include all COMBINED_CATEGORIES_V4 keys."""
        defn = contract_definition_v4()
        assert set(defn["required_categories"].keys()) == set(COMBINED_CATEGORIES_V4.keys())

    def test_v4_contract_definition_lists_allowed_verdicts(self):
        """contract_definition_v4 must list all allowed Sprint 31 verdicts."""
        defn = contract_definition_v4()
        assert set(defn["allowed_verdicts"]) == set(ALLOWED_VERDICTS_V4)

    def test_v4_contract_definition_documents_category_reconciliation(self):
        """contract_definition_v4 must document the v3→v4 delta."""
        defn = contract_definition_v4()
        recon = defn["category_count_reconciliation"]
        assert recon["v3_categories"] == 45
        assert recon["v4_categories"] == 49
        assert "sprint29_commit_proof" in recon["categories_removed_from_v3"]
        assert "security_inventory" in recon["categories_added_in_v4"]


# ---------------------------------------------------------------------------
# Helper for v5 complete bundle
# ---------------------------------------------------------------------------

def _minimal_v5_complete_files() -> dict[str, str]:
    """Return files satisfying all 53 v5 required categories with valid content."""
    files = dict(_minimal_v4_complete_files())
    # Remove v4 sprint30 keys (replaced in v5)
    files.pop("sprint30-commit-proof.json", None)
    files.pop("sprint30-bundle-vs-commit-reconciliation.md", None)
    # Update taskcard state to sprint32
    files.pop("taskcard-state-after-sprint31.json", None)
    files["taskcard-state-after-sprint32.json"] = json.dumps({"sprint": "sprint32"})
    # v5 new categories
    files["sprint31-final-state-reconciliation.json"] = json.dumps({
        "sprint31_head": "0f44886",
        "source_test_config_modified": False,
        "verdict": "SPRINT31_FINAL_STATE_CLEAN_SOURCE_COMMITTED",
    })
    files["email-target-runtime-verification-report.json"] = json.dumps({
        "target_repo": "aspose-email-net",
        "merge_sha": "023ad66970d2",
        "status": "RUNTIME_VERIFIED",
    })
    files["slides-target-runtime-verification-report.json"] = json.dumps({
        "target_repo": "aspose-slides-net",
        "merge_sha": "bf05fc43124f",
        "status": "RUNTIME_VERIFIED",
    })
    files["pdf-formimporter-latest-version-retest-report.json"] = json.dumps({
        "latest_version_tested": "26.5.0",
        "still_failing": True,
        "verdict": "DEFECT_CONFIRMED_RETEST_AT_NEXT_VERSION",
    })
    files["pdf-release-candidate-publication-packet.json"] = json.dumps({
        "total_pr_ready": 14,
        "prs": ["PR3", "PR5", "PR6", "PR7", "PR8", "PR9"],
    })
    files["pdf-release-candidate-publication-packet.md"] = (
        "# PDF Release Candidate Publication Packet\n\n14 examples ready."
    )
    # v5 git log must contain 0f44886 (Sprint 31 HEAD)
    files["git-log-proof.txt"] = (
        "0f44886 chore(sprint31-bundle): add v4-validated evidence bundle\n"
        "ef82c3b feat(sprint31): SPRINT31_APPROVAL_BLOCKED_SECURITY_RECONCILED\n"
        "e379cdf chore(sprint30-bundle): add v3-validated evidence bundle\n"
    )
    # v5 final verdict must be a Sprint 32 verdict
    files["final-verdict.md"] = (
        "# SPRINT32_APPROVAL_BLOCKED_RELEASE_CANDIDATE_AND_CONTRACT_V5_COMPLETE\n\n"
        "All packages clean. Release candidate packet complete."
    )
    # v5 source-state-classification.json must have sprint32_start_state
    files["source-state-classification.json"] = json.dumps({
        "sprint32_start_state": "CLEAN_FOR_SPRINT_EXECUTION",
        "source_changes_check": {"src_modified": False},
    })
    # v5 git-status-final.txt must have NO modified src/tests/pipeline/.gitignore
    files["git-status-final.txt"] = (
        " M workspace/fixture-validation/pdf-signature-harness/bin/Debug/net8.0/harness.dll\n"
        " M workspace/manifests/example-index.json\n"
        "?? plans/\n"
    )
    return files


# ---------------------------------------------------------------------------
# v5 contract rejects invalid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV5Rejects:
    """v5 contract must reject bundles with modified source/test/config files and missing v5 categories."""

    def test_v5_rejects_unstaged_src_in_git_status(self, tmp_path):
        """git-status-final.txt with unstaged src/ modification must fail v5 (closes V4 weakness)."""
        files = _minimal_v5_complete_files()
        # V4 weakness: unstaged (space M) was not caught by V4
        files["git-status-final.txt"] = (
            " M src/plugin_examples/evidence_contract.py\n"
            "?? plans/\n"
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        assert any("src/" in f or "modified" in f.lower() for f in result.failures)

    def test_v5_rejects_staged_src_in_git_status(self, tmp_path):
        """git-status-final.txt with staged src/ modification must also fail v5."""
        files = _minimal_v5_complete_files()
        files["git-status-final.txt"] = "M  src/plugin_examples/evidence_contract.py\n"
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        assert any("src/" in f for f in result.failures)

    def test_v5_rejects_modified_gitignore_in_git_status(self, tmp_path):
        """git-status-final.txt with modified .gitignore must fail v5."""
        files = _minimal_v5_complete_files()
        files["git-status-final.txt"] = " M .gitignore\n?? plans/\n"
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        assert any(".gitignore" in f for f in result.failures)

    def test_v5_rejects_modified_tests_in_git_status(self, tmp_path):
        """git-status-final.txt with modified tests/ file must fail v5."""
        files = _minimal_v5_complete_files()
        files["git-status-final.txt"] = " M tests/unit/test_evidence_contract.py\n"
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed

    def test_v5_rejects_sprint31_head_missing_from_log(self, tmp_path):
        """git-log-proof.txt without Sprint 31 HEAD 0f44886 must fail v5."""
        files = _minimal_v5_complete_files()
        files["git-log-proof.txt"] = "e379cdf chore(sprint30): only sprint30 here\n"
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        assert any("0f44886" in f for f in result.failures)

    def test_v5_rejects_sprint31_verdict_in_final_verdict(self, tmp_path):
        """final-verdict.md with Sprint 31 verdict (not Sprint 32) must fail v5."""
        files = _minimal_v5_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT31_APPROVAL_BLOCKED_SECURITY_RECONCILED_EVIDENCE_V4_COMPLETE"
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        assert any("Sprint 32" in f for f in result.failures)

    def test_v5_rejects_missing_sprint31_state_reconciliation(self, tmp_path):
        """Missing sprint31-final-state-reconciliation.json must fail v5."""
        files = _minimal_v5_complete_files()
        del files["sprint31-final-state-reconciliation.json"]
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        assert "sprint31_state_reconciliation" in result.categories_missing

    def test_v5_rejects_missing_email_target_runtime_report(self, tmp_path):
        """Missing email-target-runtime-verification-report.json must fail v5."""
        files = _minimal_v5_complete_files()
        del files["email-target-runtime-verification-report.json"]
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        assert "email_target_runtime_report" in result.categories_missing

    def test_v5_rejects_missing_slides_target_runtime_report(self, tmp_path):
        """Missing slides-target-runtime-verification-report.json must fail v5."""
        files = _minimal_v5_complete_files()
        del files["slides-target-runtime-verification-report.json"]
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        assert "slides_target_runtime_report" in result.categories_missing

    def test_v5_rejects_missing_release_candidate_packet(self, tmp_path):
        """Missing pdf-release-candidate-publication-packet.json must fail v5."""
        files = _minimal_v5_complete_files()
        del files["pdf-release-candidate-publication-packet.json"]
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        assert "release_candidate_packet_json" in result.categories_missing

    def test_v5_rejects_sprint31_style_bundle(self, tmp_path):
        """A Sprint 31 v4-complete bundle must fail v5 (missing sprint32 categories)."""
        files = _minimal_v4_complete_files()
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert not result.passed
        missing = set(result.categories_missing)
        assert "sprint31_state_reconciliation" in missing or "release_candidate_packet_json" in missing

    def test_v5_requires_more_categories_than_v4(self):
        """v5 must require more categories than v4 (stricter)."""
        assert MIN_CATEGORIES_REQUIRED_V5 > MIN_CATEGORIES_REQUIRED_V4, (
            f"v5 ({MIN_CATEGORIES_REQUIRED_V5}) must exceed v4 ({MIN_CATEGORIES_REQUIRED_V4})"
        )

    def test_v5_min_categories_matches_combined(self):
        """MIN_CATEGORIES_REQUIRED_V5 must equal len(COMBINED_CATEGORIES_V5)."""
        assert MIN_CATEGORIES_REQUIRED_V5 == len(COMBINED_CATEGORIES_V5)

    def test_v5_has_exactly_53_categories(self):
        """v5 must have exactly 53 categories (49 v4 - 2 removed + 6 added)."""
        assert MIN_CATEGORIES_REQUIRED_V5 == 53, (
            f"v5 must have 53 categories, got {MIN_CATEGORIES_REQUIRED_V5}"
        )


# ---------------------------------------------------------------------------
# v5 contract accepts valid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV5Accepts:
    """v5 contract must accept correctly formed Sprint 32 bundles."""

    def test_v5_accepts_complete_approval_blocked_bundle(self, tmp_path):
        """A complete Sprint 32 approval-blocked bundle must pass v5."""
        files = _minimal_v5_complete_files()
        zip_path = tmp_path / "sprint32-complete.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for name, content in files.items():
                zf.writestr(name, content)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert result.passed, f"v5 should pass but failed: {result.failures}"
        assert result.verdict == "BUNDLE_CONTRACT_PASSED"
        assert result.categories_missing == []
        assert len(result.categories_found) == MIN_CATEGORIES_REQUIRED_V5

    def test_v5_accepts_clean_binary_artifacts_in_git_status(self, tmp_path):
        """git-status-final.txt with only binary/workspace artifacts must pass v5 modified-source check."""
        files = _minimal_v5_complete_files()
        # Only binary/runtime/manifest artifacts — no src/tests/pipeline/.gitignore
        files["git-status-final.txt"] = (
            " M workspace/fixture-validation/pdf-signature-harness/bin/Debug/net8.0/harness.dll\n"
            " M workspace/manifests/example-index.json\n"
            " M workspace/verification/latest/release-status.json\n"
            "?? plans/\n"
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        # Modified-source check should not fail for binary/workspace files
        source_failures = [f for f in result.failures if "modified source" in f.lower()]
        assert len(source_failures) == 0

    def test_v5_accepts_published_verdict(self, tmp_path):
        """A bundle with Sprint 32 published verdict must pass v5."""
        files = _minimal_v5_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT32_PUBLISHED_RELEASE_CANDIDATE_AND_CONTRACT_V5_COMPLETE\n\n"
            "All 6 PRs published."
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV5().validate_zip(zip_path)
        assert result.passed, f"v5 should pass but failed: {result.failures}"

    def test_v5_contract_definition_version(self):
        """contract_definition_v5 must return version 5.0.0."""
        defn = contract_definition_v5()
        assert defn["contract_version"] == "5.0.0"

    def test_v5_contract_definition_has_all_combined_categories(self):
        """contract_definition_v5 must include all COMBINED_CATEGORIES_V5 keys."""
        defn = contract_definition_v5()
        assert set(defn["required_categories"].keys()) == set(COMBINED_CATEGORIES_V5.keys())

    def test_v5_contract_definition_lists_allowed_verdicts(self):
        """contract_definition_v5 must list all allowed Sprint 32 verdicts."""
        defn = contract_definition_v5()
        assert set(defn["allowed_verdicts"]) == set(ALLOWED_VERDICTS_V5)

    def test_v5_contract_definition_documents_category_reconciliation(self):
        """contract_definition_v5 must document the v4→v5 delta."""
        defn = contract_definition_v5()
        recon = defn["category_count_reconciliation"]
        assert recon["v4_categories"] == 49
        assert recon["v5_categories"] == 53
        assert "sprint30_commit_proof" in recon["categories_removed_from_v4"]
        assert "sprint31_state_reconciliation" in recon["categories_added_in_v5"]


# ---------------------------------------------------------------------------
# V6 helpers
# ---------------------------------------------------------------------------

def _minimal_v6_complete_files() -> dict[str, str]:
    """Return files satisfying all 67 v6 required categories with valid content."""
    files = dict(_minimal_v5_complete_files())
    # Remove v5 sprint31 key (replaced in v6)
    files.pop("sprint31-final-state-reconciliation.json", None)
    # Update taskcard state to sprint33
    files.pop("taskcard-state-after-sprint32.json", None)
    files["taskcard-state-after-sprint33.json"] = json.dumps({"sprint": "sprint33"})
    # v6 new categories
    files["sprint32-final-state-reconciliation.json"] = json.dumps({
        "sprint32_head": "b7665d4",
        "verdict": "SPRINT32_FINAL_STATE_CLEAN_SOURCE_COMMITTED",
    })
    files["dirty-artifact-policy-report.json"] = json.dumps({
        "verdict": "DIRTY_ARTIFACT_POLICY_FORMALIZED",
        "total_dirty_files": 26,
    })
    files["merge-mode-decision.json"] = json.dumps({
        "mode": "APPROVAL_BLOCKED",
        "reason": "PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL not set",
    })
    files["merge-mode-result.json"] = json.dumps({
        "result": "NOT_EXECUTED",
        "reason": "approval gate blocked",
    })
    files["words-full-sot-classification-report.json"] = json.dumps({
        "workflow_root_count": 8,
        "total_types": 25,
        "classification_complete": True,
    })
    files["words-denominator-update-report.json"] = json.dumps({
        "workflow_root_count_before": None,
        "workflow_root_count_after": 8,
        "verdict": "DENOMINATOR_UPDATED",
    })
    files["words-backlog-closeout-plan.md"] = (
        "# Words Backlog Closeout Plan\n\nAll types classified."
    )
    files["email-scoreboard-cleanup-report.json"] = json.dumps({
        "family": "email",
        "status": "PILOT_COMPLETE",
        "stale_entries_removed": True,
    })
    files["slides-scoreboard-cleanup-report.json"] = json.dumps({
        "family": "slides",
        "status": "PILOT_COMPLETE",
        "stale_entries_removed": True,
    })
    files["pdf-formimporter-version-watch-report.json"] = json.dumps({
        "current_version": "26.5.0",
        "new_version_available": False,
        "verdict": "NO_NEW_VERSION_AVAILABLE",
    })
    files["new-lowcode-family-discovery-report.json"] = json.dumps({
        "families_scanned": 5,
        "new_lowcode_families_found": 0,
        "verdict": "NO_NEW_LOWCODE_FAMILIES",
    })
    files["next-family-launch-candidate-plan.md"] = (
        "# Next Family Launch Candidate Plan\n\nAll 6 families active."
    )
    files["pdf-release-candidate-publication-packet-v2.md"] = (
        "# PDF RC Publication Packet v2\n\n14 examples, 6 PR packages."
    )
    files["pdf-release-candidate-publication-packet-v2.json"] = json.dumps({
        "pr_packages": [
            {"pr_number": 3, "examples": ["doc-converter", "html", "xls-converter"]},
            {"pr_number": 5, "examples": ["jpeg", "png", "tiff"]},
            {"pr_number": 6, "examples": ["image-extractor", "table-generator", "toc-generator"]},
            {"pr_number": 7, "examples": ["security", "form-flattener"]},
            {"pr_number": 8, "examples": ["form-editor", "form-exporter"]},
            {"pr_number": 9, "examples": ["signature"]},
        ],
        "total_new_examples": 14,
    })
    files["evidence-contract-v6-implementation-report.json"] = json.dumps({
        "contract_version": "6.0.0",
        "categories": 67,
        "verdict": "V6_IMPLEMENTED",
    })
    # v6 git log must contain b7665d4 (Sprint 32 HEAD)
    files["git-log-proof.txt"] = (
        "b7665d4 chore(sprint32-bundle): add v5-validated evidence bundle\n"
        "0f44886 chore(sprint31-bundle): add v4-validated evidence bundle\n"
        "e379cdf chore(sprint30-bundle): add v3-validated evidence bundle\n"
    )
    # v6 final verdict must be a Sprint 33 verdict (md and yaml must agree)
    files["final-verdict.md"] = (
        "# SPRINT33_APPROVAL_BLOCKED_BUT_PORTFOLIO_RELEASE_CANDIDATE_ADVANCED\n\n"
        "All packages clean. Release candidate packet v2 complete."
    )
    files["final-state-summary.yaml"] = (
        "sprint: sprint33\n"
        "verdict: SPRINT33_APPROVAL_BLOCKED_BUT_PORTFOLIO_RELEASE_CANDIDATE_ADVANCED\n"
    )
    # v6 source-state must have sprint33_start_state
    files["source-state-classification.json"] = json.dumps({
        "sprint32_start_state": "CLEAN_FOR_SPRINT_EXECUTION",
        "sprint33_start_state": "CLEAN_FOR_SPRINT_EXECUTION",
        "source_changes_check": {"src_modified": False},
    })
    # v6 bundle identity: report must reference the actual ZIP name
    # (bundle-contract-validation-report.json set with bundle_bytes > 0)
    files["bundle-contract-validation-report.json"] = json.dumps({
        "verdict": "BUNDLE_CONTRACT_PASSED",
        "passed": True,
        "bundle_file": "bundle.zip",  # matches _make_zip's default name
        "bundle_bytes": 12345,
    })
    # families-needing-launch-work.json must NOT list email/slides
    files["families-needing-launch-work.json"] = json.dumps({
        "families_needing_work": [],
        "note": "Email and Slides are PILOT_COMPLETE as of Sprint 32.",
    })
    # scoreboard and release-state must agree on total_published
    files["all-family-launch-scoreboard.json"] = json.dumps({
        "portfolio_summary": {"total_published_examples": 28},
    })
    files["release-state-reconciliation-report.json"] = json.dumps({
        "published_count_reconciliation": {"total": 28},
    })
    return files


# ---------------------------------------------------------------------------
# V6 category count test
# ---------------------------------------------------------------------------

class TestV6CategoryCount:
    def test_v6_has_exactly_67_categories(self):
        """v6 must have exactly 67 categories (53 v5 - 1 removed + 15 added)."""
        assert MIN_CATEGORIES_REQUIRED_V6 == 67, (
            f"v6 must have 67 categories, got {MIN_CATEGORIES_REQUIRED_V6}"
        )


# ---------------------------------------------------------------------------
# v6 contract rejects invalid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV6Rejects:
    """v6 contract must reject bundles that violate v6-specific rules."""

    def test_v6_rejects_wrong_final_verdict(self, tmp_path):
        """final-verdict.md with Sprint 32 verdict (not Sprint 33) must fail v6."""
        files = _minimal_v6_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT32_APPROVAL_BLOCKED_RELEASE_CANDIDATE_AND_CONTRACT_V5_COMPLETE\n"
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("Sprint 33" in f or "allowed" in f.lower() for f in result.failures)

    def test_v6_rejects_wrong_sprint32_head_in_git_log(self, tmp_path):
        """git-log-proof.txt missing Sprint 32 HEAD commit b7665d4 must fail v6."""
        files = _minimal_v6_complete_files()
        files["git-log-proof.txt"] = (
            "0f44886 chore(sprint31-bundle): Sprint 31 only\n"
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("b7665d4" in f for f in result.failures)

    def test_v6_rejects_bundle_bytes_zero(self, tmp_path):
        """bundle-contract-validation-report.json with bundle_bytes=0 must fail v6."""
        files = _minimal_v6_complete_files()
        files["bundle-contract-validation-report.json"] = json.dumps({
            "verdict": "BUNDLE_CONTRACT_PASSED",
            "passed": True,
            "bundle_file": "bundle.zip",
            "bundle_bytes": 0,
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("bundle_bytes" in f for f in result.failures)

    def test_v6_rejects_bundle_file_mismatch(self, tmp_path):
        """bundle-contract-validation-report.json with wrong bundle_file must fail v6."""
        files = _minimal_v6_complete_files()
        files["bundle-contract-validation-report.json"] = json.dumps({
            "verdict": "BUNDLE_CONTRACT_PASSED",
            "passed": True,
            "bundle_file": "sprint32-FINAL.zip",  # wrong — actual is bundle.zip
            "bundle_bytes": 99999,
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("bundle_file" in f for f in result.failures)

    def test_v6_rejects_cross_file_verdict_mismatch(self, tmp_path):
        """final-verdict.md and final-state-summary.yaml must agree on verdict."""
        files = _minimal_v6_complete_files()
        # md says one verdict, yaml says another
        files["final-verdict.md"] = (
            "# SPRINT33_APPROVAL_BLOCKED_BUT_PORTFOLIO_RELEASE_CANDIDATE_ADVANCED\n"
        )
        files["final-state-summary.yaml"] = (
            "sprint: sprint33\nverdict: SPRINT33_PARTIAL_PUBLICATION_AND_PORTFOLIO_ADVANCED\n"
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("verdict mismatch" in f.lower() or "cross-file" in f.lower() for f in result.failures)

    def test_v6_rejects_stale_email_in_families_needing_work(self, tmp_path):
        """families-needing-launch-work.json listing email must fail v6."""
        files = _minimal_v6_complete_files()
        files["families-needing-launch-work.json"] = json.dumps({
            "families_needing_work": ["email", "slides"],
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("stale" in f.lower() or "email" in f.lower() for f in result.failures)

    def test_v6_rejects_words_workflow_root_count_null(self, tmp_path):
        """words-full-sot-classification-report.json with null workflow_root_count must fail."""
        files = _minimal_v6_complete_files()
        files["words-full-sot-classification-report.json"] = json.dumps({
            "workflow_root_count": None,
            "total_types": 25,
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("workflow_root_count" in f for f in result.failures)

    def test_v6_rejects_scoreboard_count_mismatch(self, tmp_path):
        """Scoreboard total != release-state total must fail v6."""
        files = _minimal_v6_complete_files()
        files["all-family-launch-scoreboard.json"] = json.dumps({
            "portfolio_summary": {"total_published_examples": 30},
        })
        files["release-state-reconciliation-report.json"] = json.dumps({
            "published_count_reconciliation": {"total": 28},
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("consistency" in f.lower() or "total_published" in f for f in result.failures)

    def test_v6_rejects_pr7_missing_security(self, tmp_path):
        """PR#7 without security example must fail v6."""
        files = _minimal_v6_complete_files()
        files["pdf-release-candidate-publication-packet-v2.json"] = json.dumps({
            "pr_packages": [
                {"pr_number": 7, "examples": ["form-flattener"]},  # missing security
            ],
            "total_new_examples": 14,
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("security" in f.lower() for f in result.failures)

    def test_v6_rejects_dirty_artifact_policy_bad_verdict(self, tmp_path):
        """dirty-artifact-policy-report.json with unknown verdict must fail v6."""
        files = _minimal_v6_complete_files()
        files["dirty-artifact-policy-report.json"] = json.dumps({
            "verdict": "UNCLASSIFIED",
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("dirty-artifact-policy" in f.lower() or "UNCLASSIFIED" in f for f in result.failures)

    def test_v6_rejects_sprint33_start_state_not_clean(self, tmp_path):
        """source-state-classification.json sprint33_start_state != CLEAN must fail v6."""
        files = _minimal_v6_complete_files()
        files["source-state-classification.json"] = json.dumps({
            "sprint32_start_state": "CLEAN_FOR_SPRINT_EXECUTION",
            "sprint33_start_state": "DIRTY_SOURCE_MODIFIED",
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("sprint33_start_state" in f for f in result.failures)

    def test_v6_rejects_missing_sprint33_categories(self, tmp_path):
        """A bundle missing sprint33-specific categories must fail v6."""
        files = _minimal_v6_complete_files()
        files.pop("sprint32-final-state-reconciliation.json", None)
        files.pop("dirty-artifact-policy-report.json", None)
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert not result.passed
        assert any("sprint32_state_reconciliation" in f or "dirty_artifact_policy" in f
                   for f in result.failures)


# ---------------------------------------------------------------------------
# v6 contract accepts valid bundles
# ---------------------------------------------------------------------------

class TestStrictEvidenceContractV6Accepts:
    """v6 contract must accept correctly formed Sprint 33 bundles."""

    def test_v6_accepts_complete_approval_blocked_bundle(self, tmp_path):
        """A complete Sprint 33 approval-blocked bundle must pass v6."""
        files = _minimal_v6_complete_files()
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert result.passed, f"v6 should pass but failed: {result.failures}"
        assert result.file_count == len(files)
        assert len(result.categories_found) == MIN_CATEGORIES_REQUIRED_V6

    def test_v6_accepts_published_verdict(self, tmp_path):
        """A bundle with Sprint 33 published verdict must pass v6."""
        files = _minimal_v6_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT33_PUBLISHED_MERGED_AND_PORTFOLIO_RELEASE_CANDIDATE_COMPLETE\n\n"
            "All 14 PDF examples merged."
        )
        files["final-state-summary.yaml"] = (
            "sprint: sprint33\n"
            "verdict: SPRINT33_PUBLISHED_MERGED_AND_PORTFOLIO_RELEASE_CANDIDATE_COMPLETE\n"
        )
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert result.passed, f"v6 should pass but failed: {result.failures}"

    def test_v6_accepts_clean_dirty_artifact_policy(self, tmp_path):
        """dirty-artifact-policy-report.json with CLEAN verdict must pass v6."""
        files = _minimal_v6_complete_files()
        files["dirty-artifact-policy-report.json"] = json.dumps({
            "verdict": "DIRTY_ARTIFACT_POLICY_CLEAN",
            "total_dirty_files": 0,
        })
        zip_path = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV6().validate_zip(zip_path)
        assert result.passed, f"v6 should pass but failed: {result.failures}"

    def test_v6_contract_definition_version(self):
        """contract_definition_v6 must return version 6.0.0."""
        defn = contract_definition_v6()
        assert defn["contract_version"] == "6.0.0"

    def test_v6_contract_definition_has_all_combined_categories(self):
        """contract_definition_v6 must include all COMBINED_CATEGORIES_V6 keys."""
        defn = contract_definition_v6()
        assert set(defn["required_categories"].keys()) == set(COMBINED_CATEGORIES_V6.keys())

    def test_v6_contract_definition_lists_allowed_verdicts(self):
        """contract_definition_v6 must list all allowed Sprint 33 verdicts."""
        defn = contract_definition_v6()
        assert set(defn["allowed_verdicts"]) == set(ALLOWED_VERDICTS_V6)

    def test_v6_contract_definition_documents_category_reconciliation(self):
        """contract_definition_v6 must document the v5→v6 delta."""
        defn = contract_definition_v6()
        recon = defn["category_count_reconciliation"]
        assert recon["v5_categories"] == 53
        assert recon["v6_categories"] == 67
        assert "sprint31_state_reconciliation" in recon["categories_removed_from_v5"]
        assert "sprint32_state_reconciliation" in recon["categories_added_in_v6"]
        assert "dirty_artifact_policy" in recon["categories_added_in_v6"]
        assert "words_sot_classification" in recon["categories_added_in_v6"]

    def test_v6_v5_v4_v3_v2_v1_categories_disjoint_from_each_other(self):
        """Each version must have a unique total category count."""
        counts = [
            len(COMBINED_CATEGORIES_V5),
            len(COMBINED_CATEGORIES_V6),
        ]
        assert counts[0] == 53
        assert counts[1] == 67
        assert counts[0] != counts[1]


# ---------------------------------------------------------------------------
# V7 Tests — Sprint 34 README Healing
# ---------------------------------------------------------------------------

def _minimal_v7_complete_files() -> dict[str, str]:
    """Return files satisfying all 69 v7 required categories with valid content."""
    files = dict(_minimal_v6_complete_files())
    # v7 new categories
    files["readme-sync-audit.json"] = json.dumps({
        "audit_type": "readme_sync",
        "family_audits": [
            {"family": "pdf", "inventory_count": 17, "readme_count": 17, "is_stale": False}
        ],
        "all_families_in_sync": True,
    })
    files["readme-coverage-audit-before.json"] = json.dumps({
        "audit_type": "readme_coverage_audit_before",
        "family_audits": [
            {"family": "pdf", "readme_count": 3, "is_stale": True}
        ],
    })
    files["readme-coverage-audit-after.json"] = json.dumps({
        "audit_type": "readme_coverage_audit_after",
        "family_audits": [
            {"family": "pdf", "readme_count": 17, "is_stale": False}
        ],
    })
    # v7 final verdict must be Sprint 34
    files["final-verdict.md"] = (
        "# SPRINT34_README_HEALING_COMPLETE\n\n"
        "All 6 families have cumulative READMEs. PDF healed from 3 to 17 examples."
    )
    files["final-state-summary.yaml"] = (
        "sprint: sprint34\n"
        "verdict: SPRINT34_README_HEALING_COMPLETE\n"
    )
    return files


class TestStrictEvidenceContractV7Accepts:

    def test_v7_accepts_complete_readme_healing_bundle(self, tmp_path):
        files = _minimal_v7_complete_files()
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV7().validate_zip(zp)
        assert result.passed, f"V7 validation failed: {result.failures}"
        assert result.verdict == "BUNDLE_CONTRACT_PASSED"
        assert len(result.categories_found) >= 69

    def test_v7_contract_definition_version(self):
        defn = StrictEvidenceContractV7.contract_definition()
        assert defn["version"] == "v7"

    def test_v7_contract_definition_has_69_categories(self):
        defn = StrictEvidenceContractV7.contract_definition()
        assert defn["min_categories_required"] == 69
        assert len(defn["required_categories"]) == 69

    def test_v7_contract_lists_readme_categories(self):
        defn = StrictEvidenceContractV7.contract_definition()
        cats = defn["required_categories"]
        assert "readme_sync_audit" in cats
        assert "readme_coverage_audit" in cats

    def test_v7_category_reconciliation(self):
        defn = StrictEvidenceContractV7.contract_definition()
        recon = defn["category_count_reconciliation"]
        assert recon["v6_categories"] == 67
        assert recon["v7_categories"] == 69
        assert "readme_sync_audit" in recon["categories_added_in_v7"]
        assert "readme_coverage_audit" in recon["categories_added_in_v7"]

    def test_v7_v6_categories_superset(self):
        """V7 must contain all V6 categories."""
        for cat in COMBINED_CATEGORIES_V6:
            assert cat in COMBINED_CATEGORIES_V7, f"V7 missing V6 category: {cat}"

    def test_v7_unique_category_count(self):
        """Each version has a unique count."""
        assert MIN_CATEGORIES_REQUIRED_V6 == 67
        assert MIN_CATEGORIES_REQUIRED_V7 == 69
        assert MIN_CATEGORIES_REQUIRED_V6 != MIN_CATEGORIES_REQUIRED_V7


class TestStrictEvidenceContractV7Rejects:

    def test_v7_rejects_missing_readme_sync(self, tmp_path):
        files = _minimal_v7_complete_files()
        del files["readme-sync-audit.json"]
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV7().validate_zip(zp)
        assert not result.passed
        assert "readme_sync_audit" in result.categories_missing

    def test_v7_rejects_missing_coverage_audit(self, tmp_path):
        files = _minimal_v7_complete_files()
        del files["readme-coverage-audit-before.json"]
        del files["readme-coverage-audit-after.json"]
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV7().validate_zip(zp)
        assert not result.passed
        assert "readme_coverage_audit" in result.categories_missing

    def test_v7_rejects_stale_sync_audit(self, tmp_path):
        files = _minimal_v7_complete_files()
        files["readme-sync-audit.json"] = json.dumps({
            "audit_type": "readme_sync",
            "all_families_in_sync": False,
        })
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV7().validate_zip(zp)
        assert not result.passed
        assert any("all_families_in_sync" in f for f in result.failures)

    def test_v7_rejects_wrong_verdict(self, tmp_path):
        files = _minimal_v7_complete_files()
        files["final-verdict.md"] = "# SPRINT33_SOME_OLD_VERDICT\n\nWrong sprint."
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV7().validate_zip(zp)
        assert not result.passed
        assert any("Sprint 34 verdict" in f for f in result.failures)


# ---------------------------------------------------------------------------
# V8 Tests — Format Capability Manifest Category
# ---------------------------------------------------------------------------

def _minimal_v8_complete_files() -> dict[str, str]:
    """Return files satisfying all 70 v8 required categories with valid content."""
    files = dict(_minimal_v7_complete_files())
    # v8 new category: format-capability-manifest
    files["format-capability-manifest-cells.json"] = json.dumps({
        "family": "cells",
        "generation_date": "2026-05-19T08:00:00+00:00",
        "types": {"SpreadsheetConverter": {"operation_kind": "converter"}},
    })
    # Update verdict to V8
    files["final-verdict.md"] = (
        "# FORMAT_LIFECYCLE_V8_AUDITOR_VERIFIED\n\n"
        "All format lifecycle gaps resolved."
    )
    return files


class TestStrictEvidenceContractV8Accepts:

    def test_v8_accepts_complete_bundle(self, tmp_path):
        files = _minimal_v8_complete_files()
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV8().validate_zip(zp)
        assert result.passed, f"V8 validation failed: {result.failures}"
        assert result.verdict == "BUNDLE_CONTRACT_PASSED"
        assert len(result.categories_found) >= 70

    def test_v8_contract_definition_version(self):
        defn = StrictEvidenceContractV8.contract_definition()
        assert defn["version"] == "v8"

    def test_v8_contract_definition_has_70_categories(self):
        defn = StrictEvidenceContractV8.contract_definition()
        assert defn["min_categories_required"] == 70
        assert len(defn["required_categories"]) == 70

    def test_v8_contract_lists_format_capability_manifest(self):
        defn = StrictEvidenceContractV8.contract_definition()
        cats = defn["required_categories"]
        assert "format_capability_manifest" in cats

    def test_v8_category_reconciliation(self):
        defn = StrictEvidenceContractV8.contract_definition()
        recon = defn["category_count_reconciliation"]
        assert recon["v7_categories"] == 69
        assert recon["v8_categories"] == 70
        assert "format_capability_manifest" in recon["categories_added_in_v8"]

    def test_v8_v7_categories_superset(self):
        """V8 must contain all V7 categories."""
        for cat in COMBINED_CATEGORIES_V7:
            assert cat in COMBINED_CATEGORIES_V8, f"V8 missing V7 category: {cat}"

    def test_v8_unique_category_count(self):
        """Each version has a unique count."""
        assert MIN_CATEGORIES_REQUIRED_V7 == 69
        assert MIN_CATEGORIES_REQUIRED_V8 == 70
        assert MIN_CATEGORIES_REQUIRED_V7 != MIN_CATEGORIES_REQUIRED_V8

    def test_v8_accepts_v7_verdict_for_backward_compat(self, tmp_path):
        """V8 contract should also accept V7 verdicts."""
        files = _minimal_v8_complete_files()
        files["final-verdict.md"] = (
            "# SPRINT37_APPROVAL_BLOCKED_PORTFOLIO_ADVANCED_VERSION_DRIFT_PILOTED\n\n"
            "V7 verdict in V8 bundle."
        )
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV8().validate_zip(zp)
        assert result.passed, f"V8 should accept V7 verdict: {result.failures}"


class TestStrictEvidenceContractV8Rejects:

    def test_v8_rejects_missing_format_capability_manifest(self, tmp_path):
        files = _minimal_v7_complete_files()
        # V7 files but no format-capability-manifest and V8 verdict
        files["final-verdict.md"] = (
            "# FORMAT_LIFECYCLE_V8_AUDITOR_VERIFIED\n\nMissing manifest."
        )
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV8().validate_zip(zp)
        assert not result.passed
        assert "format_capability_manifest" in result.categories_missing

    def test_v8_rejects_invalid_manifest_json(self, tmp_path):
        files = _minimal_v8_complete_files()
        # Replace manifest with invalid JSON
        files["format-capability-manifest-cells.json"] = "not valid json"
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV8().validate_zip(zp)
        assert not result.passed
        assert any("valid JSON" in f for f in result.failures)

    def test_v8_rejects_manifest_without_family_key(self, tmp_path):
        files = _minimal_v8_complete_files()
        files["format-capability-manifest-cells.json"] = json.dumps({"not_family": "cells"})
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV8().validate_zip(zp)
        assert not result.passed
        assert any("family" in f for f in result.failures)

    def test_v8_rejects_wrong_verdict(self, tmp_path):
        files = _minimal_v8_complete_files()
        files["final-verdict.md"] = "# SOME_UNKNOWN_VERDICT\n\nWrong."
        zp = _make_zip(tmp_path, files)
        result = StrictEvidenceContractV8().validate_zip(zp)
        assert not result.passed
        assert any("verdict" in f.lower() for f in result.failures)


# ---------------------------------------------------------------------------
# Planner Sprint Evidence Contract Tests
# ---------------------------------------------------------------------------

def _minimal_planner_complete_files() -> dict[str, str]:
    """Return minimum files needed to pass the planner sprint evidence contract."""
    return {
        "final-state-summary.json": json.dumps({"head": "abc123", "verdict": "TEST"}),
        "final-state-summary.md": "# Final State Summary\n",
        "final-next-actions.json": json.dumps({"generated_from_head": "abc123"}),
        "final-next-actions.md": "# Final Next Actions\n",
        "final-git-status.txt": "nothing to commit\n",
        "final-git-log.txt": "abc123 test commit\n",
        "final-git-diff-stat.txt": "0 files changed\n",
        "final-changed-files.txt": "",
        "test-full-log.txt": "100 passed\n",
        "test-targeted-log.txt": "50 passed\n",
        "planner-cycle-01.json": json.dumps({"cycle": 1}),
        "final-planner-board.json": json.dumps({"actions": []}),
        "planner-loop-ledger.json": json.dumps({"cycles": []}),
        "final-dirty-state.json": json.dumps({"actionable_count": 0}),
        "taskcard-state.json": json.dumps({"open_taskcards": []}),
        "taskcard-state.md": "# Taskcard State\n",
        "local-metrics.json": json.dumps({"sprint": 46}),
        "bundle-manifest.json": json.dumps({"files": [{"file": "x", "sha256": "abc"}]}),
        "no-secret-proof.txt": "No secrets found.\n",
        "execution-ledger.md": "# Execution Ledger\n",
    }


class TestPlannerSprintEvidenceContract:
    def test_planner_categories_count(self):
        assert MIN_PLANNER_CATEGORIES_REQUIRED == 17

    def test_complete_planner_bundle_passes(self, tmp_path):
        files = _minimal_planner_complete_files()
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert result.passed
        assert result.verdict == "PLANNER_CONTRACT_PASSED"

    def test_missing_raw_logs_fails(self, tmp_path):
        files = _minimal_planner_complete_files()
        del files["test-full-log.txt"]
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert not result.passed
        assert any("test_full_log" in f for f in result.failures)

    def test_missing_final_git_proof_fails(self, tmp_path):
        files = _minimal_planner_complete_files()
        del files["final-git-status.txt"]
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert not result.passed
        assert any("final_git_status" in f for f in result.failures)

    def test_missing_planner_cycle_fails(self, tmp_path):
        files = _minimal_planner_complete_files()
        del files["planner-cycle-01.json"]
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert not result.passed

    def test_missing_dirty_state_proof_fails(self, tmp_path):
        files = _minimal_planner_complete_files()
        del files["final-dirty-state.json"]
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert not result.passed

    def test_missing_manifest_fails(self, tmp_path):
        files = _minimal_planner_complete_files()
        del files["bundle-manifest.json"]
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert not result.passed

    def test_missing_head_in_summary_fails(self, tmp_path):
        files = _minimal_planner_complete_files()
        files["final-state-summary.json"] = json.dumps({"verdict": "X"})
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert not result.passed
        assert any("head" in f for f in result.failures)

    def test_missing_generated_from_head_fails(self, tmp_path):
        files = _minimal_planner_complete_files()
        files["final-next-actions.json"] = json.dumps({"actions": []})
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert not result.passed
        assert any("generated_from_head" in f for f in result.failures)

    def test_manifest_without_sha256_fails(self, tmp_path):
        files = _minimal_planner_complete_files()
        files["bundle-manifest.json"] = json.dumps({"files": [{"file": "x"}]})
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert not result.passed

    def test_secret_in_planner_bundle_fails(self, tmp_path):
        files = _minimal_planner_complete_files()
        files["no-secret-proof.txt"] = "Found token: ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"
        zp = _make_zip(tmp_path, files)
        result = PlannerSprintEvidenceContract().validate_zip(zp)
        assert not result.passed
        assert len(result.secret_violations) > 0

    def test_nonexistent_zip_fails(self, tmp_path):
        result = PlannerSprintEvidenceContract().validate_zip(tmp_path / "nope.zip")
        assert not result.passed

    def test_contract_definition_has_required_fields(self):
        defn = PlannerSprintEvidenceContract.contract_definition()
        assert defn["version"] == "planner-v1"
        assert defn["min_categories_required"] == MIN_PLANNER_CATEGORIES_REQUIRED
        assert "required_categories" in defn

    def test_allowed_planner_verdicts_defined(self):
        assert len(ALLOWED_PLANNER_VERDICTS) >= 5


class TestGenerateValidationProof:
    def test_proof_names_correct_zip_path(self, tmp_path):
        files = _minimal_planner_complete_files()
        zp = _make_zip(tmp_path, files)
        proof = generate_validation_proof(zp)
        assert proof["validated_bundle"] == str(zp)
        assert proof["result"]["passed"] is True

    def test_proof_includes_sha256(self, tmp_path):
        files = _minimal_planner_complete_files()
        zp = _make_zip(tmp_path, files)
        proof = generate_validation_proof(zp)
        assert len(proof["validated_bundle_sha256"]) == 64

    def test_proof_writes_to_output_path(self, tmp_path):
        files = _minimal_planner_complete_files()
        zp = _make_zip(tmp_path, files)
        out = tmp_path / "proof.json"
        proof = generate_validation_proof(zp, output_path=out)
        assert out.exists()
        import json
        written = json.loads(out.read_text())
        assert written["validated_bundle"] == str(zp)
        assert written["result"]["verdict"] == "PLANNER_CONTRACT_PASSED"

    def test_proof_fails_for_incomplete_bundle(self, tmp_path):
        files = _minimal_planner_complete_files()
        del files["test-full-log.txt"]
        zp = _make_zip(tmp_path, files)
        proof = generate_validation_proof(zp)
        assert proof["result"]["passed"] is False
        assert proof["result"]["failure_count"] > 0

    def test_proof_rejects_nonexistent_zip(self, tmp_path):
        import pytest
        with pytest.raises(FileNotFoundError):
            generate_validation_proof(tmp_path / "missing.zip")

    def test_proof_has_contract_metadata(self, tmp_path):
        files = _minimal_planner_complete_files()
        zp = _make_zip(tmp_path, files)
        proof = generate_validation_proof(zp)
        assert proof["contract"] == "PlannerSprintEvidenceContract"
        assert proof["contract_version"] == "planner-v1"
        assert "validation_timestamp" in proof

    def test_proof_path_never_stale(self, tmp_path):
        """Two different ZIPs produce proofs naming their own paths."""
        files = _minimal_planner_complete_files()
        (tmp_path / "a").mkdir()
        (tmp_path / "b").mkdir()
        zp1 = _make_zip(tmp_path / "a", files)
        zp2 = _make_zip(tmp_path / "b", files)
        proof1 = generate_validation_proof(zp1)
        proof2 = generate_validation_proof(zp2)
        assert proof1["validated_bundle"] != proof2["validated_bundle"]
        assert str(zp1) in proof1["validated_bundle"]
        assert str(zp2) in proof2["validated_bundle"]


class TestCompanionProof:
    def test_companion_proof_written_next_to_zip(self, tmp_path):
        files = _minimal_planner_complete_files()
        zp = _make_zip(tmp_path, files)
        proof = generate_companion_proof(zp)
        companion = zp.parent / (zp.name + ".validation.json")
        assert companion.exists()
        assert proof["result"]["passed"] is True

    def test_companion_proof_hash_matches_zip(self, tmp_path):
        import hashlib
        files = _minimal_planner_complete_files()
        zp = _make_zip(tmp_path, files)
        expected_sha = hashlib.sha256(zp.read_bytes()).hexdigest()
        proof = generate_companion_proof(zp)
        assert proof["validated_bundle_sha256"] == expected_sha

    def test_companion_proof_names_zip_path(self, tmp_path):
        files = _minimal_planner_complete_files()
        zp = _make_zip(tmp_path, files)
        proof = generate_companion_proof(zp)
        assert str(zp) in proof["validated_bundle"]

    def test_companion_proof_fails_for_incomplete_bundle(self, tmp_path):
        files = _minimal_planner_complete_files()
        del files["test-full-log.txt"]
        zp = _make_zip(tmp_path, files)
        proof = generate_companion_proof(zp)
        assert proof["result"]["passed"] is False
        companion = zp.parent / (zp.name + ".validation.json")
        assert companion.exists()


class TestHeadConsistency:
    def test_consistent_heads(self, tmp_path):
        import json
        for name in ["final-state-summary.json", "final-next-actions.json",
                      "final-dirty-state.json", "local-metrics.json"]:
            key = {"final-state-summary.json": "head",
                   "final-next-actions.json": "generated_from_head",
                   "final-dirty-state.json": "captured_at_head",
                   "local-metrics.json": "head"}[name]
            (tmp_path / name).write_text(json.dumps({key: "abc1234"}))
        result = check_head_consistency(tmp_path)
        assert result["consistent"] is True
        assert result["heads_found"] == ["abc1234"]

    def test_inconsistent_heads(self, tmp_path):
        import json
        (tmp_path / "final-state-summary.json").write_text(json.dumps({"head": "aaa"}))
        (tmp_path / "final-next-actions.json").write_text(json.dumps({"generated_from_head": "bbb"}))
        result = check_head_consistency(tmp_path)
        assert result["consistent"] is False
        assert len(result["heads_found"]) == 2

    def test_missing_artifacts_tolerated(self, tmp_path):
        import json
        (tmp_path / "final-state-summary.json").write_text(json.dumps({"head": "xyz"}))
        result = check_head_consistency(tmp_path)
        assert result["consistent"] is True
