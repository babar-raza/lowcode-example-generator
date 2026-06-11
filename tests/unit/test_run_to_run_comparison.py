"""Tests for run-to-run comparison (REM-016 / B-002 / B-014)."""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from dataclasses import asdict
from pathlib import Path

import pytest

from plugin_examples.gates.example_lifecycle import (
    STATE_STRENGTH,
    ExampleLifecycleRecord,
    ExampleLifecycleRegistry,
    RunToRunComparisonResult,
    ScenarioComparisonResult,
    _state_strength,
    compare_with_prior_run,
    write_comparison_evidence,
)


# ---------------------------------------------------------------------------
# STATE_STRENGTH ordering
# ---------------------------------------------------------------------------


class TestStateStrengthOrdering:
    """Verify that the state strength ordering is complete and monotonic."""

    def test_ordering_covers_all_lifecycle_stages(self):
        from plugin_examples.gates.example_lifecycle import LIFECYCLE_STAGES

        for stage in LIFECYCLE_STAGES:
            assert stage in STATE_STRENGTH, f"Stage '{stage}' missing from STATE_STRENGTH"

    def test_ordering_is_monotonic_for_success_path(self):
        success_path = [
            "planned",
            "generation_attempted",
            "generated",
            "build_attempted",
            "build_passed",
            "run_attempted",
            "run_passed",
            "reviewer_attempted",
            "reviewer_passed",
            "pr_candidate",
        ]
        strengths = [_state_strength(s) for s in success_path]
        for i in range(1, len(strengths)):
            assert strengths[i] > strengths[i - 1], (
                f"Non-monotonic: {success_path[i-1]}({strengths[i-1]}) >= " f"{success_path[i]}({strengths[i]})"
            )

    def test_failure_states_weaker_than_pass_states(self):
        assert _state_strength("generation_failed") < _state_strength("generated")
        assert _state_strength("build_failed") < _state_strength("build_passed")
        assert _state_strength("run_failed") < _state_strength("run_passed")
        assert _state_strength("reviewer_failed") < _state_strength("reviewer_passed")

    def test_excluded_and_backlogged_are_weakest(self):
        assert _state_strength("excluded") < _state_strength("planned")
        assert _state_strength("backlogged") < _state_strength("planned")

    def test_unknown_stage_returns_negative(self):
        assert _state_strength("nonexistent_stage") == -1


# ---------------------------------------------------------------------------
# Lifecycle record backward compatibility
# ---------------------------------------------------------------------------


class TestLifecycleBackwardCompatibility:
    """Ensure old lifecycle records without comparison fields load correctly."""

    def test_old_record_loads_without_new_fields(self):
        old_data = {
            "scenario_id": "cells-Converter",
            "family": "cells",
            "run_id": "old-run-001",
            "current_stage": "pr_candidate",
            "final_verdict": "EXAMPLE_READY_FOR_PR_DRY_RUN",
        }
        # Simulate loading old JSON: create record and verify defaults
        record = ExampleLifecycleRecord(
            scenario_id=old_data["scenario_id"],
            family=old_data["family"],
            run_id=old_data["run_id"],
        )
        assert record.prior_run_id is None
        assert record.prior_state is None
        assert record.prior_run_result is None
        assert record.regression_detected is False
        assert record.regression_reason is None

    def test_new_fields_serialize_correctly(self):
        record = ExampleLifecycleRecord(
            scenario_id="test-scenario",
            family="cells",
            run_id="run-001",
            prior_run_id="run-000",
            prior_state="build_passed",
            prior_run_result="IMPROVED",
            regression_detected=False,
        )
        d = asdict(record)
        assert d["prior_run_id"] == "run-000"
        assert d["prior_state"] == "build_passed"
        assert d["prior_run_result"] == "IMPROVED"
        assert d["regression_detected"] is False
        assert d["regression_reason"] is None

    def test_regression_fields_serialize(self):
        record = ExampleLifecycleRecord(
            scenario_id="test-scenario",
            family="cells",
            run_id="run-002",
            prior_run_id="run-001",
            prior_state="reviewer_passed",
            prior_run_result="REGRESSED",
            regression_detected=True,
            regression_reason="State weakened: reviewer_passed -> build_failed",
        )
        d = asdict(record)
        assert d["regression_detected"] is True
        assert "weakened" in d["regression_reason"]


# ---------------------------------------------------------------------------
# Comparison logic
# ---------------------------------------------------------------------------


def _make_registry(family: str, run_id: str, scenarios: list[tuple[str, str]]) -> ExampleLifecycleRegistry:
    """Helper: create a registry with scenarios at given stages."""
    reg = ExampleLifecycleRegistry(family=family, run_id=run_id)
    for scenario_id, stage in scenarios:
        rec = reg.create_record(scenario_id)
        rec.current_stage = stage
    return reg


