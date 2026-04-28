"""Unit tests for publisher, package_watcher, and __main__."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.publisher.publisher import (
    PublishResult,
    publish_examples,
    write_publishing_report,
)
from plugin_examples.publisher.pr_builder import build_pr
from plugin_examples.package_watcher.watcher import (
    check_for_updates,
    write_monthly_report,
)


# --- Tests: publisher ---


class TestPublisher:
    def test_dry_run_publishes(self, tmp_path):
        # Set up required evidence
        latest = tmp_path / "workspace" / "verification" / "latest"
        latest.mkdir(parents=True)
        (latest / "cells-source-of-truth-proof.json").write_text("{}")
        (latest / "validation-results.json").write_text("{}")

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "workspace" / "verification",
            dry_run=True,
        )
        assert result.status == "dry_run"
        assert result.evidence_verified
        assert len(result.files_included) == 1

    def test_blocked_missing_evidence(self, tmp_path):
        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "workspace" / "verification",
        )
        assert result.status == "blocked"
        assert "Missing evidence" in result.blocked_reason

    def test_blocked_no_passing_examples(self, tmp_path):
        latest = tmp_path / "workspace" / "verification" / "latest"
        latest.mkdir(parents=True)
        (latest / "cells-source-of-truth-proof.json").write_text("{}")
        (latest / "validation-results.json").write_text("{}")

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "failed"}],
            verification_dir=tmp_path / "workspace" / "verification",
        )
        assert result.status == "blocked"

    def test_never_pushes_to_main(self, tmp_path):
        latest = tmp_path / "workspace" / "verification" / "latest"
        latest.mkdir(parents=True)
        (latest / "cells-source-of-truth-proof.json").write_text("{}")
        (latest / "validation-results.json").write_text("{}")

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "workspace" / "verification",
            dry_run=False,
        )
        # Without token, falls back to dry-run
        assert result.branch_name == "pipeline/test-run/cells"
        assert result.branch_name != "main"

    def test_write_publishing_report(self, tmp_path):
        result = PublishResult(dry_run=True, status="dry_run")
        path = write_publishing_report(result, tmp_path / "workspace" / "verification")
        assert path.exists()
        assert "publishing-report" in path.name


# --- Tests: pr_builder ---


class TestPRBuilder:
    def test_builds_pr_content(self):
        pr = build_pr(
            family="cells",
            run_id="run-123",
            examples_count=5,
            package_version="25.4.0",
        )
        assert "cells" in pr.title
        assert "5" in pr.title
        assert pr.branch == "pipeline/run-123/cells"
        assert "cells" in pr.labels


# --- Tests: package_watcher ---


class TestPackageWatcher:
    def test_disabled_family_skipped(self, tmp_path):
        families = [{"family": "words", "enabled": False, "status": "disabled",
                      "nuget": {"package_id": "Aspose.Words"}}]
        results = check_for_updates(families, tmp_path)
        assert len(results) == 1
        assert results[0].skipped
        assert results[0].skip_reason == "Family is disabled"

    def test_enabled_family_checked(self, tmp_path):
        families = [{"family": "cells", "enabled": True, "status": "active",
                      "nuget": {"package_id": "Aspose.Cells"}}]
        results = check_for_updates(families, tmp_path)
        assert len(results) == 1
        assert not results[0].skipped

    def test_write_monthly_report(self, tmp_path):
        from plugin_examples.package_watcher.watcher import UpdateCheck
        results = [UpdateCheck(family="cells", package_id="Aspose.Cells",
                               current_version="25.3.0", latest_version="25.4.0",
                               has_update=True)]
        path = write_monthly_report(results, tmp_path / "workspace" / "verification")
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data["updates_found"] == 1

    def test_paths_use_workspace(self, tmp_path):
        result = PublishResult(dry_run=True)
        path = write_publishing_report(result, tmp_path / "workspace" / "verification")
        assert "workspace" in str(path)
