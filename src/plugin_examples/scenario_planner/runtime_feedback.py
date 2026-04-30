"""Classify runtime failure feedback for scenario healing."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RuntimeFailureClassification:
    """Classification of a runtime failure."""
    scenario_id: str
    exit_code: int
    classification: str
    detail: str
    actionable: bool
    recommendation: str


# Classification patterns — order matters (first match wins)
_PATTERNS: list[tuple[str, str, bool, str]] = [
    # (regex, classification, actionable, recommendation)
    (
        r"Cannot read keys when either application does not have a console|Console\.ReadKey|Console\.ReadLine",
        "interactive_console_call",
        True,
        "Code uses Console.ReadKey/ReadLine which fails in headless CI. "
        "Remove interactive input calls from generated code.",
    ),
    (
        r"Only text based formats|CellsException.*text based",
        "wrong_input_format",
        True,
        "API requires a different input format. Check scenario input format mapping.",
    ),
    (
        r"No input has been specified for the process|No input has been specified",
        "missing_options_input",
        True,
        "LowCodeLoadOptions.InputFile was not set before calling Process(). "
        "Use the simple string-path overload, or set InputFile on LowCodeLoadOptions.",
    ),
    (
        r"System\.NullReferenceException.*LowCode|LowCode.*System\.NullReferenceException",
        "null_options_passed",
        True,
        "Null was passed for LowCodeLoadOptions or LowCodeSaveOptions. "
        "Use the simple string-path overload instead of passing null options.",
    ),
    (
        r"System\.NullReferenceException",
        "blocked_runtime_context_required",
        True,
        "NullReferenceException — likely caused by passing null options or uninitialized options. "
        "Use the simple string-path overload, or ensure all required properties are set.",
    ),
    (
        r"System\.ArgumentNullException",
        "blocked_null_argument",
        True,
        "Method requires non-null argument. Provide valid input file or object.",
    ),
    (
        r"System\.IO\.FileNotFoundException|Could not find file",
        "blocked_missing_fixture",
        True,
        "Input file not found. Ensure fixture file is available.",
    ),
    (
        r"System\.IO\.DirectoryNotFoundException",
        "blocked_missing_directory",
        True,
        "Output directory not found. Ensure output path exists.",
    ),
    (
        r"System\.InvalidOperationException",
        "blocked_invalid_operation",
        True,
        "Operation invalid in current state. Review API usage sequence.",
    ),
    (
        r"System\.NotImplementedException",
        "blocked_not_implemented",
        False,
        "Method not implemented. Skip this scenario.",
    ),
    (
        r"System\.TypeInitializationException",
        "blocked_type_init_failed",
        False,
        "Type initialization failed. May require license or native dependency.",
    ),
    (
        r"System\.DllNotFoundException|Unable to load shared library",
        "blocked_native_dependency",
        False,
        "Native dependency missing. Cannot run in this environment.",
    ),
]


def classify_runtime_failure(
    scenario_id: str,
    exit_code: int,
    stdout: str = "",
    stderr: str = "",
) -> RuntimeFailureClassification:
    """Classify a runtime failure based on exit code and output.

    Args:
        scenario_id: Scenario identifier.
        exit_code: Process exit code.
        stdout: Standard output text.
        stderr: Standard error text.

    Returns:
        RuntimeFailureClassification with actionable recommendation.
    """
    combined = f"{stdout}\n{stderr}"

    for pattern, classification, actionable, recommendation in _PATTERNS:
        if re.search(pattern, combined):
            # Extract detail from the matched line
            for line in combined.splitlines():
                if re.search(pattern, line):
                    detail = line.strip()[:200]
                    break
            else:
                detail = f"Matched pattern: {pattern}"

            return RuntimeFailureClassification(
                scenario_id=scenario_id,
                exit_code=exit_code,
                classification=classification,
                detail=detail,
                actionable=actionable,
                recommendation=recommendation,
            )

    # Unknown failure
    return RuntimeFailureClassification(
        scenario_id=scenario_id,
        exit_code=exit_code,
        classification="unknown_runtime_failure",
        detail=combined.strip()[:200] if combined.strip() else f"Exit code {exit_code}",
        actionable=False,
        recommendation="Investigate runtime output manually.",
    )


def classify_validation_results(validation_results: list) -> list[RuntimeFailureClassification]:
    """Classify all runtime failures from validation results.

    Args:
        validation_results: List of ValidationResult from dotnet_runner.

    Returns:
        List of classifications for failed runs only.
    """
    classifications = []
    for vr in validation_results:
        if vr.run and not vr.run.success:
            classifications.append(classify_runtime_failure(
                scenario_id=vr.scenario_id,
                exit_code=vr.run.exit_code,
                stdout=vr.run.stdout or "",
                stderr=vr.run.stderr or "",
            ))
    return classifications


def write_runtime_failure_classifications(
    classifications: list[RuntimeFailureClassification],
    verification_dir: Path,
) -> Path:
    """Write runtime failure classification evidence."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "runtime-failure-classifications.json"

    summary: dict[str, int] = {}
    for c in classifications:
        summary[c.classification] = summary.get(c.classification, 0) + 1

    data = {
        "total_failures": len(classifications),
        "classification_summary": summary,
        "classifications": [
            {
                "scenario_id": c.scenario_id,
                "exit_code": c.exit_code,
                "classification": c.classification,
                "detail": c.detail,
                "actionable": c.actionable,
                "recommendation": c.recommendation,
            }
            for c in classifications
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Runtime failure classifications written: %s", path)
    return path
