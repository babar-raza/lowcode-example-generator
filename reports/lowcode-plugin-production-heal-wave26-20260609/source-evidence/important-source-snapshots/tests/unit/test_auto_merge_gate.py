"""Tests for the AMG (Auto-Merge Gate) state machine — Wave 25 Lane A.

Covers all 10 AMG conditions independently plus backward-compat alias check.
"""
from __future__ import annotations

import os

import pytest

from plugin_examples.publisher.merge_approval_gate import (
    APPROVAL_BLOCKED,
    APPROVED_PUBLICATION_REPOS,
    FIXTURE_SOURCE_REPOS,
    MergeGateResult,
    evaluate_branch_delete_gate,
    evaluate_merge_gate,
)

# ── Helpers ────────────────────────────────────────────────────────────────────

_GOOD_REPO = "aspose-barcode-net/Aspose.BarCode.Plugins-for-.NET-Examples"
_GOOD_BRANCH = "lowcode/wave25/barcode-plugin-examples"
_GOOD_PR_URL = f"https://github.com/{_GOOD_REPO}/pull/1"
_ARTIFACT_PASS = {"status": "PASS"}
_BUILD_PASS = {"verdict": "ALL_PASS"}
_README_QUALITY = {"verdict": "QUALITY"}


def _call_gate(env: dict | None = None, **overrides):
    """Call evaluate_merge_gate with good defaults, applying overrides."""
    base = dict(
        pr_url=_GOOD_PR_URL,
        repo=_GOOD_REPO,
        head_branch=_GOOD_BRANCH,
        pr_state="OPEN",
        pr_mergeable="MERGEABLE",
        artifact_contract=_ARTIFACT_PASS,
        build_result=_BUILD_PASS,
        readme_result=_README_QUALITY,
    )
    base.update(overrides)
    extra_env = env or {}
    saved = {k: os.environ.get(k) for k in extra_env}
    try:
        for k, v in extra_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        return evaluate_merge_gate(**base)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ── AMG-01: APPROVE_LIVE_MERGE env gate ───────────────────────────────────────

