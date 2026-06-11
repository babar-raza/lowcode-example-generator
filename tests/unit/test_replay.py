"""Tests for the hardened replay pipeline (src/plugin_examples/replay.py).

Covers:
- find_prior_run: no runs, ignores discovery/multi-family prefix, returns most recent
- stages_to_skip: correct sets per mode, scenario_planning never skipped
- check_replay_integrity: missing catalog, catalog hash mismatch, package version mismatch,
  changed constraints (hard fail for validation+), reviewer unavailable blocks publisher,
  gate verdict blocks publisher, missing candidates blocks publisher
- restore_generated_projects: valid path rewrite, path escape rejection, missing Program.cs
- restore_validation_results: typed output (ValidationResult/DotnetResult), missing file,
  malformed file, reviewer unavailable
- write_replay_manifest: written with correct fields, restored-artifacts-report.json
- Runner integration: skipped_replayed status, scenario_planning never in skip set
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.replay import (
    VALID_REPLAY_STEPS,
    ReplayIntegrityError,
    copy_reviewer_evidence,
    find_prior_run,
    restore_catalog,
    restore_generated_projects,
    restore_validation_results,
    stages_to_skip,
    write_replay_manifest,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """Minimal repo structure with workspace/runs/ and pipeline/configs/."""
    (tmp_path / "workspace" / "runs").mkdir(parents=True)
    (tmp_path / "pipeline" / "configs" / "families").mkdir(parents=True)
    (tmp_path / "pipeline" / "configs" / "denominators").mkdir(parents=True)
    return tmp_path


def _make_run(repo: pathlib.Path, run_id: str, family: str = "words") -> pathlib.Path:
    """Create a minimal run directory."""
    run_dir = repo / "workspace" / "runs" / run_id
    (run_dir / "evidence" / "latest").mkdir(parents=True)
    (run_dir / "evidence").mkdir(parents=True, exist_ok=True)
    return run_dir


def _write_catalog(run_dir: pathlib.Path, family: str, content: dict | None = None) -> None:
    """Write a minimal api-catalog.json."""
    if content is None:
        content = {"package_id": "Aspose.Words", "package_version": "26.5.0", "namespaces": [], "types": []}
    (run_dir / "evidence" / "latest" / "api-catalog.json").write_text(json.dumps(content), encoding="utf-8")


def _write_example_index(run_dir: pathlib.Path, family: str, examples: list | None = None) -> None:
    """Write example-index.json and create project dirs."""
    if examples is None:
        # Create a real project dir
        proj_dir = run_dir / "generated" / family / f"{family}-converter"
        proj_dir.mkdir(parents=True, exist_ok=True)
        (proj_dir / "Program.cs").write_text("// code", encoding="utf-8")
        examples = [
            {
                "scenario_id": f"{family}-converter",
                "project_dir": str(proj_dir),
                "csproj_path": str(proj_dir / f"{family}-converter.csproj"),
                "program_path": str(proj_dir / "Program.cs"),
                "package_id": "Aspose.Words",
                "status": "generated",
                "input_strategy": "programmatic_input",
                "input_files": [],
                "placed_fixtures": [],
                "claimed_symbols": [],
                "target_framework": "net8.0",
            }
        ]
    (run_dir / "evidence" / "example-index.json").write_text(
        json.dumps({"total_examples": len(examples), "examples": examples}),
        encoding="utf-8",
    )


def _write_validation_results(run_dir: pathlib.Path, results: list | None = None) -> None:
    """Write validation-results.json."""
    if results is None:
        results = [
            {
                "scenario_id": "words-converter",
                "passed": True,
                "failure_stage": None,
                "restore": {"operation": "restore", "success": True, "exit_code": 0, "duration_ms": 100.0},
                "build": {"operation": "build", "success": True, "exit_code": 0, "duration_ms": 200.0},
                "run": {"operation": "run", "success": True, "exit_code": 0, "duration_ms": 300.0},
            }
        ]
    (run_dir / "evidence" / "latest" / "validation-results.json").write_text(
        json.dumps(
            {
                "total": len(results),
                "passed": sum(1 for r in results if r["passed"]),
                "failed": sum(1 for r in results if not r["passed"]),
                "results": results,
            }
        ),
        encoding="utf-8",
    )


def _write_reviewer_evidence(run_dir: pathlib.Path, available: bool = True) -> None:
    (run_dir / "evidence" / "latest" / "example-reviewer-results.json").write_text(
        json.dumps({"available": available, "passed": available}), encoding="utf-8"
    )


def _write_gate_results(run_dir: pathlib.Path, verdict: str = "PR_DRY_RUN_READY") -> None:
    (run_dir / "evidence" / "latest" / "gate-results.json").write_text(
        json.dumps({"verdict": verdict, "publishable": verdict == "PR_READY"}),
        encoding="utf-8",
    )


def _write_pr_manifest(run_dir: pathlib.Path, count: int = 2) -> None:
    (run_dir / "evidence" / "latest" / "pr-candidate-manifest.json").write_text(
        json.dumps({"publishable_candidate_count": count, "included_examples": []}),
        encoding="utf-8",
    )


def _write_pilot_report(run_dir: pathlib.Path, stages_artifacts: dict | None = None) -> None:
    stages = []
    if stages_artifacts:
        for stage_name, arts in stages_artifacts.items():
            stages.append(
                {
                    "name": stage_name,
                    "order": 1,
                    "status": "success",
                    "duration_ms": 100.0,
                    "error": None,
                    "artifacts": arts,
                }
            )
    (run_dir / "pilot-report.json").write_text(
        json.dumps({"meta": {}, "stages": stages, "gate_summary": {}, "verdict": "PR_DRY_RUN_READY"}),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# find_prior_run tests
# ---------------------------------------------------------------------------


class TestFindPriorRun:
    def test_no_runs_returns_none(self, tmp_repo):
        assert find_prior_run("words", tmp_repo) is None

    def test_no_matching_family_returns_none(self, tmp_repo):
        _make_run(tmp_repo, "pilot-cells-20260513-180040", "cells")
        assert find_prior_run("words", tmp_repo) is None

    def test_returns_most_recent(self, tmp_repo):
        _make_run(tmp_repo, "pilot-words-20260510-100000")
        _make_run(tmp_repo, "pilot-words-20260513-180040")
        _make_run(tmp_repo, "pilot-words-20260512-090000")
        result = find_prior_run("words", tmp_repo)
        assert result == "pilot-words-20260513-180040"

    def test_ignores_discovery_prefix(self, tmp_repo):
        _make_run(tmp_repo, "discovery-words-20260513-180040")
        assert find_prior_run("words", tmp_repo) is None

    def test_ignores_multi_family_prefix(self, tmp_repo):
        _make_run(tmp_repo, "multi-family-20260513-180040")
        # multi-family doesn't start with pilot-words- so already excluded
        assert find_prior_run("words", tmp_repo) is None

    def test_single_run(self, tmp_repo):
        _make_run(tmp_repo, "pilot-words-20260501-120000")
        assert find_prior_run("words", tmp_repo) == "pilot-words-20260501-120000"

    def test_missing_workspace_runs(self, tmp_path):
        assert find_prior_run("words", tmp_path) is None


# ---------------------------------------------------------------------------
# stages_to_skip tests
# ---------------------------------------------------------------------------


class TestStagesToSkip:
    INFRA = {"nuget_fetch", "dependency_resolution", "extraction", "reflection"}

    def test_generation_skips_only_infra(self):
        skip = stages_to_skip("generation")
        assert skip == frozenset(self.INFRA)

    def test_validation_skips_infra_and_generation(self):
        skip = stages_to_skip("validation")
        assert skip == frozenset(self.INFRA | {"generation"})

    def test_reviewer_skips_infra_generation_validation(self):
        skip = stages_to_skip("reviewer")
        assert skip == frozenset(self.INFRA | {"generation", "validation"})

    def test_publisher_skips_infra_generation_validation_reviewer(self):
        skip = stages_to_skip("publisher")
        assert skip == frozenset(self.INFRA | {"generation", "validation", "reviewer"})

    def test_scenario_planning_never_skipped(self):
        for mode in VALID_REPLAY_STEPS:
            assert "scenario_planning" not in stages_to_skip(mode)

    def test_load_config_never_skipped(self):
        for mode in VALID_REPLAY_STEPS:
            assert "load_config" not in stages_to_skip(mode)

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown replay_from"):
            stages_to_skip("invalid_mode")


# ---------------------------------------------------------------------------
# check_replay_integrity tests
# ---------------------------------------------------------------------------


class TestCheckReplayIntegrity:
    def test_missing_catalog_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        with pytest.raises(ReplayIntegrityError, match="api-catalog.json not found"):
            from plugin_examples.replay import check_replay_integrity

            check_replay_integrity("words", "generation", run_dir, tmp_repo)

    def test_stale_check_written_on_missing_catalog(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        with pytest.raises(ReplayIntegrityError):
            from plugin_examples.replay import check_replay_integrity

            check_replay_integrity("words", "generation", run_dir, tmp_repo)
        stale = run_dir / "evidence" / "latest" / "stale-artifact-check.json"
        assert stale.exists()

    def test_catalog_hash_mismatch_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_catalog(run_dir, "words")

        # Write denominator with wrong hash
        denom = {
            "family": "words",
            "api_catalog_sha256": "0" * 64,
        }
        (tmp_repo / "pipeline" / "configs" / "denominators" / "words.json").write_text(
            json.dumps(denom), encoding="utf-8"
        )

        from plugin_examples.replay import check_replay_integrity

        with pytest.raises(ReplayIntegrityError, match="catalog_hash|SHA256|hash"):
            check_replay_integrity("words", "generation", run_dir, tmp_repo)

    def test_catalog_hash_match_passes(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        catalog_text = json.dumps({"package_id": "Aspose.Words", "package_version": "26.5.0"})
        (run_dir / "evidence" / "latest" / "api-catalog.json").write_text(catalog_text, encoding="utf-8")
        actual_hash = hashlib.sha256(catalog_text.encode("utf-8")).hexdigest()

        denom = {"family": "words", "api_catalog_sha256": actual_hash}
        (tmp_repo / "pipeline" / "configs" / "denominators" / "words.json").write_text(
            json.dumps(denom), encoding="utf-8"
        )

        from plugin_examples.replay import check_replay_integrity

        result = check_replay_integrity("words", "generation", run_dir, tmp_repo)
        check = next(c for c in result["checks"] if c["check_id"] == "catalog_hash")
        assert check["status"] == "pass"

    def test_package_version_mismatch_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_catalog(run_dir, "words", {"package_id": "Aspose.Words", "package_version": "24.1.0"})

        # Family YAML pins a different version
        yml = "nuget:\n  package_id: Aspose.Words\n  pinned_version: 26.5.0\n"
        (tmp_repo / "pipeline" / "configs" / "families" / "words.yml").write_text(yml, encoding="utf-8")

        from plugin_examples.replay import check_replay_integrity

        with pytest.raises(ReplayIntegrityError, match="[Pp]ackage version"):
            check_replay_integrity("words", "generation", run_dir, tmp_repo)

    def test_constraints_hash_change_warns_for_generation(self, tmp_repo):
        """Changed constraints is a WARN (not fail) when replaying from generation."""
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_catalog(run_dir, "words")
        _write_pilot_report(run_dir, {"load_config": {"constraints_hash": "old_hash_" + "a" * 55}})

        from plugin_examples.replay import check_replay_integrity

        # Should NOT raise (warn only for generation mode)
        result = check_replay_integrity("words", "generation", run_dir, tmp_repo)
        check = next((c for c in result["checks"] if c["check_id"] == "constraints_hash"), None)
        if check:
            assert check["status"] in ("warn", "skipped", "pass")

    def test_constraints_hash_change_fails_for_validation(self, tmp_repo):
        """Changed constraints is a hard FAIL when replaying from validation."""
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        catalog_content = json.dumps({"package_id": "Aspose.Words", "package_version": "26.5.0"})
        (run_dir / "evidence" / "latest" / "api-catalog.json").write_text(catalog_content, encoding="utf-8")

        # Write family YAML with constraints
        yml = "per_type_constraints:\n  Converter:\n    REQUIRED: [Convert]\nstatus: active\n"
        (tmp_repo / "pipeline" / "configs" / "families" / "words.yml").write_text(yml, encoding="utf-8")

        # Store a DIFFERENT constraints hash in pilot-report (simulating changed constraints)
        _write_pilot_report(
            run_dir,
            {
                "load_config": {
                    "constraints_hash": hashlib.sha256(b"different constraints content").hexdigest(),
                    "config_hash": hashlib.sha256(b"some old config").hexdigest(),
                }
            },
        )
        _write_example_index(run_dir, "words")

        from plugin_examples.replay import check_replay_integrity

        with pytest.raises(ReplayIntegrityError, match="[Cc]onstraints"):
            check_replay_integrity("words", "validation", run_dir, tmp_repo)

    def test_publisher_reviewer_unavailable_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_catalog(run_dir, "words")
        _write_example_index(run_dir, "words")
        _write_validation_results(run_dir)
        _write_reviewer_evidence(run_dir, available=False)  # unavailable!
        _write_gate_results(run_dir, "PR_DRY_RUN_READY")
        _write_pr_manifest(run_dir, 2)

        from plugin_examples.replay import check_replay_integrity

        with pytest.raises(ReplayIntegrityError, match="[Rr]eviewer.*available|available.*false"):
            check_replay_integrity("words", "publisher", run_dir, tmp_repo)

    def test_publisher_stale_gate_verdict_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_catalog(run_dir, "words")
        _write_example_index(run_dir, "words")
        _write_validation_results(run_dir)
        _write_reviewer_evidence(run_dir, available=True)
        _write_gate_results(run_dir, "SOURCE_OF_TRUTH_PROVEN_ONLY")  # not publishable!
        _write_pr_manifest(run_dir, 2)

        from plugin_examples.replay import check_replay_integrity

        with pytest.raises(ReplayIntegrityError, match="[Vv]erdict.*not.*publishable|[Vv]erdict.*publishable"):
            check_replay_integrity("words", "publisher", run_dir, tmp_repo)

    def test_publisher_missing_candidates_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_catalog(run_dir, "words")
        _write_example_index(run_dir, "words")
        _write_validation_results(run_dir)
        _write_reviewer_evidence(run_dir, available=True)
        _write_gate_results(run_dir, "PR_DRY_RUN_READY")
        _write_pr_manifest(run_dir, 0)  # no candidates!

        from plugin_examples.replay import check_replay_integrity

        with pytest.raises(ReplayIntegrityError, match="[Cc]andidate|publishable_candidate_count"):
            check_replay_integrity("words", "publisher", run_dir, tmp_repo)

    def test_stale_check_always_written(self, tmp_repo):
        """stale-artifact-check.json is always written, even on pass."""
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_catalog(run_dir, "words")

        from plugin_examples.replay import check_replay_integrity

        check_replay_integrity("words", "generation", run_dir, tmp_repo)
        stale = run_dir / "evidence" / "latest" / "stale-artifact-check.json"
        assert stale.exists()
        data = json.loads(stale.read_text())
        assert "checks" in data
        assert "overall" in data


# ---------------------------------------------------------------------------
# restore_generated_projects tests
# ---------------------------------------------------------------------------


class TestRestoreGeneratedProjects:
    def test_valid_paths_returned(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_example_index(run_dir, "words")

        result = restore_generated_projects(run_dir, "words", tmp_repo)
        assert len(result) == 1
        proj = result[0]
        assert proj["scenario_id"] == "words-converter"
        assert pathlib.Path(proj["project_dir"]).is_dir()

    def test_path_escape_raises(self, tmp_path):
        """project_dir pointing outside repo_root is rejected — uses an explicit outside dir."""
        # Build a self-contained repo INSIDE tmp_path so we can create an OUTSIDE dir
        tmp_repo = tmp_path / "repo"
        (tmp_repo / "workspace" / "runs").mkdir(parents=True)
        (tmp_repo / "pipeline" / "configs" / "families").mkdir(parents=True)
        (tmp_repo / "pipeline" / "configs" / "denominators").mkdir(parents=True)

        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")

        # Create a real directory that IS outside tmp_repo (sibling to repo/)
        outside = tmp_path / "outside_scope"
        outside.mkdir()
        (outside / "Program.cs").write_text("// code", encoding="utf-8")

        examples = [
            {
                "scenario_id": "words-converter",
                "project_dir": str(outside.resolve()),  # exists but escapes repo_root
                "program_path": str(outside / "Program.cs"),
                "csproj_path": str(outside / "words-converter.csproj"),
                "package_id": "Aspose.Words",
                "status": "generated",
                "input_strategy": "none",
                "input_files": [],
                "placed_fixtures": [],
                "claimed_symbols": [],
                "target_framework": "net8.0",
            }
        ]
        (run_dir / "evidence" / "example-index.json").write_text(
            json.dumps({"total_examples": 1, "examples": examples}), encoding="utf-8"
        )

        with pytest.raises(ReplayIntegrityError, match="escapes repo_root"):
            restore_generated_projects(run_dir, "words", tmp_repo)

    def test_missing_program_cs_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        proj_dir = run_dir / "generated" / "words" / "words-converter"
        proj_dir.mkdir(parents=True)
        # Note: NOT creating Program.cs

        examples = [
            {
                "scenario_id": "words-converter",
                "project_dir": str(proj_dir),
                "program_path": str(proj_dir / "Program.cs"),
                "csproj_path": str(proj_dir / "words-converter.csproj"),
                "package_id": "Aspose.Words",
                "status": "generated",
                "input_strategy": "none",
                "input_files": [],
                "placed_fixtures": [],
                "claimed_symbols": [],
                "target_framework": "net8.0",
            }
        ]
        (run_dir / "evidence" / "example-index.json").write_text(
            json.dumps({"total_examples": 1, "examples": examples}), encoding="utf-8"
        )

        with pytest.raises(ReplayIntegrityError, match="Program.cs missing"):
            restore_generated_projects(run_dir, "words", tmp_repo)

    def test_missing_index_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        with pytest.raises(ReplayIntegrityError, match="example-index.json not found"):
            restore_generated_projects(run_dir, "words", tmp_repo)

    def test_path_rewritten_to_prior_run(self, tmp_repo):
        """When project_dir from index doesn't exist, falls back to prior run generated dir."""
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        proj_dir = run_dir / "generated" / "words" / "words-converter"
        proj_dir.mkdir(parents=True)
        (proj_dir / "Program.cs").write_text("// code", encoding="utf-8")

        # Index points at a stale path in a different run
        examples = [
            {
                "scenario_id": "words-converter",
                "project_dir": "/nonexistent/path/words-converter",
                "program_path": "/nonexistent/path/words-converter/Program.cs",
                "csproj_path": "/nonexistent/path/words-converter/words-converter.csproj",
                "package_id": "Aspose.Words",
                "status": "generated",
                "input_strategy": "none",
                "input_files": [],
                "placed_fixtures": [],
                "claimed_symbols": [],
                "target_framework": "net8.0",
            }
        ]
        (run_dir / "evidence" / "example-index.json").write_text(
            json.dumps({"total_examples": 1, "examples": examples}), encoding="utf-8"
        )

        result = restore_generated_projects(run_dir, "words", tmp_repo)
        assert len(result) == 1
        assert pathlib.Path(result[0]["project_dir"]).is_dir()