def _write_prior_lifecycle(repo_root: Path, run_id: str, family: str, scenarios: list[tuple[str, str]]) -> None:
    """Helper: write a prior lifecycle record file."""
    records = []
    for scenario_id, stage in scenarios:
        records.append(
            {
                "scenario_id": scenario_id,
                "family": family,
                "run_id": run_id,
                "current_stage": stage,
                "final_verdict": "PENDING",
            }
        )
    path = repo_root / "workspace" / "runs" / run_id / "evidence" / "latest" / "example-lifecycle-records.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "family": family,
        "run_id": run_id,
        "summary": {},
        "records": records,
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class TestComparisonLogic:
    def test_no_regression_when_same_state(self, tmp_path):
        prior_scenarios = [("s1", "reviewer_passed"), ("s2", "pr_candidate")]
        current_scenarios = [("s1", "reviewer_passed"), ("s2", "pr_candidate")]
        _write_prior_lifecycle(tmp_path, "prior-run", "cells", prior_scenarios)
        registry = _make_registry("cells", "current-run", current_scenarios)

        result = compare_with_prior_run(registry, "prior-run", tmp_path)

        assert result.regression_detected is False
        assert result.unchanged_count == 2
        assert result.regressed_count == 0
        assert result.verdict == "RUN_TO_RUN_COMPARISON_PASS"

    def test_no_regression_when_improved(self, tmp_path):
        prior_scenarios = [("s1", "build_passed"), ("s2", "generated")]
        current_scenarios = [("s1", "reviewer_passed"), ("s2", "run_passed")]
        _write_prior_lifecycle(tmp_path, "prior-run", "cells", prior_scenarios)
        registry = _make_registry("cells", "current-run", current_scenarios)

        result = compare_with_prior_run(registry, "prior-run", tmp_path)

        assert result.regression_detected is False
        assert result.improved_count == 2
        assert result.verdict == "RUN_TO_RUN_COMPARISON_PASS_WITH_IMPROVEMENTS"

    def test_regression_detected_when_weaker_state(self, tmp_path):
        prior_scenarios = [("s1", "reviewer_passed"), ("s2", "run_passed")]
        current_scenarios = [("s1", "build_failed"), ("s2", "run_passed")]
        _write_prior_lifecycle(tmp_path, "prior-run", "cells", prior_scenarios)
        registry = _make_registry("cells", "current-run", current_scenarios)

        result = compare_with_prior_run(registry, "prior-run", tmp_path)

        assert result.regression_detected is True
        assert result.regressed_count == 1
        assert result.verdict == "RUN_TO_RUN_COMPARISON_REGRESSION_DETECTED"
        # Verify the record itself is marked
        rec = registry.get_record("s1")
        assert rec.regression_detected is True
        assert rec.prior_state == "reviewer_passed"
        assert rec.prior_run_result == "REGRESSED"

    def test_regression_on_missing_scenario(self, tmp_path):
        prior_scenarios = [("s1", "reviewer_passed"), ("s2", "pr_candidate")]
        current_scenarios = [("s1", "reviewer_passed")]  # s2 is missing
        _write_prior_lifecycle(tmp_path, "prior-run", "cells", prior_scenarios)
        registry = _make_registry("cells", "current-run", current_scenarios)

        result = compare_with_prior_run(registry, "prior-run", tmp_path)

        assert result.regression_detected is True
        assert result.missing_from_current_count == 1
        # s2 was at pr_candidate (strong) and is now missing — regression
        missing = [r for r in result.per_scenario_results if r["classification"] == "MISSING_FROM_CURRENT"]
        assert len(missing) == 1
        assert missing[0]["scenario_id"] == "s2"

    def test_missing_planned_scenario_is_not_regression(self, tmp_path):
        """A scenario at 'planned' stage missing from current is not a regression."""
        prior_scenarios = [("s1", "reviewer_passed"), ("s2", "planned")]
        current_scenarios = [("s1", "reviewer_passed")]
        _write_prior_lifecycle(tmp_path, "prior-run", "cells", prior_scenarios)
        registry = _make_registry("cells", "current-run", current_scenarios)

        result = compare_with_prior_run(registry, "prior-run", tmp_path)

        assert result.regression_detected is False
        assert result.missing_from_current_count == 1
        assert result.regressed_count == 0

    def test_new_scenario_is_not_regression(self, tmp_path):
        prior_scenarios = [("s1", "reviewer_passed")]
        current_scenarios = [("s1", "reviewer_passed"), ("s2", "generated")]
        _write_prior_lifecycle(tmp_path, "prior-run", "cells", prior_scenarios)
        registry = _make_registry("cells", "current-run", current_scenarios)

        result = compare_with_prior_run(registry, "prior-run", tmp_path)

        assert result.regression_detected is False
        assert result.new_scenario_count == 1
        rec = registry.get_record("s2")
        assert rec.prior_run_result == "NEW_SCENARIO"

    def test_blocked_verdict_when_prior_not_found(self, tmp_path):
        registry = _make_registry("cells", "current-run", [("s1", "reviewer_passed")])

        result = compare_with_prior_run(registry, "nonexistent-run", tmp_path)

        assert result.verdict == "RUN_TO_RUN_COMPARISON_BLOCKED_PRIOR_RUN_NOT_FOUND"
        assert result.regression_detected is False

    def test_mixed_results(self, tmp_path):
        prior_scenarios = [
            ("s1", "pr_candidate"),  # will stay same
            ("s2", "build_passed"),  # will improve
            ("s3", "reviewer_passed"),  # will regress
        ]
        current_scenarios = [
            ("s1", "pr_candidate"),
            ("s2", "reviewer_passed"),
            ("s3", "generation_failed"),
        ]
        _write_prior_lifecycle(tmp_path, "prior-run", "cells", prior_scenarios)
        registry = _make_registry("cells", "current-run", current_scenarios)

        result = compare_with_prior_run(registry, "prior-run", tmp_path)

        assert result.unchanged_count == 1
        assert result.improved_count == 1
        assert result.regressed_count == 1
        assert result.regression_detected is True
        assert result.verdict == "RUN_TO_RUN_COMPARISON_REGRESSION_DETECTED"


