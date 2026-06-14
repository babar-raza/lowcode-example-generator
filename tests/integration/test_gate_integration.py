"""Integration tests for approval gate and publication gate — TC-INTTEST-003."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from plugin_examples.gates.publication_gate import (
    check_repo_local_authority_exists,
    evaluate_publication_gate,
)
from plugin_examples.publisher.approval_gate import (
    APPROVAL_EXPECTED_VALUE,
    BLOCKED_INVALID_LIVE_PR_APPROVAL,
    BLOCKED_LIVE_PR_APPROVAL_REQUIRED,
    check_approval,
)


class TestApprovalGateIntegration:
    """Cross-module approval gate tests."""

    def test_no_token_returns_blocked(self):
        """check_approval(None) returns BLOCKED_LIVE_PR_APPROVAL_REQUIRED."""
        with patch.dict(os.environ, {}, clear=True):
            approved, reason = check_approval(None)
        assert approved is False
        assert reason == BLOCKED_LIVE_PR_APPROVAL_REQUIRED

    def test_correct_token_returns_approved(self):
        """check_approval('APPROVE_LIVE_PR') returns approved."""
        approved, reason = check_approval(APPROVAL_EXPECTED_VALUE)
        assert approved is True
        assert reason == ""

    def test_wrong_token_returns_invalid(self):
        """check_approval('wrong_token') returns BLOCKED_INVALID_LIVE_PR_APPROVAL."""
        approved, reason = check_approval("wrong_token")
        assert approved is False
        assert reason == BLOCKED_INVALID_LIVE_PR_APPROVAL

    def test_env_var_fallback(self):
        """Token read from PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL env var."""
        with patch.dict(os.environ, {"PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL": APPROVAL_EXPECTED_VALUE}):
            approved, reason = check_approval(None)
        assert approved is True

    def test_env_var_wrong_value(self):
        """Wrong env var value returns BLOCKED_INVALID."""
        with patch.dict(os.environ, {"PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL": "NOPE"}):
            approved, reason = check_approval(None)
        assert approved is False
        assert reason == BLOCKED_INVALID_LIVE_PR_APPROVAL


class TestPublicationGateIntegration:
    """Cross-module publication gate tests."""

    def test_missing_format_authority_blocks(self, tmp_path):
        """evaluate_publication_gate returns passed=False when format authority missing."""
        with patch(
            "plugin_examples.gates.publication_gate.check_repo_local_authority_exists",
            return_value=False,
        ):
            result = evaluate_publication_gate(
                scenario_id="cells-converter",
                family="cells",
                type_name="SpreadsheetConverter",
            )
        assert result.passed is False
        assert any("authority" in r.lower() for r in result.reasons)

    def test_authority_exists_check_uses_manifest(self, tmp_path):
        """check_repo_local_authority_exists returns True when manifest present."""
        manifest_dir = tmp_path / "pipeline" / "format-authority"
        manifest_dir.mkdir(parents=True)
        (manifest_dir / "manifest.json").write_text("{}", encoding="utf-8")
        with patch(
            "plugin_examples.gates.publication_gate._REPO_LOCAL_MANIFEST",
            manifest_dir / "manifest.json",
        ):
            assert check_repo_local_authority_exists() is True