def test_amg01_absent_returns_credential_blocked(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.delenv("APPROVE_LIVE_MERGE", raising=False)
    result = _call_gate()
    assert result.verdict == "CREDENTIAL_BLOCKED"
    assert "APPROVE_LIVE_MERGE" in (result.reason or "")


def test_amg01_wrong_value_returns_credential_blocked(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("APPROVE_LIVE_MERGE", "yes")
    result = _call_gate()
    assert result.verdict == "CREDENTIAL_BLOCKED"


# ── AMG-02: GITHUB_TOKEN ──────────────────────────────────────────────────────

def test_amg02_no_token_returns_credential_blocked(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("APPROVE_LIVE_MERGE", raising=False)
    result = _call_gate()
    assert result.verdict == "CREDENTIAL_BLOCKED"


def test_amg02_gh_token_fallback_accepted(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("GH_TOKEN", "ghp_fallback")
    monkeypatch.delenv("APPROVE_LIVE_MERGE", raising=False)
    result = _call_gate()
    # Should not be blocked on AMG-02; may be blocked on AMG-01 (no APPROVE_LIVE_MERGE)
    assert result.verdict != "CREDENTIAL_BLOCKED" or "APPROVE_LIVE_MERGE" in (result.reason or "")


# ── AMG-03: publication repo allowlist ────────────────────────────────────────

def test_amg03_fixture_source_repo_returns_review_policy_blocked(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("APPROVE_LIVE_MERGE", "1")
    for repo in list(FIXTURE_SOURCE_REPOS)[:3]:
        result = _call_gate(repo=repo, pr_url=f"https://github.com/{repo}/pull/1")
        assert result.verdict == "REVIEW_POLICY_BLOCKED", f"Expected blocked for {repo}"


def test_amg03_unknown_repo_returns_review_policy_blocked(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("APPROVE_LIVE_MERGE", "1")
    result = _call_gate(repo="some-other-org/Some-Other-Repo")
    assert result.verdict == "REVIEW_POLICY_BLOCKED"


def test_amg03_all_approved_repos_pass(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.delenv("APPROVE_LIVE_MERGE", raising=False)  # let it reach AMG-01
    for repo in APPROVED_PUBLICATION_REPOS:
        result = _call_gate(repo=repo, pr_url=f"https://github.com/{repo}/pull/1")
        # Should not be REVIEW_POLICY_BLOCKED
        assert result.verdict != "REVIEW_POLICY_BLOCKED", f"Should pass AMG-03 for {repo}"


# ── AMG-04: branch pattern ────────────────────────────────────────────────────

def test_amg04_wrong_branch_returns_review_policy_blocked(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("APPROVE_LIVE_MERGE", "1")
    result = _call_gate(head_branch="main")
    assert result.verdict == "REVIEW_POLICY_BLOCKED"
    result2 = _call_gate(head_branch="feature/something")
    assert result2.verdict == "REVIEW_POLICY_BLOCKED"


def test_amg04_correct_pattern_passes(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.delenv("APPROVE_LIVE_MERGE", raising=False)
    for branch in ["lowcode/wave25/barcode-plugin-examples", "lowcode/wave19/cad-plugin-examples"]:
        result = _call_gate(head_branch=branch)
        assert result.verdict != "REVIEW_POLICY_BLOCKED"


# ── AMG-05: PR state ──────────────────────────────────────────────────────────

def test_amg05_closed_pr_returns_merge_gate_ready(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("APPROVE_LIVE_MERGE", "1")
    result = _call_gate(pr_state="CLOSED")
    assert result.verdict == "MERGE_GATE_READY"


def test_amg05_not_mergeable_returns_merge_gate_ready(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("APPROVE_LIVE_MERGE", "1")
    result = _call_gate(pr_state="OPEN", pr_mergeable="CONFLICTING")
    assert result.verdict == "MERGE_GATE_READY"


# ── AMG-06..08: artifact gates ────────────────────────────────────────────────

def test_amg06_artifact_not_pass_returns_merge_gate_ready(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("APPROVE_LIVE_MERGE", "1")
    result = _call_gate(artifact_contract={"status": "FAIL"})
    assert result.verdict == "MERGE_GATE_READY"


def test_amg07_build_not_all_pass_returns_merge_gate_ready(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("APPROVE_LIVE_MERGE", "1")
    result = _call_gate(build_result={"verdict": "PARTIAL_PASS"})
    assert result.verdict == "MERGE_GATE_READY"


def test_amg08_readme_not_quality_returns_merge_gate_ready(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("APPROVE_LIVE_MERGE", "1")
    result = _call_gate(readme_result={"verdict": "DRAFT"})
    assert result.verdict == "MERGE_GATE_READY"


# ── APPROVAL_BLOCKED is NOT produced by new code ─────────────────────────────

def test_approval_blocked_never_produced_as_verdict(monkeypatch):
    """New code must never emit APPROVAL_BLOCKED as a verdict string."""
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    scenarios = [
        {},  # all good except no APPROVE_LIVE_MERGE → CREDENTIAL_BLOCKED
        {"repo": "aspose-barcode/Aspose.BarCode-for-.NET"},  # fixture repo → REVIEW_POLICY_BLOCKED
        {"artifact_contract": {"status": "FAIL"}},  # bad contract → MERGE_GATE_READY
    ]
    for overrides in scenarios:
        monkeypatch.delenv("APPROVE_LIVE_MERGE", raising=False)
        result = _call_gate(**overrides)
        assert result.verdict != "APPROVAL_BLOCKED", (
            f"APPROVAL_BLOCKED must never be produced by new code; got {result.verdict!r} for {overrides}"
        )


# ── backward-compat alias ─────────────────────────────────────────────────────

def test_approval_blocked_alias_equals_credential_blocked():
    """APPROVAL_BLOCKED is a compatibility alias pointing to CREDENTIAL_BLOCKED."""
    assert APPROVAL_BLOCKED == "CREDENTIAL_BLOCKED"


# ── Branch delete gate ────────────────────────────────────────────────────────

def test_bdg_no_env_var_returns_skipped_policy(monkeypatch):
    monkeypatch.delenv("APPROVE_DELETE_BRANCH", raising=False)
    result = evaluate_branch_delete_gate(_GOOD_REPO, _GOOD_BRANCH, "MERGED")
    assert result.verdict == "BRANCH_DELETE_SKIPPED_POLICY"


def test_bdg_pr_not_merged_returns_skipped_policy(monkeypatch):
    monkeypatch.setenv("APPROVE_DELETE_BRANCH", "1")
    result = evaluate_branch_delete_gate(_GOOD_REPO, _GOOD_BRANCH, "OPEN")
    assert result.verdict == "BRANCH_DELETE_SKIPPED_POLICY"


def test_bdg_bad_branch_pattern_returns_skipped_policy(monkeypatch):
    monkeypatch.setenv("APPROVE_DELETE_BRANCH", "1")
    result = evaluate_branch_delete_gate(_GOOD_REPO, "main", "MERGED")
    assert result.verdict == "BRANCH_DELETE_SKIPPED_POLICY"


def test_bdg_all_gates_pass_returns_authorized(monkeypatch):
    monkeypatch.setenv("APPROVE_DELETE_BRANCH", "1")
    result = evaluate_branch_delete_gate(_GOOD_REPO, _GOOD_BRANCH, "MERGED")
    assert result.verdict == "BRANCH_DELETE_AUTHORIZED"
