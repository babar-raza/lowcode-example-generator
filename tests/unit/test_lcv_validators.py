"""Tests for LowCode Completeness Validators (LCV-01..LCV-15)."""

import json
from pathlib import Path

import pytest

from src.plugin_examples.fixture_factory.lowcode_completeness_validators import LcvResult, run_all_lcv_checks


def complete_closeout(**overrides):
    base = {
        "verdict": "SPRINT_COMPLETE",
        "final_verdict": "APPROVAL_BLOCKED",
        "final_verdict_reason": "All local work complete. Only external gates remain.",
        "taskcards": {"total": 60, "complete": 60, "pending": 0, "iv_prerequisite_satisfied": True},
        "evidence_bundle": {
            "sha256": "abc123",
            "external_sidecar": ".local/evidence-bundles/test.sha256",
            "protocol_note": "SHA is authoritative in external sidecar only (v2 protocol)",
        },
        "iv_verdict": "IV_PASS",
        "adversarial_review_verdict": "ADVERSARIAL_REVIEW_PASS",
        "prs_created": 3,
        "pr_urls": [
            "https://github.com/org/repo/pull/1",
            "https://github.com/org/repo2/pull/1",
            "https://github.com/org/repo3/pull/1",
        ],
        "pclc_total": 38,
        "published": 0,
    }
    base.update(overrides)
    return base


def test_lcv_passes_on_valid_closeout(tmp_path):
    (tmp_path / "final").mkdir()
    (tmp_path / "final" / "git-status-final.txt").write_text("clean")
    (tmp_path / "pr-review").mkdir()
    (tmp_path / "pr-review" / "barcode-review.json").write_text("{}")
    (tmp_path / "publication" / "pr-packets").mkdir(parents=True)
    (tmp_path / "publication" / "pr-packets" / "pr-packet.json").write_text("{}")
    (tmp_path / "workspace-hygiene").mkdir()
    (tmp_path / "workspace-hygiene" / "dirty-state-classification.json").write_text("{}")
    co = complete_closeout()
    result = run_all_lcv_checks(co, tmp_path)
    assert result.passes, f"Expected PASS but got errors: {result.violations}"


def test_lcv_03_missing_sidecar():
    co = complete_closeout()
    co["evidence_bundle"] = {"sha256": "abc"}  # no external_sidecar
    result = run_all_lcv_checks(co, Path("/tmp/nonexistent"))
    rules = [v.rule for v in result.violations]
    assert "LCV-03" in rules


def test_lcv_04_missing_sha():
    co = complete_closeout()
    co["evidence_bundle"] = {"external_sidecar": "test.sha256"}  # no sha256
    result = run_all_lcv_checks(co, Path("/tmp/nonexistent"))
    rules = [v.rule for v in result.violations]
    assert "LCV-04" in rules


def test_lcv_05_iv_not_pass():
    co = complete_closeout(iv_verdict="IV_PENDING")
    result = run_all_lcv_checks(co, Path("/tmp/nonexistent"))
    rules = [v.rule for v in result.violations]
    assert "LCV-05" in rules


def test_lcv_06_adversarial_not_pass():
    co = complete_closeout(adversarial_review_verdict="ADVERSARIAL_REVIEW_PENDING")
    result = run_all_lcv_checks(co, Path("/tmp/nonexistent"))
    rules = [v.rule for v in result.violations]
    assert "LCV-06" in rules


def test_lcv_08_pr_created_no_urls():
    co = complete_closeout(prs_created=3, pr_urls=[])
    result = run_all_lcv_checks(co, Path("/tmp/nonexistent"))
    rules = [v.rule for v in result.violations]
    assert "LCV-08" in rules


def test_lcv_09_published_without_evidence():
    co = complete_closeout(published=5)
    result = run_all_lcv_checks(co, Path("/tmp/nonexistent"))
    rules = [v.rule for v in result.violations]
    assert "LCV-09" in rules


def test_lcv_12_missing_git_status(tmp_path):
    # No git-status-final.txt
    co = complete_closeout()
    result = run_all_lcv_checks(co, tmp_path)
    rules = [v.rule for v in result.violations]
    assert "LCV-12" in rules


def test_lcv_15_approval_blocked_with_failing_iv():
    co = complete_closeout(iv_verdict="IV_FAIL", adversarial_review_verdict="ADVERSARIAL_REVIEW_PASS")
    result = run_all_lcv_checks(co, Path("/tmp/nonexistent"))
    rules = [v.rule for v in result.violations]
    assert "LCV-05" in rules or "LCV-15" in rules
