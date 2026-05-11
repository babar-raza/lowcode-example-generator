"""Tests for monthly runbook correctness and CI environment docs."""

import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RUNBOOK_PATH = _REPO_ROOT / "workspace" / "verification" / "latest" / "monthly-maintenance-runbook.json"
_CI_DOCS_PATH = _REPO_ROOT / "docs" / "ci" / "environment-variables.md"


class TestMonthlyRunbook:
    """Validate monthly-maintenance-runbook.json for correctness."""

    def _load_runbook(self) -> dict:
        assert _RUNBOOK_PATH.exists(), f"Runbook not found: {_RUNBOOK_PATH}"
        return json.loads(_RUNBOOK_PATH.read_text(encoding="utf-8"))

    def test_monthly_runbook_uses_github_token(self):
        """Runbook must not reference $GH_TOKEN; only $GITHUB_TOKEN is allowed."""
        runbook_text = _RUNBOOK_PATH.read_text(encoding="utf-8")
        assert "$GH_TOKEN" not in runbook_text, (
            "monthly-maintenance-runbook.json references $GH_TOKEN. "
            "All GitHub token references must use $GITHUB_TOKEN (token policy sprint closure)."
        )
        assert "GITHUB_TOKEN" in runbook_text, (
            "Runbook must reference GITHUB_TOKEN for GitHub operations."
        )

    def test_monthly_runbook_pdf_blocked_until_is_not_stale(self):
        """pdf_blocked_until must not reference the now-CLOSED followup-pdf-reflection-dedup taskcard."""
        runbook = self._load_runbook()
        pdf_blocked = runbook.get("immutable_rules", {}).get("pdf_blocked_until", "")
        # The taskcard is CLOSED — the runbook should not say "followup-pdf-reflection-dedup resolved" as a future condition
        assert "followup-pdf-reflection-dedup resolved" not in pdf_blocked or "RESOLVED" in pdf_blocked, (
            "pdf_blocked_until still says the taskcard needs to be resolved, "
            "but followup-pdf-reflection-dedup is CLOSED. Update the runbook."
        )

    def test_monthly_runbook_step1_does_not_use_check_command(self):
        """Step 1 must not use the non-existent 'check' CLI subcommand."""
        runbook = self._load_runbook()
        steps = runbook.get("steps", [])
        step1 = next((s for s in steps if s.get("step") == 1), None)
        assert step1 is not None, "Step 1 not found in runbook"
        cmd = step1.get("command", "")
        assert "plugin_examples check" not in cmd, (
            "Step 1 references 'plugin_examples check' which does not exist as a real command. "
            "Use 'discover-lowcode' instead."
        )

    def test_monthly_runbook_has_required_fields(self):
        """Runbook must have required top-level fields."""
        runbook = self._load_runbook()
        for field in ["runbook_type", "steps", "immutable_rules"]:
            assert field in runbook, f"Missing required runbook field: {field}"

    def test_monthly_runbook_merge_approval_is_separate(self):
        """Runbook must document that APPROVE_MERGE_PR is separate from APPROVE_LIVE_PR."""
        runbook = self._load_runbook()
        rules = runbook.get("immutable_rules", {})
        assert rules.get("merge_approval_separate_from_live_pr") is True, (
            "immutable_rules.merge_approval_separate_from_live_pr must be true"
        )


class TestCIEnvDocs:
    """Validate docs/ci/environment-variables.md exists and documents required vars."""

    def test_ci_docs_file_exists(self):
        """docs/ci/environment-variables.md must exist."""
        assert _CI_DOCS_PATH.exists(), f"CI env docs not found: {_CI_DOCS_PATH}"

    def test_ci_docs_include_required_env_vars(self):
        """CI env docs must document all required environment variables."""
        content = _CI_DOCS_PATH.read_text(encoding="utf-8")
        required_vars = [
            "GITHUB_TOKEN",
            "PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL",
            "PLUGIN_EXAMPLES_MERGE_PR_APPROVAL",
            "GPT_OSS_ENDPOINT",
            "GPT_OSS_API_KEY",
            "EXAMPLE_REVIEWER_PATH",
        ]
        for var in required_vars:
            assert var in content, f"Required env var '{var}' not documented in CI env docs"

    def test_ci_docs_approve_tokens_not_in_ci_secrets(self):
        """CI docs must state that approval tokens are NOT stored as CI secrets."""
        content = _CI_DOCS_PATH.read_text(encoding="utf-8")
        # Must mention that approval tokens are human-provided, not CI secrets
        assert "APPROVE_LIVE_PR" in content, "CI docs must mention APPROVE_LIVE_PR"
        assert "APPROVE_MERGE_PR" in content, "CI docs must mention APPROVE_MERGE_PR"
        # Must have some indication these are human tokens not stored in CI
        human_indicators = ["human", "operator", "interactively", "must NOT"]
        assert any(ind in content for ind in human_indicators), (
            "CI docs must indicate that approval tokens require human operator input, not CI secret storage"
        )
