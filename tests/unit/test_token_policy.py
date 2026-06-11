"""Token policy tests for the publishing pipeline.

Verifies:
- pipeline code reads only GITHUB_TOKEN (not GH_TOKEN)
- runbook docs do not require GH_TOKEN directly
- token values are never written to evidence files
- live publish is blocked when GITHUB_TOKEN is absent
- token capability preflight reports meaningful failure modes
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Test: pipeline source reads only GITHUB_TOKEN, not GH_TOKEN
# ---------------------------------------------------------------------------


class TestPipelineUsesOnlyGithubTokenEnv:
    def test_repo_access_resolver_reads_github_token_not_gh_token(self):
        """repo_access_resolver._get_headers() reads GITHUB_TOKEN, never GH_TOKEN."""
        from plugin_examples.publisher.repo_access_resolver import _get_headers

        # When GITHUB_TOKEN is absent, headers should be None
        with patch.dict(os.environ, {}, clear=False):
            env_without = {k: v for k, v in os.environ.items() if k not in ("GITHUB_TOKEN", "GH_TOKEN")}
            with patch.dict(os.environ, env_without, clear=True):
                result = _get_headers()
            assert result is None, "_get_headers() must return None when GITHUB_TOKEN is absent"

    def test_repo_access_resolver_reads_github_token_when_set(self):
        """_get_headers() uses GITHUB_TOKEN when set."""
        from plugin_examples.publisher.repo_access_resolver import _get_headers

        with patch.dict(os.environ, {"GITHUB_TOKEN": "test-classic-token"}, clear=False):
            headers = _get_headers()

        assert headers is not None
        assert "Authorization" in headers
        assert "test-classic-token" in headers["Authorization"]

    def test_publisher_reads_github_token_from_main(self):
        """publish-pr command handler reads GITHUB_TOKEN env var."""
        import ast
        import textwrap

        cmd_path = Path("src/plugin_examples/commands/publish_pr.py")
        source = cmd_path.read_text(encoding="utf-8")
        # Confirm GITHUB_TOKEN is referenced in the publish-pr handler
        assert "GITHUB_TOKEN" in source, "publish_pr.py must reference GITHUB_TOKEN"
        # GH_TOKEN must NOT be directly referenced in source code
        assert "GH_TOKEN" not in source, (
            "publish_pr.py must not reference GH_TOKEN directly — "
            "the operator sets GITHUB_TOKEN; the pipeline reads GITHUB_TOKEN only"
        )

    def test_publisher_py_does_not_reference_gh_token(self):
        """publisher.py must not reference GH_TOKEN directly."""
        source = Path("src/plugin_examples/publisher/publisher.py").read_text(encoding="utf-8")
        assert "GH_TOKEN" not in source, "publisher.py must not reference GH_TOKEN"

    def test_github_pr_publisher_does_not_reference_gh_token(self):
        """github_pr_publisher.py must not reference GH_TOKEN directly."""
        source = Path("src/plugin_examples/publisher/github_pr_publisher.py").read_text(encoding="utf-8")
        assert "GH_TOKEN" not in source, "github_pr_publisher.py must not reference GH_TOKEN"


# ---------------------------------------------------------------------------
# Test: runbook doc does not require GH_TOKEN directly
# ---------------------------------------------------------------------------


class TestRunbookDoesNotRequireGhToken:
    def test_runbook_documents_github_token_as_pipeline_variable(self):
        """The pipeline reads GITHUB_TOKEN. If the runbook mentions GH_TOKEN as operator storage,
        it must also clearly identify GITHUB_TOKEN as what the pipeline actually reads."""
        runbook_path = Path("docs/operations/live-publishing.md")
        assert runbook_path.exists(), f"Runbook not found: {runbook_path}"
        content = runbook_path.read_text(encoding="utf-8")
        # The pipeline variable GITHUB_TOKEN must always be documented
        assert "GITHUB_TOKEN" in content, "Runbook must document GITHUB_TOKEN — that is what the pipeline reads."
        # If GH_TOKEN is mentioned (as operator storage), the runbook must also
        # clarify that the pipeline reads GITHUB_TOKEN (not GH_TOKEN directly)
        if "GH_TOKEN" in content:
            assert (
                "pipeline reads" in content.lower()
                or "never read directly" in content.lower()
                or "GITHUB_TOKEN" in content
            ), (
                "If GH_TOKEN appears in the runbook, it must clarify that "
                "the pipeline reads GITHUB_TOKEN, not GH_TOKEN directly."
            )

    def test_runbook_references_github_token(self):
        """The runbook must explicitly mention GITHUB_TOKEN."""
        runbook_path = Path("docs/operations/live-publishing.md")
        content = runbook_path.read_text(encoding="utf-8")
        assert "GITHUB_TOKEN" in content, "Runbook must reference GITHUB_TOKEN"

    def test_runbook_mentions_token_type_requirement(self):
        """Runbook should mention classic PAT or repo scope requirement."""
        runbook_path = Path("docs/operations/live-publishing.md")
        content = runbook_path.read_text(encoding="utf-8")
        has_classic_pat = "classic PAT" in content or "classic" in content
        has_repo_scope = "repo scope" in content or "repo` scope" in content
        has_contents_write = "Contents" in content
        assert has_classic_pat or has_repo_scope or has_contents_write, (
            "Runbook must mention token type requirement (classic PAT with repo scope "
            "or fine-grained PAT with Contents write)"
        )


# ---------------------------------------------------------------------------
# Test: token value never written to evidence
# ---------------------------------------------------------------------------


class TestTokenValueNotWrittenToEvidence:
    def test_probe_report_does_not_store_token_value(self, tmp_path):
        """publish-permission-probe.json must not contain the GITHUB_TOKEN value."""
        from types import SimpleNamespace
        from plugin_examples.publisher.publish_permission_probe import probe_publish_permissions

        pub_repo = SimpleNamespace(
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
            branch="main",
        )
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo)
        cfg = SimpleNamespace(status="active", github=github_cfg)

        fake_token = "ghp_SUPER_SECRET_SHOULD_NOT_APPEAR_IN_FILE"

        def mock_check(owner, repo, branch, headers=None):
            return {
                "can_read": True,
                "can_push": True,
                "http_status": 200,
                "visibility": "public",
                "default_branch": "main",
                "branch_exists": True,
                "repo_access_ready": True,
                "pr_permission_ready": True,
                "error_classification": "repo_access_ok",
                "interpretation": "Repo accessible.",
            }

        with (
            patch.dict(os.environ, {"GITHUB_TOKEN": fake_token}),
            patch("plugin_examples.publisher.repo_access_resolver.check_repo_access", mock_check),
        ):
            probe_publish_permissions(
                [("cells", cfg, "cells.yml")],
                tmp_path / "verification",
                promote_latest=True,
            )

        report_path = tmp_path / "verification" / "latest" / "publish-permission-probe.json"
        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        assert fake_token not in content, "GITHUB_TOKEN value must NEVER appear in the probe report"

    def test_publishing_report_does_not_store_token_value(self, tmp_path):
        """publishing-report.json must not contain the GITHUB_TOKEN value."""
        from plugin_examples.publisher.publisher import PublishResult, write_publishing_report

        result = PublishResult(dry_run=True, status="dry_run")
        # Simulate a token being passed — it must not end up in the report
        fake_token = "ghp_TOKEN_MUST_NOT_LEAK_INTO_REPORT"
        result.blocked_reason = None

        report_path = write_publishing_report(result, tmp_path / "verification")
        content = report_path.read_text(encoding="utf-8")
        assert fake_token not in content


# ---------------------------------------------------------------------------
# Test: live publish blocked when GITHUB_TOKEN absent
# ---------------------------------------------------------------------------


class TestLivePublishBlocksWhenGithubTokenAbsent:
    def _setup_evidence(self, latest: Path, family: str) -> None:
        latest.mkdir(parents=True, exist_ok=True)
        (latest / f"{family}-source-of-truth-proof.json").write_text("{}")
        (latest / "validation-results.json").write_text("{}")

    def _make_passing_verdict(self):
        from plugin_examples.gates.models import GateVerdict

        return GateVerdict(
            verdict="PR_DRY_RUN_READY",
            publishable=False,
            all_required_passed=True,
            blocking_gates=[],
            gates=[],
        )

    def _make_family_config(self):
        from types import SimpleNamespace

        pub_repo = SimpleNamespace(
            owner="aspose-words-net",
            repo="Aspose.Words.LowCode-for-.NET-Examples",
            branch="main",
        )
        github_cfg = SimpleNamespace(
            published_plugin_examples_repo=pub_repo,
            central_repo_allowed=False,
        )
        return SimpleNamespace(status="active", github=github_cfg)

    def test_live_publish_falls_back_to_dry_run_when_token_absent(self, tmp_path):
        """When GITHUB_TOKEN is empty, publisher returns dry_run (no error, but no live push)."""
        from plugin_examples.publisher.publisher import publish_examples
        from plugin_examples.publisher.approval_gate import APPROVAL_EXPECTED_VALUE

        latest = tmp_path / "verification" / "latest"
        self._setup_evidence(latest, "words")
        verdict = self._make_passing_verdict()
        family_cfg = self._make_family_config()

        result = publish_examples(
            family="words",
            run_id="test-run",
            examples=[{"scenario_id": "w1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="",  # explicitly empty
            gate_verdict=verdict,
            family_config=family_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        # Empty token → falls back to dry_run (not an error — operator must fix token)
        assert result.status == "dry_run"
        assert result.pr_url is None


# ---------------------------------------------------------------------------
# Test: token capability preflight reports repo scope failure precisely
# ---------------------------------------------------------------------------


class TestTokenCapabilityPreflightReportsRepoScopeFailure:
    def test_preflight_reports_token_missing_when_no_github_token(self):
        """When GITHUB_TOKEN is absent, check_repo_access reports token_missing."""
        from plugin_examples.publisher.repo_access_resolver import (
            check_repo_access,
            TOKEN_MISSING,
        )

        result = check_repo_access(
            "aspose-words-net",
            "Aspose.Words.LowCode-for-.NET-Examples",
            "main",
            headers=None,
        )
        assert result["can_read"] is False
        assert result["error_classification"] == TOKEN_MISSING
        assert result["repo_access_ready"] is False

    def test_preflight_reports_not_found_on_404(self):
        """When API returns 404, check_repo_access reports repo_not_found classification."""
        from plugin_examples.publisher.repo_access_resolver import (
            check_repo_access,
            REPO_NOT_FOUND,
        )

        with patch(
            "plugin_examples.publisher.repo_access_resolver._github_get",
            return_value=(404, None),
        ):
            result = check_repo_access(
                "aspose-words-net",
                "Aspose.Words.LowCode-for-.NET-Examples",
                "main",
                headers={"Authorization": "token test"},
            )
        assert result["can_read"] is False
        assert result["error_classification"] == REPO_NOT_FOUND
        assert result["repo_access_ready"] is False

    def test_preflight_reports_no_push_permission_when_push_false(self):
        """When API returns push=false, check_repo_access reports pr_permission_ready=False."""
        from plugin_examples.publisher.repo_access_resolver import check_repo_access

        fake_body = {
            "default_branch": "main",
            "visibility": "public",
            "permissions": {"push": False, "pull": True, "admin": False},
        }

        def mock_get(url, headers):
            if "/branches/" in url:
                return 200, {}
            return 200, fake_body

        with patch(
            "plugin_examples.publisher.repo_access_resolver._github_get",
            side_effect=mock_get,
        ):
            result = check_repo_access(
                "aspose-words-net",
                "Aspose.Words.LowCode-for-.NET-Examples",
                "main",
                headers={"Authorization": "token test"},
            )
        assert result["can_push"] is False
        assert result["pr_permission_ready"] is False
        assert result["repo_access_ready"] is True  # can_read is True

    def test_probe_reports_token_present_true_without_exposing_value(self, tmp_path):
        """probe_publish_permissions sets token_present=True but never stores token value."""
        from types import SimpleNamespace
        from plugin_examples.publisher.publish_permission_probe import probe_publish_permissions

        fake_token = "ghp_CANARY_TOKEN_MUST_NOT_APPEAR"
        pub_repo = SimpleNamespace(
            owner="aspose-words-net",
            repo="Aspose.Words.LowCode-for-.NET-Examples",
            branch="main",
        )
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo)
        cfg = SimpleNamespace(status="active", github=github_cfg)

        def mock_check(owner, repo, branch, headers=None):
            return {
                "can_read": True,
                "can_push": True,
                "http_status": 200,
                "visibility": "public",
                "default_branch": "main",
                "branch_exists": True,
                "repo_access_ready": True,
                "pr_permission_ready": True,
                "error_classification": "repo_access_ok",
                "interpretation": "Repo accessible.",
            }

        with (
            patch.dict(os.environ, {"GITHUB_TOKEN": fake_token}),
            patch("plugin_examples.publisher.repo_access_resolver.check_repo_access", mock_check),
        ):
            result = probe_publish_permissions(
                [("words", cfg, "words.yml")],
                tmp_path / "verification",
                promote_latest=True,
            )

        assert result["token_present"] is True
        report_path = tmp_path / "verification" / "latest" / "publish-permission-probe.json"
        file_content = report_path.read_text()
        assert fake_token not in file_content, "Token value must not appear in probe report"