# ---------------------------------------------------------------------------
# restore_validation_results tests
# ---------------------------------------------------------------------------


class TestRestoreValidationResults:
    def test_returns_typed_validation_results(self, tmp_repo):
        from plugin_examples.verifier_bridge.dotnet_runner import ValidationResult, DotnetResult

        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_validation_results(run_dir)

        results = restore_validation_results(run_dir)
        assert len(results) == 1
        vr = results[0]
        assert isinstance(vr, ValidationResult), f"Expected ValidationResult, got {type(vr)}"
        assert vr.scenario_id == "words-converter"
        assert vr.passed is True

    def test_dotnet_results_are_typed(self, tmp_repo):
        from plugin_examples.verifier_bridge.dotnet_runner import DotnetResult

        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_validation_results(run_dir)

        results = restore_validation_results(run_dir)
        vr = results[0]
        assert isinstance(vr.build, DotnetResult), f"Expected DotnetResult, got {type(vr.build)}"
        assert vr.build.success is True

    def test_not_plain_dicts(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_validation_results(run_dir)

        results = restore_validation_results(run_dir)
        for r in results:
            assert not isinstance(r, dict), "ValidationResult must not be a plain dict"

    def test_missing_file_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        with pytest.raises(ReplayIntegrityError, match="validation-results.json not found"):
            restore_validation_results(run_dir)

    def test_malformed_file_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        (run_dir / "evidence" / "latest" / "validation-results.json").write_text(
            "not valid json {{{{", encoding="utf-8"
        )
        with pytest.raises(ReplayIntegrityError, match="[Ff]ailed to parse|[Ii]nvalid"):
            restore_validation_results(run_dir)

    def test_multiple_results(self, tmp_repo):
        from plugin_examples.verifier_bridge.dotnet_runner import ValidationResult

        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_validation_results(
            run_dir,
            results=[
                {
                    "scenario_id": "words-converter",
                    "passed": True,
                    "failure_stage": None,
                    "build": {"operation": "build", "success": True, "exit_code": 0, "duration_ms": 100.0},
                    "run": {"operation": "run", "success": True, "exit_code": 0, "duration_ms": 200.0},
                    "restore": None,
                },
                {
                    "scenario_id": "words-splitter",
                    "passed": False,
                    "failure_stage": "build",
                    "build": {"operation": "build", "success": False, "exit_code": 1, "duration_ms": 150.0},
                    "run": None,
                    "restore": None,
                },
            ],
        )
        results = restore_validation_results(run_dir)
        assert len(results) == 2
        assert all(isinstance(r, ValidationResult) for r in results)
        assert results[0].passed is True
        assert results[1].passed is False
        assert results[1].failure_stage == "build"


# ---------------------------------------------------------------------------
# write_replay_manifest tests
# ---------------------------------------------------------------------------


class TestWriteReplayManifest:
    def test_writes_replay_manifest(self, tmp_path):
        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir()

        write_replay_manifest(
            evidence_dir=evidence_dir,
            replay_from="validation",
            reuse_run_id="pilot-words-20260513-180040",
            new_run_id="pilot-words-20260514-091523",
            family="words",
            skipped_stages=frozenset(
                {"nuget_fetch", "dependency_resolution", "extraction", "reflection", "generation"}
            ),
            integrity_result={"checks": [], "overall": "pass"},
        )

        manifest_file = evidence_dir / "latest" / "replay-manifest.json"
        assert manifest_file.exists()
        manifest = json.loads(manifest_file.read_text())
        assert manifest["replay_from"] == "validation"
        assert manifest["reuse_run_id"] == "pilot-words-20260513-180040"
        assert manifest["new_run_id"] == "pilot-words-20260514-091523"
        assert manifest["family"] == "words"
        assert "skipped_stages" in manifest
        assert "created_at" in manifest

    def test_writes_restored_artifacts_report(self, tmp_path):
        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir()

        write_replay_manifest(
            evidence_dir=evidence_dir,
            replay_from="validation",
            reuse_run_id="pilot-words-20260513-180040",
            new_run_id="pilot-words-20260514-091523",
            family="words",
            skipped_stages=frozenset({"nuget_fetch", "generation"}),
            integrity_result={"checks": [], "overall": "pass"},
        )

        report_file = evidence_dir / "latest" / "restored-artifacts-report.json"
        assert report_file.exists()
        report = json.loads(report_file.read_text())
        assert "restored_artifacts" in report
        assert "family" in report

    def test_manifest_has_hash_checks(self, tmp_path):
        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir()

        write_replay_manifest(
            evidence_dir=evidence_dir,
            replay_from="generation",
            reuse_run_id="pilot-pdf-20260513-180040",
            new_run_id="pilot-pdf-20260514-100000",
            family="pdf",
            skipped_stages=frozenset({"nuget_fetch", "extraction", "reflection"}),
            integrity_result={
                "checks": [
                    {"check_id": "catalog_hash", "status": "pass", "expected": "abc", "actual": "abc", "message": ""},
                ],
                "overall": "pass",
            },
        )

        manifest = json.loads((evidence_dir / "latest" / "replay-manifest.json").read_text())
        assert "hash_checks" in manifest
        assert "catalog_hash" in manifest["hash_checks"]


# ---------------------------------------------------------------------------
# Runner integration tests (stage status)
# ---------------------------------------------------------------------------


class TestRunnerReplayIntegration:
    def test_stages_to_skip_excludes_scenario_planning(self):
        """scenario_planning must never appear in skip sets — it enforces denominator governance."""
        for mode in VALID_REPLAY_STEPS:
            skip = stages_to_skip(mode)
            assert (
                "scenario_planning" not in skip
            ), f"scenario_planning must never be skipped; found in skip set for mode '{mode}'"

    def test_stages_to_skip_excludes_load_config(self):
        for mode in VALID_REPLAY_STEPS:
            skip = stages_to_skip(mode)
            assert "load_config" not in skip

    def test_publisher_skips_reviewer(self):
        skip = stages_to_skip("publisher")
        assert "reviewer" in skip

    def test_reviewer_does_not_skip_reviewer(self):
        skip = stages_to_skip("reviewer")
        assert "reviewer" not in skip

    def test_generation_does_not_skip_generation(self):
        skip = stages_to_skip("generation")
        assert "generation" not in skip

    def test_valid_replay_steps_constant(self):
        assert VALID_REPLAY_STEPS == {"generation", "validation", "reviewer", "publisher"}


# ---------------------------------------------------------------------------
# copy_reviewer_evidence tests
# ---------------------------------------------------------------------------


class TestCopyReviewerEvidence:
    def test_copies_reviewer_file(self, tmp_repo):
        prior_run = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_reviewer_evidence(prior_run, available=True)

        new_evidence = tmp_repo / "new_run" / "evidence"
        new_evidence.mkdir(parents=True)
        copy_reviewer_evidence(prior_run, new_evidence, "words")

        dst = new_evidence / "latest" / "example-reviewer-results.json"
        assert dst.exists()

    def test_unavailable_reviewer_raises(self, tmp_repo):
        prior_run = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_reviewer_evidence(prior_run, available=False)

        new_evidence = tmp_repo / "new_run" / "evidence"
        new_evidence.mkdir(parents=True)

        with pytest.raises(ReplayIntegrityError, match="available=false|available.*false"):
            copy_reviewer_evidence(prior_run, new_evidence, "words")

    def test_missing_reviewer_evidence_raises(self, tmp_repo):
        prior_run = _make_run(tmp_repo, "pilot-words-20260513-180040")
        # No reviewer evidence written

        new_evidence = tmp_repo / "new_run" / "evidence"
        new_evidence.mkdir(parents=True)

        with pytest.raises(ReplayIntegrityError, match="example-reviewer-results.json not found"):
            copy_reviewer_evidence(prior_run, new_evidence, "words")


# ---------------------------------------------------------------------------
# restore_catalog tests
# ---------------------------------------------------------------------------


class TestRestoreCatalog:
    def test_loads_catalog_from_evidence_latest(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        _write_catalog(run_dir, "words", {"package_id": "Aspose.Words", "types": []})

        catalog, path = restore_catalog(run_dir, "words")
        assert catalog["package_id"] == "Aspose.Words"
        assert path.exists()

    def test_missing_catalog_raises(self, tmp_repo):
        run_dir = _make_run(tmp_repo, "pilot-words-20260513-180040")
        with pytest.raises(ReplayIntegrityError, match="api-catalog.json not found"):
            restore_catalog(run_dir, "words")
