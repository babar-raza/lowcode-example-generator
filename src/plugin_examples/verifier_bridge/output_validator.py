"""Validate output of generated example runs."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class OutputValidation:
    """Result of output validation."""
    scenario_id: str
    passed: bool = False
    has_output: bool = False
    has_error: bool = False
    output_length: int = 0
    issues: list[str] = field(default_factory=list)


def validate_output(
    scenario_id: str,
    stdout: str,
    stderr: str,
    *,
    expected_patterns: list[str] | None = None,
) -> OutputValidation:
    """Validate the output of a generated example run.

    Args:
        scenario_id: Scenario identifier.
        stdout: Standard output from the run.
        stderr: Standard error from the run.
        expected_patterns: Optional patterns to check in output.

    Returns:
        OutputValidation result.
    """
    result = OutputValidation(
        scenario_id=scenario_id,
        has_output=len(stdout.strip()) > 0,
        output_length=len(stdout),
    )

    # Check for error indicators in stderr
    if stderr and any(kw in stderr.lower() for kw in ["exception", "error", "fatal"]):
        result.has_error = True
        result.issues.append(f"Error output detected: {stderr[:200]}")

    # Check for unhandled exceptions in stdout
    if "Unhandled exception" in stdout:
        result.has_error = True
        result.issues.append("Unhandled exception in output")

    if not result.has_output:
        result.issues.append("No output produced")

    # Check expected patterns
    if expected_patterns:
        for pattern in expected_patterns:
            if pattern not in stdout:
                result.issues.append(f"Missing expected output: {pattern}")

    result.passed = not result.has_error and result.has_output and len(result.issues) == 0

    return result


def write_output_validation(
    validation: OutputValidation,
    run_dir: Path,
) -> Path:
    """Write output validation result for a scenario."""
    val_dir = run_dir / "validation" / validation.scenario_id
    val_dir.mkdir(parents=True, exist_ok=True)
    path = val_dir / "output-validation.json"

    data = {
        "scenario_id": validation.scenario_id,
        "passed": validation.passed,
        "has_output": validation.has_output,
        "has_error": validation.has_error,
        "output_length": validation.output_length,
        "issues": validation.issues,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return path
