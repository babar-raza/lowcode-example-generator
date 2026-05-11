"""Tests for monthly build regression validation (B-005/B-006/B-007)."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

# Add scripts dir to path for import
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_published_examples_build import (
    FAMILY_REPO_MAP,
    FamilyBuildResult,
    MonthlyBuildReport,
    build_report,
    discover_published_families,
)


# ---------------------------------------------------------------------------
# Report building
# ---------------------------------------------------------------------------


class TestBuildReport:

    def test_all_pass_verdict(self):
        results = [
            FamilyBuildResult(family="cells", repo="r1", build_exit_code=0, verdict="PASS"),
            FamilyBuildResult(family="words", repo="r2", build_exit_code=0, verdict="PASS"),
        ]
        report = build_report(results)
        assert report.overall_verdict == "ALL_PASS"
        assert report.families_checked == 2
        assert report.families_passed == 2
        assert report.families_regressed == 0

    def test_regression_detected_verdict(self):
        results = [
            FamilyBuildResult(family="cells", repo="r1", build_exit_code=0, verdict="PASS"),
            FamilyBuildResult(family="words", repo="r2", build_exit_code=1, verdict="REGRESSED"),
        ]
        report = build_report(results)
        assert report.overall_verdict == "REGRESSION_DETECTED"
        assert report.families_regressed == 1

    def test_partial_verdict_on_clone_failure(self):
        results = [
            FamilyBuildResult(family="cells", repo="r1", verdict="CLONE_FAILED"),
        ]
        report = build_report(results)
        assert report.overall_verdict == "PARTIAL"

    def test_report_serializes_to_json(self):
        results = [
            FamilyBuildResult(family="cells", repo="r1", build_exit_code=0, verdict="PASS"),
        ]
        report = build_report(results)
        data = asdict(report)
        json_str = json.dumps(data, indent=2)
        parsed = json.loads(json_str)
        assert parsed["overall_verdict"] == "ALL_PASS"
        assert len(parsed["results"]) == 1

    def test_report_has_required_fields(self):
        results = [
            FamilyBuildResult(family="cells", repo="r1", build_exit_code=0, verdict="PASS"),
        ]
        report = build_report(results)
        data = asdict(report)
        required = [
            "generated_at", "families_checked", "families_passed",
            "families_regressed", "overall_verdict", "results",
        ]
        for field_name in required:
            assert field_name in data, f"Missing required field: {field_name}"


# ---------------------------------------------------------------------------
# Family discovery
# ---------------------------------------------------------------------------


class TestFamilyDiscovery:

    def test_discovers_families_from_merge_results(self, tmp_path):
        verification = tmp_path / "workspace" / "verification" / "latest"
        verification.mkdir(parents=True, exist_ok=True)
        merge_data = {"target_repo": "org/repo-cells", "merge_commit_sha": "abc123"}
        (verification / "cells-merge-result.json").write_text(json.dumps(merge_data))

        published = discover_published_families(tmp_path)
        assert "cells" in published
        assert published["cells"] == "org/repo-cells"

    def test_no_merge_results_returns_empty(self, tmp_path):
        published = discover_published_families(tmp_path)
        assert len(published) == 0


# ---------------------------------------------------------------------------
# Family repo map
# ---------------------------------------------------------------------------


class TestFamilyRepoMap:

    def test_map_has_all_published_families(self):
        assert "cells" in FAMILY_REPO_MAP
        assert "words" in FAMILY_REPO_MAP
        assert "pdf" in FAMILY_REPO_MAP

    def test_repos_are_non_empty_strings(self):
        for family, repo in FAMILY_REPO_MAP.items():
            assert isinstance(repo, str)
            assert len(repo) > 0
            assert "/" in repo  # org/repo format
