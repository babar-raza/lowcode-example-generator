"""Tests for the live PR approval gate and publisher approval guards."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from plugin_examples.gates.models import GateVerdict
from plugin_examples.publisher.approval_gate import (
    APPROVAL_EXPECTED_VALUE,
    BLOCKED_INVALID_LIVE_PR_APPROVAL,
    BLOCKED_LIVE_PR_APPROVAL_REQUIRED,
    BLOCKED_PR_PERMISSION_NOT_READY,
    BLOCKED_PUBLISH_DRY_RUN_CONFLICT,
    BLOCKED_PUBLISH_TO_MAIN,
    BLOCKED_REPO_ACCESS_NOT_READY,
    check_approval,
)
from plugin_examples.publisher.publisher import publish_examples


def _make_passing_verdict() -> GateVerdict:
    return GateVerdict(
        verdict="PR_DRY_RUN_READY",
        publishable=False,
        all_required_passed=True,
        blocking_gates=[],
        gates=[],
    )


def _setup_evidence(latest: Path, family: str) -> None:
    latest.mkdir(parents=True, exist_ok=True)
    (latest / f"{family}-source-of-truth-proof.json").write_text("{}")
    (latest / "validation-results.json").write_text("{}")


def _make_family_cfg(family: str, owner: str, repo: str):
    from types import SimpleNamespace

    pub_repo = SimpleNamespace(owner=owner, repo=repo, branch="main")
    github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo, central_repo_allowed=False)
    return SimpleNamespace(status="active", github=github_cfg)


class TestLivePRApprovalGate:
    def test_live_publish_requires_approval_token(self, tmp_path):
        """publish_examples with dry_run=False and no approval token must be blocked."""
        latest = tmp_path / "verification" / "latest"
        _setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        full_cfg = _make_family_cfg("cells", "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples")

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=full_cfg,
            approval_token=None,
        )
        assert result.status == "blocked"
        assert result.blocked_reason == BLOCKED_LIVE_PR_APPROVAL_REQUIRED

    def test_live_publish_rejects_wrong_approval_token(self, tmp_path):
        """publish_examples with wrong approval token value must be blocked."""
        latest = tmp_path / "verification" / "latest"
        _setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        full_cfg = _make_family_cfg("cells", "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples")

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=full_cfg,
            approval_token="WRONG_TOKEN",
        )
        assert result.status == "blocked"
        assert result.blocked_reason == BLOCKED_INVALID_LIVE_PR_APPROVAL

    def test_live_publish_does_not_use_github_token_as_approval(self):
        """GitHub PAT values must not satisfy the approval check."""
        approved, reason = check_approval("ghp_some_github_token_value")
        assert approved is False
        assert reason == BLOCKED_INVALID_LIVE_PR_APPROVAL

        approved2, reason2 = check_approval("github_pat_some_fine_grained_token")
        assert approved2 is False
        assert reason2 == BLOCKED_INVALID_LIVE_PR_APPROVAL

    def test_live_publish_blocks_dry_run_conflict(self):
        """blocked_publish_dry_run_conflict constant is defined for CLI conflict detection."""
        assert BLOCKED_PUBLISH_DRY_RUN_CONFLICT == "blocked_publish_dry_run_conflict"

    def test_live_publish_blocks_main_branch(self, tmp_path):
        """Branch name from publish_examples is never main; BLOCKED_PUBLISH_TO_MAIN constant exists."""
        assert BLOCKED_PUBLISH_TO_MAIN == "blocked_publish_to_main"

        latest = tmp_path / "verification" / "latest"
        _setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        full_cfg = _make_family_cfg("cells", "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples")

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=full_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        # Branch format: plugin-examples/{family}/{timestamp} — never equals "main"
        assert result.branch_name is not None
        assert result.branch_name.startswith("plugin-examples/cells/")
        assert result.branch_name != "main"

    def test_live_publish_requires_validation_evidence(self, tmp_path):
        """Publisher must block when evidence files are missing."""
        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        assert result.status == "blocked"
        assert "Missing evidence" in result.blocked_reason

    def test_live_publish_requires_repo_access_ready(self, tmp_path):
        """publish_examples with dry_run=False and repo_access_ready=False must be blocked."""
        latest = tmp_path / "verification" / "latest"
        _setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        full_cfg = _make_family_cfg("cells", "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples")

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=full_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=False,
            pr_permission_ready=True,
        )
        assert result.status == "blocked"
        assert result.blocked_reason == BLOCKED_REPO_ACCESS_NOT_READY

    def test_live_publish_requires_pr_permission_ready(self, tmp_path):
        """publish_examples with dry_run=False and pr_permission_ready=False must be blocked."""
        latest = tmp_path / "verification" / "latest"
        _setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        full_cfg = _make_family_cfg("cells", "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples")

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=full_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=False,
        )
        assert result.status == "blocked"
        assert result.blocked_reason == BLOCKED_PR_PERMISSION_NOT_READY

    def test_live_publish_blocks_discovery_only_family(self):
        """discovery_only family must be blocked at publish_readiness level."""
        from types import SimpleNamespace

        from plugin_examples.publisher.publish_readiness import (
            BLOCKED_FAMILY_NOT_ACTIVE,
            check_family_publish_readiness,
        )

        cfg = SimpleNamespace(status="discovery_only", github=None)
        record = check_family_publish_readiness("pdf", cfg)
        assert record["publish_ready"] is False
        assert record["blocked_reason"] == BLOCKED_FAMILY_NOT_ACTIVE

    def test_probe_publish_permissions_does_not_push_content(self, tmp_path):
        """probe_publish_permissions must be read-only and never push content."""
        from unittest.mock import patch

        from plugin_examples.publisher.publish_permission_probe import probe_publish_permissions

        fake_body = {
            "default_branch": "main",
            "visibility": "public",
            "permissions": {"push": True, "pull": True, "admin": True},
        }

        def mock_get(url, headers):
            if "/branches/" in url:
                return 200, {}
            return 200, fake_body

        from types import SimpleNamespace

        pub_repo = SimpleNamespace(
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
            branch="main",
        )
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo, central_repo_allowed=False)
        cfg = SimpleNamespace(status="active", github=github_cfg)

        with (
            patch(
                "plugin_examples.publisher.repo_access_resolver._github_get",
                side_effect=mock_get,
            ),
            patch(
                "plugin_examples.publisher.repo_access_resolver._get_headers",
                return_value={"Authorization": "token test_token"},
            ),
        ):
            result = probe_publish_permissions(
                [("cells", cfg, "cells.yml")],
                tmp_path / "verification",
                dry_run=True,
                promote_latest=True,
            )

        assert result["probe_is_read_only"] is True
        assert result["no_content_pushed"] is True
        assert result["summary"]["live_publish_authorized"] is False
        assert result["families"][0]["pr_permission_ready"] is True
        assert result["families"][0]["safe_to_publish"] is False

    def test_monthly_runner_cannot_live_publish_without_explicit_approval(self, tmp_path):
        """Unattended runner call without approval_token must be blocked."""
        latest = tmp_path / "verification" / "latest"
        _setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        full_cfg = _make_family_cfg("cells", "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples")

        # Remove approval env var to simulate unattended run
        env_backup = os.environ.pop("PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL", None)
        try:
            result = publish_examples(
                family="cells",
                run_id="monthly-2026-05",
                examples=[{"scenario_id": "s1", "status": "generated"}],
                verification_dir=tmp_path / "verification",
                dry_run=False,
                github_token="fake-token",
                gate_verdict=verdict,
                family_config=full_cfg,
                approval_token=None,
                repo_access_ready=True,
                pr_permission_ready=True,
            )
        finally:
            if env_backup is not None:
                os.environ["PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL"] = env_backup

        assert result.status == "blocked"
        assert result.blocked_reason == BLOCKED_LIVE_PR_APPROVAL_REQUIRED
