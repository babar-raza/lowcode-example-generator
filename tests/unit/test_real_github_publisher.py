"""Tests for the real GitHub PR publisher.

All tests use mocks — no real network calls are made.
These tests verify:
  - Approval gate guards
  - Branch name safety
  - Family-specific target requirement
  - Dry-run performs no remote writes
  - Live mode calls GitHub API steps in correct order
  - Token never appears in return values
  - Stub removed: publish_examples returns blocked_real_publisher_not_implemented
    when package_path is None
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from plugin_examples.publisher.approval_gate import APPROVAL_EXPECTED_VALUE
from plugin_examples.publisher.github_pr_publisher import (
    PublishingError,
    collect_package_files,
    create_github_pr,
)
from plugin_examples.publisher.pr_builder import build_pr
from plugin_examples.publisher.publisher import PublishResult, publish_examples


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_evidence_dir(tmp_path: Path, family: str = "cells") -> Path:
    """Create minimal evidence files so _verify_evidence passes."""
    latest = tmp_path / "verification" / "latest"
    latest.mkdir(parents=True)
    (latest / f"{family}-source-of-truth-proof.json").write_text("{}")
    (latest / "validation-results.json").write_text("{}")
    (latest / "gate-results.json").write_text(
        json.dumps({"publishable": True, "all_required_passed": True, "verdict": "PR_DRY_RUN_READY"})
    )
    return tmp_path / "verification"


def _make_fake_config(
    owner: str = "aspose-cells-net",
    repo: str = "Aspose.Cells.LowCode-for-.NET-Examples",
    central_repo_allowed: bool = False,
):
    """Build a minimal family config mock."""
    pub_repo = MagicMock()
    pub_repo.owner = owner
    pub_repo.repo = repo
    pub_repo.branch = "main"

    github_cfg = MagicMock()
    github_cfg.published_plugin_examples_repo = pub_repo
    github_cfg.central_repo_allowed = central_repo_allowed

    cfg = MagicMock()
    cfg.github = github_cfg
    return cfg


def _examples():
    return [{"scenario_id": "cells-html-converter", "status": "generated"}]


# ---------------------------------------------------------------------------
# Test 1: rejects without approval token
# ---------------------------------------------------------------------------

class TestRealPublisherRejectsWithoutApproval:
    def test_real_publisher_rejects_without_approval(self, tmp_path):
        """publish_examples must return blocked_live_pr_approval_required when no token."""
        verification_dir = _make_evidence_dir(tmp_path)
        result = publish_examples(
            family="cells",
            run_id="test-run-001",
            examples=_examples(),
            verification_dir=verification_dir,
            dry_run=False,
            github_token="fake_token",
            approval_token=None,
            repo_access_ready=True,
            pr_permission_ready=True,
            family_config=_make_fake_config(),
            package_path=tmp_path / "package",
        )
        assert result.status == "blocked"
        assert result.blocked_reason == "blocked_live_pr_approval_required"


# ---------------------------------------------------------------------------
# Test 2: dry-run returns dry_run status (not published)
# ---------------------------------------------------------------------------

class TestRealPublisherDryRunStatus:
    def test_real_publisher_dry_run_returns_dry_run_status(self, tmp_path):
        """publish_examples with dry_run=True must return status='dry_run', never 'published'."""
        verification_dir = _make_evidence_dir(tmp_path)
        result = publish_examples(
            family="cells",
            run_id="test-run-002",
            examples=_examples(),
            verification_dir=verification_dir,
            dry_run=True,
            github_token="fake_token",
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
            family_config=_make_fake_config(),
        )
        assert result.status == "dry_run"
        assert result.status != "published"


# ---------------------------------------------------------------------------
# Test 3: rejects main branch
# ---------------------------------------------------------------------------

class TestRealPublisherRejectsMainBranch:
    def test_real_publisher_rejects_main_branch(self, tmp_path):
        """create_github_pr must raise PublishingError when branch_name == base_branch."""
        pkg_path = tmp_path / "package"
        pkg_path.mkdir()
        (pkg_path / "README.md").write_text("test")

        with pytest.raises(PublishingError, match="blocked_publish_to_main"):
            create_github_pr(
                owner="aspose-cells-net",
                repo="Aspose.Cells.LowCode-for-.NET-Examples",
                base_branch="main",
                branch_name="main",  # same as base
                pr_title="Test",
                pr_body="Test body",
                package_path=pkg_path,
                github_token="fake_token",
            )


# ---------------------------------------------------------------------------
# Test 4: requires family-specific target
# ---------------------------------------------------------------------------

class TestRealPublisherFamilySpecificTarget:
    def test_real_publisher_requires_family_specific_target(self, tmp_path):
        """publish_examples must block when target is a central repo."""
        verification_dir = _make_evidence_dir(tmp_path)
        central_config = _make_fake_config(
            owner="aspose",
            repo="aspose-plugins-examples-dotnet",
            central_repo_allowed=False,
        )
        result = publish_examples(
            family="cells",
            run_id="test-run-004",
            examples=_examples(),
            verification_dir=verification_dir,
            dry_run=False,
            github_token="fake_token",
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
            family_config=central_config,
            package_path=tmp_path / "package",
        )
        assert result.status == "blocked"
        assert "blocked_central_repo_target_not_allowed" in (result.blocked_reason or "")


# ---------------------------------------------------------------------------
# Test 5: requires validation evidence
# ---------------------------------------------------------------------------

class TestRealPublisherRequiresEvidence:
    def test_real_publisher_requires_validation_evidence(self, tmp_path):
        """publish_examples must block when evidence files are missing."""
        empty_verification = tmp_path / "verification"
        empty_verification.mkdir(parents=True)
        (empty_verification / "latest").mkdir()
        # Missing evidence files — no gate-results.json, no source-of-truth-proof.json

        result = publish_examples(
            family="cells",
            run_id="test-run-005",
            examples=_examples(),
            verification_dir=empty_verification,
            dry_run=False,
            github_token="fake_token",
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
            family_config=_make_fake_config(),
            package_path=tmp_path / "package",
        )
        assert result.status == "blocked"
        assert result.blocked_reason is not None
        assert "Missing evidence" in result.blocked_reason


# ---------------------------------------------------------------------------
# Test 6: branch name format
# ---------------------------------------------------------------------------

class TestRealPublisherBranchName:
    def test_real_publisher_builds_branch_name(self):
        """build_pr must generate branch name in 'plugin-examples/{family}/{run_id}' format."""
        pr_content = build_pr(
            family="cells",
            run_id="20260501-120000",
            examples_count=9,
            package_version="26.4.0",
        )
        assert pr_content.branch.startswith("plugin-examples/cells/")
        assert "20260501-120000" in pr_content.branch
        assert pr_content.branch != "main"


# ---------------------------------------------------------------------------
# Test 7: PR body contains required sections
# ---------------------------------------------------------------------------

class TestRealPublisherPRBody:
    def test_real_publisher_builds_pr_body_with_evidence(self):
        """build_pr must produce a body containing all required sections."""
        pr_content = build_pr(
            family="cells",
            run_id="20260501-120000",
            examples_count=9,
            package_version="26.4.0",
            examples_list=["html-converter", "pdf-converter"],
            excluded_scenarios=["Comparer (blocked)"],
            gate_verdict="PR_DRY_RUN_READY",
            reviewer_passed=True,
        )
        body = pr_content.body
        # Required sections
        assert "Scope" in body
        assert "Package" in body
        assert "Included Examples" in body
        assert "Excluded Scenarios" in body
        assert "Validation Summary" in body
        assert "Reviewer Result" in body
        assert "Source-of-Truth Evidence" in body
        assert "Generated By" in body
        assert "Merge Instructions" in body or "DO NOT MERGE" in body
        # Specific content
        assert "Aspose.Cells" in body
        assert "26.4.0" in body
        assert "html-converter" in body
        assert "PR_DRY_RUN_READY" in body
        # Evidence file paths
        assert "cells-source-of-truth-proof.json" in body
        assert "gate-results.json" in body


# ---------------------------------------------------------------------------
# Test 8: dry-run performs no remote writes
# ---------------------------------------------------------------------------

class TestRealPublisherDryRunNoWrites:
    def test_real_publisher_dry_run_performs_no_remote_writes(self, tmp_path):
        """publish_examples dry_run=True must not call _api_request at all."""
        verification_dir = _make_evidence_dir(tmp_path)
        with patch("plugin_examples.publisher.github_pr_publisher._api_request") as mock_api:
            result = publish_examples(
                family="cells",
                run_id="test-run-008",
                examples=_examples(),
                verification_dir=verification_dir,
                dry_run=True,
                github_token="fake_token",
                approval_token=APPROVAL_EXPECTED_VALUE,
                repo_access_ready=True,
                pr_permission_ready=True,
                family_config=_make_fake_config(),
            )
        mock_api.assert_not_called()
        assert result.status == "dry_run"


# ---------------------------------------------------------------------------
# Test 9: live mode calls API steps in correct order
# ---------------------------------------------------------------------------

class TestRealPublisherAPICallOrder:
    def test_real_publisher_live_calls_create_branch_commit_push_pr_in_order(self, tmp_path):
        """create_github_pr must call GitHub API steps in: ref→commit→blobs→tree→commit→ref→PR."""
        pkg_path = tmp_path / "package"
        pkg_path.mkdir()
        (pkg_path / "Program.cs").write_text("// test")
        (pkg_path / "README.md").write_text("# test")

        call_sequence: list[str] = []

        def mock_api(method: str, url: str, headers: dict, body=None):
            call_sequence.append(f"{method}:{url.split('/repos/')[1] if '/repos/' in url else url}")
            if "git/ref" in url and method == "GET":
                return {"object": {"sha": "base_sha_abc123"}}
            if "git/commits" in url and method == "GET":
                return {"tree": {"sha": "base_tree_sha_def456"}}
            if "git/blobs" in url:
                return {"sha": f"blob_sha_{len(call_sequence):04d}"}
            if "git/trees" in url:
                return {"sha": "new_tree_sha_789abc"}
            if "git/commits" in url and method == "POST":
                return {"sha": "new_commit_sha_xyz999"}
            if "git/refs" in url and method == "POST":
                return {"ref": f"refs/heads/plugin-examples/cells/{tmp_path.name}"}
            if "/pulls" in url:
                return {"html_url": "https://github.com/owner/repo/pull/42", "number": 42}
            if "/labels" in url:
                return []
            return {}

        with patch("plugin_examples.publisher.github_pr_publisher._api_request", side_effect=mock_api):
            result = create_github_pr(
                owner="aspose-cells-net",
                repo="Aspose.Cells.LowCode-for-.NET-Examples",
                base_branch="main",
                branch_name="plugin-examples/cells/20260501-120000",
                pr_title="Add verified Aspose.Cells LowCode examples for .NET controlled pilot",
                pr_body="Test body",
                package_path=pkg_path,
                labels=["automated"],
                github_token="fake_token",
            )

        # Verify no token in result
        assert "github_token" not in result
        assert "token" not in result

        # Verify correct return values
        assert result["pr_url"] == "https://github.com/owner/repo/pull/42"
        assert result["pr_number"] == 42
        assert result["branch_name"] == "plugin-examples/cells/20260501-120000"
        assert result["files_count"] == 2

        # Verify ordering: GET ref, GET commit, POST blobs..., POST tree, POST commit, POST ref, POST pulls
        methods = [s.split(":")[0] for s in call_sequence]
        assert methods[0] == "GET"   # get base branch ref
        assert methods[1] == "GET"   # get commit tree SHA
        # All blobs must precede the tree creation
        blob_indices = [i for i, s in enumerate(call_sequence) if "git/blobs" in s]
        tree_indices = [i for i, s in enumerate(call_sequence) if "git/trees" in s]
        commit_post_indices = [
            i for i, s in enumerate(call_sequence)
            if "git/commits" in s and s.startswith("POST")
        ]
        ref_post_indices = [i for i, s in enumerate(call_sequence) if "git/refs" in s and s.startswith("POST")]
        pr_indices = [i for i, s in enumerate(call_sequence) if "/pulls" in s]

        assert len(blob_indices) == 2, "One blob per file"
        assert len(tree_indices) == 1
        assert len(commit_post_indices) == 1
        assert len(ref_post_indices) == 1
        assert len(pr_indices) == 1

        # All blobs before tree
        assert all(b < tree_indices[0] for b in blob_indices)
        # Tree before commit
        assert tree_indices[0] < commit_post_indices[0]
        # Commit before ref creation
        assert commit_post_indices[0] < ref_post_indices[0]
        # Ref creation before PR
        assert ref_post_indices[0] < pr_indices[0]


# ---------------------------------------------------------------------------
# Test 10: token never serialized
# ---------------------------------------------------------------------------

class TestRealPublisherTokenSafety:
    def test_real_publisher_never_serializes_token(self, tmp_path):
        """create_github_pr result dict must never contain the github_token."""
        pkg_path = tmp_path / "package"
        pkg_path.mkdir()
        (pkg_path / "test.cs").write_text("// test")

        def mock_api(method, url, headers, body=None):
            if "git/ref" in url and method == "GET":
                return {"object": {"sha": "sha_base"}}
            if "git/commits" in url and method == "GET":
                return {"tree": {"sha": "sha_tree"}}
            if "git/blobs" in url:
                return {"sha": "sha_blob"}
            if "git/trees" in url:
                return {"sha": "sha_newtree"}
            if "git/commits" in url and method == "POST":
                return {"sha": "sha_commit"}
            if "git/refs" in url:
                return {}
            if "/pulls" in url:
                return {"html_url": "https://github.com/o/r/pull/1", "number": 1}
            return {}

        with patch("plugin_examples.publisher.github_pr_publisher._api_request", side_effect=mock_api):
            result = create_github_pr(
                owner="aspose-cells-net",
                repo="Aspose.Cells.LowCode-for-.NET-Examples",
                base_branch="main",
                branch_name="plugin-examples/cells/20260501-000000",
                pr_title="Test PR",
                pr_body="Test body",
                package_path=pkg_path,
                github_token="SUPER_SECRET_TOKEN_DO_NOT_LEAK",
            )

        # Token must never appear in any result field
        result_str = json.dumps(result)
        assert "SUPER_SECRET_TOKEN_DO_NOT_LEAK" not in result_str
        assert "github_token" not in result
        assert "token" not in result


# ---------------------------------------------------------------------------
# Test 11: stub removed — publish_examples blocks without package_path
# ---------------------------------------------------------------------------

class TestStubRemoved:
    def test_stub_published_status_removed(self, tmp_path):
        """publish_examples must not return status='published' when package_path is None.

        This test proves the old stub 'result.status = "published"' is removed.
        Without a package_path, live publish must return blocked_real_publisher_not_implemented.
        """
        verification_dir = _make_evidence_dir(tmp_path)
        result = publish_examples(
            family="cells",
            run_id="test-run-011",
            examples=_examples(),
            verification_dir=verification_dir,
            dry_run=False,
            github_token="fake_token",
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
            family_config=_make_fake_config(),
            package_path=None,  # explicitly None — stub must be gone
        )
        assert result.status != "published", (
            "publisher.py stub 'result.status = published' must be removed. "
            f"Got: status={result.status!r}, blocked_reason={result.blocked_reason!r}"
        )
        assert result.status == "blocked"
        assert "blocked_real_publisher_not_implemented" in (result.blocked_reason or ""), (
            f"Expected 'blocked_real_publisher_not_implemented' in blocked_reason, "
            f"got: {result.blocked_reason!r}"
        )
