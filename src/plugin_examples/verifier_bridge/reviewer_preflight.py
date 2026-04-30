"""Reviewer environment preflight check with evidence output."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ReviewerPreflightResult:
    """Result of reviewer environment preflight check."""
    reviewer_path_configured: bool
    reviewer_path_exists: bool
    reviewer_python_found: bool
    reviewer_cli_responds: bool
    reviewer_version: str | None
    dotnet_sdk_found: bool
    dotnet_sdk_version: str | None
    overall_ready: bool
    issues: list[str]


def run_reviewer_preflight(
    reviewer_path: str | None = None,
) -> ReviewerPreflightResult:
    """Run a preflight check on the reviewer environment.

    Args:
        reviewer_path: Path to example-reviewer repo (or EXAMPLE_REVIEWER_PATH env).

    Returns:
        ReviewerPreflightResult with detailed status.
    """
    issues: list[str] = []

    # Resolve reviewer path
    rpath = reviewer_path or os.environ.get("EXAMPLE_REVIEWER_PATH")
    path_configured = rpath is not None
    path_exists = False
    python_found = False
    cli_responds = False
    version = None

    if not path_configured:
        issues.append("EXAMPLE_REVIEWER_PATH not set and no --reviewer-path given")
    else:
        rp = Path(rpath)
        path_exists = rp.exists() and rp.is_dir()
        if not path_exists:
            issues.append(f"Reviewer path does not exist: {rpath}")
        else:
            # Check for Python
            venv_python = rp / ".venv" / "Scripts" / "python.exe"
            if not venv_python.exists():
                venv_python = rp / ".venv" / "bin" / "python"
            if venv_python.exists():
                python_found = True
            else:
                # Try system python
                python_found = shutil.which("python") is not None
                if not python_found:
                    issues.append("No Python found for reviewer")

            # Check CLI responds
            if python_found:
                try:
                    py = str(venv_python) if venv_python.exists() else "python"
                    result = subprocess.run(
                        [py, "-m", "src.cli.main", "--json", "--safe-workspace", "status"],
                        cwd=str(rp), capture_output=True, text=True, timeout=30,
                    )
                    if result.returncode == 0:
                        cli_responds = True
                        try:
                            data = json.loads(result.stdout)
                            version = data.get("version")
                        except (json.JSONDecodeError, KeyError):
                            pass
                    else:
                        issues.append(f"Reviewer CLI returned exit code {result.returncode}")
                except Exception as e:
                    issues.append(f"Reviewer CLI check failed: {e}")

    # Check .NET SDK
    dotnet_found = False
    dotnet_version = None
    try:
        result = subprocess.run(
            ["dotnet", "--version"], capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            dotnet_found = True
            dotnet_version = result.stdout.strip()
    except Exception:
        issues.append(".NET SDK not found")

    overall_ready = path_configured and path_exists and python_found and cli_responds and dotnet_found

    return ReviewerPreflightResult(
        reviewer_path_configured=path_configured,
        reviewer_path_exists=path_exists,
        reviewer_python_found=python_found,
        reviewer_cli_responds=cli_responds,
        reviewer_version=version,
        dotnet_sdk_found=dotnet_found,
        dotnet_sdk_version=dotnet_version,
        overall_ready=overall_ready,
        issues=issues,
    )


def write_reviewer_preflight(
    result: ReviewerPreflightResult,
    verification_dir: Path,
) -> Path:
    """Write reviewer preflight evidence."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "reviewer-preflight.json"

    data = {
        "reviewer_path_configured": result.reviewer_path_configured,
        "reviewer_path_exists": result.reviewer_path_exists,
        "reviewer_python_found": result.reviewer_python_found,
        "reviewer_cli_responds": result.reviewer_cli_responds,
        "reviewer_version": result.reviewer_version,
        "dotnet_sdk_found": result.dotnet_sdk_found,
        "dotnet_sdk_version": result.dotnet_sdk_version,
        "overall_ready": result.overall_ready,
        "issues": result.issues,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Reviewer preflight written: %s", path)
    return path