# ---------------------------------------------------------------------------
# Comparison evidence writer
# ---------------------------------------------------------------------------


class TestComparisonEvidenceWriter:
    def test_comparison_artifact_has_required_fields(self, tmp_path):
        result = RunToRunComparisonResult(
            current_run_id="run-002",
            prior_run_id="run-001",
            family="cells",
            verdict="RUN_TO_RUN_COMPARISON_PASS",
        )
        path = write_comparison_evidence(result, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        required = [
            "current_run_id",
            "prior_run_id",
            "family",
            "generated_at",
            "total_prior_scenarios",
            "total_current_scenarios",
            "unchanged_count",
            "improved_count",
            "regressed_count",
            "missing_from_current_count",
            "new_scenario_count",
            "regression_detected",
            "per_scenario_results",
            "verdict",
        ]
        for field in required:
            assert field in data, f"Missing required field: {field}"


# ---------------------------------------------------------------------------
# CLI flag acceptance
# ---------------------------------------------------------------------------


class TestCLICompareRun:
    def test_cli_accepts_compare_run_flag(self):
        """Verify --compare-run is accepted by the parser (no error on parse)."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "plugin_examples",
                "run",
                "--family",
                "cells",
                "--compare-run",
                "some-prior-run",
                "--help",
            ],
            capture_output=True,
            text=True,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(Path(__file__).resolve().parents[2]),
        )
        # --help exits with 0; if --compare-run is unknown, parser errors with rc=2
        assert result.returncode == 0, f"Parser rejected --compare-run: {result.stderr}"

    def test_cli_help_mentions_compare_run(self):
        result = subprocess.run(
            [sys.executable, "-m", "plugin_examples", "run", "--help"],
            capture_output=True,
            text=True,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(Path(__file__).resolve().parents[2]),
        )
        assert "--compare-run" in result.stdout


# ---------------------------------------------------------------------------
# Promoted family evidence fallback (--compare-run latest)
# ---------------------------------------------------------------------------


class TestPromotedEvidenceFallback:
    def test_compare_run_latest_uses_promoted_evidence(self, tmp_path):
        """When prior_run_id='latest', use promoted family evidence."""
        # Write promoted evidence
        family_dir = tmp_path / "workspace" / "verification" / "latest" / "families" / "cells"
        family_dir.mkdir(parents=True, exist_ok=True)
        records = [
            {
                "scenario_id": "s1",
                "family": "cells",
                "run_id": "latest",
                "current_stage": "reviewer_passed",
                "final_verdict": "PENDING",
            },
        ]
        data = {"family": "cells", "run_id": "latest", "summary": {}, "records": records}
        (family_dir / "example-lifecycle-records.json").write_text(json.dumps(data))

        registry = _make_registry("cells", "current-run", [("s1", "reviewer_passed")])
        result = compare_with_prior_run(registry, "latest", tmp_path)

        assert result.verdict == "RUN_TO_RUN_COMPARISON_PASS"
        assert result.unchanged_count == 1
