"""Bridge to example-reviewer for publishing gate validation."""

from __future__ import annotations

import json
import logging
import os
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
        python_exe = _get_reviewer_python(reviewer_path)
        cmd = [python_exe, "-m", "src.cli.main", "--json", "--safe-workspace", "status"]
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


def _get_reviewer_python(reviewer_path: Path | None) -> str:
    """Get the Python executable for the reviewer (prefer its venv)."""
    if reviewer_path:
        # Windows venv
        venv_python = reviewer_path / ".venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            return str(venv_python)
        # Unix venv
        venv_python = reviewer_path / ".venv" / "bin" / "python"
        if venv_python.exists():
            return str(venv_python)
    return "python"


def _resolve_reviewer_path(reviewer_path: Path | None = None) -> Path | None:
    """Resolve reviewer path from explicit arg, env var, or sibling directory."""
    if reviewer_path:
        return reviewer_path
    env_path = os.environ.get("EXAMPLE_REVIEWER_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p
    # Try sibling directory convention
    sibling = Path(__file__).resolve().parents[3] / "example-reviewer"
    if sibling.exists():
        return sibling
    return None


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
    reviewer_path = _resolve_reviewer_path(reviewer_path)
    if not check_reviewer_availability(reviewer_path):
        raise ReviewerUnavailableError(
            "example-reviewer is not available. "
            "Ensure the repo is cloned and dependencies installed."
        )

    try:
        python_exe = _get_reviewer_python(reviewer_path)
        cmd = [
            python_exe, "-m", "src.cli.main",
            "--json", "--safe-workspace",
            "compile-verify",
            "--family", family,
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
