"""Bridge to example-reviewer for publishing gate validation."""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class ReviewerUnavailableError(Exception):
    """Raised when the example-reviewer is not available."""


@dataclass
class ReviewerResult:
    """Result of example-reviewer validation."""
    available: bool = False
    passed: bool = False
    error: str | None = None
    details: dict | None = None


def check_reviewer_availability(
    reviewer_path: Path | None = None,
) -> bool:
    """Check if example-reviewer is available.

    Args:
        reviewer_path: Path to example-reviewer repo.

    Returns:
        True if reviewer CLI is accessible.
    """
    if reviewer_path and not reviewer_path.exists():
        return False

    try:
        cmd = ["python", "-m", "src.cli.main", "status", "--json"]
        result = subprocess.run(
            cmd,
            cwd=str(reviewer_path) if reviewer_path else None,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def run_example_reviewer(
    *,
    family: str,
    workspace_dir: Path,
    reviewer_path: Path | None = None,
    timeout: int = 300,
) -> ReviewerResult:
    """Run example-reviewer on generated examples.

    Args:
        family: Family name.
        workspace_dir: Workspace directory with generated examples.
        reviewer_path: Path to example-reviewer repo.
        timeout: Subprocess timeout in seconds.

    Returns:
        ReviewerResult.

    Raises:
        ReviewerUnavailableError: If reviewer is not available.
    """
    if not check_reviewer_availability(reviewer_path):
        raise ReviewerUnavailableError(
            "example-reviewer is not available. "
            "Ensure the repo is cloned and dependencies installed."
        )

    try:
        cmd = [
            "python", "-m", "src.cli.main",
            "compile-verify",
            "--family", family,
            "--json",
        ]

        proc = subprocess.run(
            cmd,
            cwd=str(reviewer_path) if reviewer_path else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        result = ReviewerResult(available=True)

        if proc.returncode == 0:
            result.passed = True
            try:
                result.details = json.loads(proc.stdout)
            except json.JSONDecodeError:
                result.details = {"raw_output": proc.stdout[:1000]}
        else:
            result.passed = False
            result.error = proc.stderr[:500] if proc.stderr else "Unknown error"

        return result

    except subprocess.TimeoutExpired:
        return ReviewerResult(
            available=True,
            passed=False,
            error=f"Reviewer timed out after {timeout}s",
        )


def write_reviewer_results(
    result: ReviewerResult,
    verification_dir: Path,
) -> Path:
    """Write example-reviewer results."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "example-reviewer-results.json"

    data = {
        "available": result.available,
        "passed": result.passed,
        "error": result.error,
        "details": result.details,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Reviewer results written: %s", path)
    return path
