"""Local .NET validation harness — restore, build, run generated examples."""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DotnetResult:
    """Result of a single dotnet operation."""
    operation: str  # restore, build, run
    success: bool
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0.0


@dataclass
class ValidationResult:
    """Full validation result for a generated example."""
    scenario_id: str
    restore: DotnetResult | None = None
    build: DotnetResult | None = None
    run: DotnetResult | None = None
    passed: bool = False
    failure_stage: str | None = None


def run_dotnet_validation(
    project_dir: Path,
    scenario_id: str,
    *,
    skip_run: bool = False,
    timeout: int = 120,
) -> ValidationResult:
    """Run restore, build, and optionally run on a generated project.

    Args:
        project_dir: Path to the project directory.
        scenario_id: Scenario identifier.
        skip_run: If True, skip the run step.
        timeout: Subprocess timeout in seconds.

    Returns:
        ValidationResult with results for each stage.
    """
    result = ValidationResult(scenario_id=scenario_id)

    # Restore
    result.restore = _run_dotnet("restore", project_dir, timeout)
    if not result.restore.success:
        result.failure_stage = "restore"
        return result

    # Build
    result.build = _run_dotnet("build", project_dir, timeout, extra_args=["--no-restore"])
    if not result.build.success:
        result.failure_stage = "build"
        return result

    # Run
    if not skip_run:
        result.run = _run_dotnet("run", project_dir, timeout, extra_args=["--no-build"])
        if not result.run.success:
            result.failure_stage = "run"
            return result

    result.passed = True
    return result


def write_validation_results(
    results: list[ValidationResult],
    verification_dir: Path,
) -> Path:
    """Write validation results summary."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "validation-results.json"

    data = {
        "total": len(results),
        "passed": len([r for r in results if r.passed]),
        "failed": len([r for r in results if not r.passed]),
        "results": [
            {
                "scenario_id": r.scenario_id,
                "passed": r.passed,
                "failure_stage": r.failure_stage,
                "restore": _result_to_dict(r.restore) if r.restore else None,
                "build": _result_to_dict(r.build) if r.build else None,
                "run": _result_to_dict(r.run) if r.run else None,
            }
            for r in results
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Validation results written: %s", path)
    return path


def _run_dotnet(
    command: str,
    project_dir: Path,
    timeout: int,
    extra_args: list[str] | None = None,
) -> DotnetResult:
    """Run a dotnet command."""
    cmd = ["dotnet", command]
    if extra_args:
        cmd.extend(extra_args)

    import time
    start = time.time()

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = (time.time() - start) * 1000

        return DotnetResult(
            operation=command,
            success=proc.returncode == 0,
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_ms=duration,
        )
    except subprocess.TimeoutExpired:
        return DotnetResult(
            operation=command,
            success=False,
            exit_code=-1,
            stderr=f"Timeout after {timeout}s",
        )
    except FileNotFoundError:
        return DotnetResult(
            operation=command,
            success=False,
            exit_code=-1,
            stderr="dotnet CLI not found",
        )


def _result_to_dict(r: DotnetResult) -> dict:
    return {
        "operation": r.operation,
        "success": r.success,
        "exit_code": r.exit_code,
        "duration_ms": r.duration_ms,
    }
