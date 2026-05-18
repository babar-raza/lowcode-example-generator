"""Batch publication orchestrator.

Provides one-command orchestration of the multi-package PDF publication workflow.
Runs publish-pr (dry-run or live) for all 6 PDF PR packages in sequence,
collecting results into a single batch report.

Usage (programmatic):
    from plugin_examples.publisher.batch_publisher import run_batch_publish

Usage (CLI):
    python -m plugin_examples publish-pr-batch [--family pdf] [--publish] [--approval-token ...]
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

logger = logging.getLogger(__name__)

# Ordered list of (pr_number, package_name) for PDF publication
PDF_PR_PACKAGES: list[tuple[int, str]] = [
    (3, "pdf-controlled-pilot"),
    (5, "pdf-controlled-pilot-pr5"),
    (6, "pdf-controlled-pilot-pr6"),
    (7, "pdf-controlled-pilot-pr7"),
    (8, "pdf-controlled-pilot-pr8"),
    (9, "pdf-controlled-pilot-pr9"),
]


@dataclass
class PackagePublishResult:
    """Result of publishing a single PR package."""
    pr_number: int
    package_name: str
    exit_code: int
    stdout: str
    stderr: str
    simulation_passed: bool | None
    live_pr_url: str | None = None
    error: str | None = None


@dataclass
class BatchPublishResult:
    """Aggregated result of a batch publish run."""
    started_at: str
    finished_at: str
    family: str
    live_mode: bool
    approval_gate_set: bool
    results: list[PackagePublishResult] = field(default_factory=list)
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    blocked: int = 0

    @property
    def all_passed(self) -> bool:
        return self.succeeded == self.total and self.failed == 0

    @property
    def verdict(self) -> str:
        if not self.approval_gate_set:
            return "BATCH_APPROVAL_BLOCKED_DRY_RUN_ONLY"
        if self.all_passed:
            return "BATCH_PUBLISH_ALL_PASSED"
        if self.failed == 0:
            return "BATCH_PUBLISH_PARTIAL"
        return f"BATCH_PUBLISH_FAILED_{self.failed}_OF_{self.total}"


def run_batch_publish(
    family: str,
    repo_root: Path,
    *,
    live_mode: bool = False,
    approval_token: str | None = None,
    package_path_override: str | None = None,
    promote_latest: bool = True,
    python_exe: str | None = None,
) -> BatchPublishResult:
    """Run publish-pr for all packages in a family batch.

    Args:
        family: Family name (typically "pdf").
        repo_root: Root of the lowcode-example-generator repo.
        live_mode: If True, pass --publish (requires APPROVE_LIVE_PR gate).
        approval_token: Approval token value for the gate.
        package_path_override: Override package path (for testing).
        promote_latest: Pass --promote-latest to each publish-pr call.
        python_exe: Path to Python executable (defaults to sys.executable).

    Returns:
        BatchPublishResult with per-package and aggregate results.
    """
    started_at = datetime.now(timezone.utc).isoformat()
    py = python_exe or sys.executable

    # Determine approval gate status
    import os
    gate_value = os.environ.get("PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL", "")
    approval_gate_set = (
        gate_value == "APPROVE_LIVE_PR"
        or approval_token == "APPROVE_LIVE_PR"
    )

    packages = _get_packages_for_family(family)
    results: list[PackagePublishResult] = []

    for pr_number, package_name in packages:
        pkg_path = package_path_override or str(repo_root / "workspace" / "pr-dry-run" / package_name)

        # Build command
        cmd = [
            py, "-m", "plugin_examples",
            "publish-pr",
            "--family", family,
            "--package-path", pkg_path,
        ]
        if live_mode and approval_gate_set:
            cmd += ["--publish", "--approval-token", "APPROVE_LIVE_PR"]
        else:
            cmd += ["--dry-run"]
        if promote_latest:
            cmd += ["--promote-latest"]

        logger.info(
            "Running publish-pr for PR#%d (%s): %s",
            pr_number, package_name, " ".join(cmd),
        )

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(repo_root),
                timeout=300,
            )
            combined_out = proc.stdout + "\n" + proc.stderr
            simulation_passed = proc.returncode == 0

            # Extract live PR URL if present in output
            live_pr_url = None
            for line in combined_out.splitlines():
                if "PR created:" in line or "html_url" in line:
                    parts = line.strip().split(":", 1)
                    if len(parts) == 2:
                        live_pr_url = parts[1].strip()
                        break

            results.append(PackagePublishResult(
                pr_number=pr_number,
                package_name=package_name,
                exit_code=proc.returncode,
                stdout=proc.stdout[:3000],
                stderr=proc.stderr[:1000],
                simulation_passed=simulation_passed,
                live_pr_url=live_pr_url,
            ))
        except subprocess.TimeoutExpired:
            results.append(PackagePublishResult(
                pr_number=pr_number,
                package_name=package_name,
                exit_code=-1,
                stdout="",
                stderr="",
                simulation_passed=False,
                error="Timeout after 300s",
            ))
        except Exception as e:
            results.append(PackagePublishResult(
                pr_number=pr_number,
                package_name=package_name,
                exit_code=-1,
                stdout="",
                stderr="",
                simulation_passed=False,
                error=str(e),
            ))

    finished_at = datetime.now(timezone.utc).isoformat()
    total = len(results)
    succeeded = sum(1 for r in results if r.simulation_passed)
    failed = sum(1 for r in results if not r.simulation_passed and r.error)
    blocked = sum(1 for r in results if not r.simulation_passed and not r.error)

    return BatchPublishResult(
        started_at=started_at,
        finished_at=finished_at,
        family=family,
        live_mode=live_mode,
        approval_gate_set=approval_gate_set,
        results=results,
        total=total,
        succeeded=succeeded,
        failed=failed,
        blocked=blocked,
    )


def write_batch_report(result: BatchPublishResult, output_path: Path) -> Path:
    """Write a batch publish report to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "family": result.family,
        "live_mode": result.live_mode,
        "approval_gate_set": result.approval_gate_set,
        "total": result.total,
        "succeeded": result.succeeded,
        "failed": result.failed,
        "blocked": result.blocked,
        "verdict": result.verdict,
        "packages": [
            {
                "pr_number": r.pr_number,
                "package_name": r.package_name,
                "exit_code": r.exit_code,
                "simulation_passed": r.simulation_passed,
                "live_pr_url": r.live_pr_url,
                "error": r.error,
                "stdout_excerpt": r.stdout[:500] if r.stdout else None,
            }
            for r in result.results
        ],
    }

    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Batch publish report written: %s", output_path)
    return output_path


def _get_packages_for_family(family: str) -> list[tuple[int, str]]:
    """Get the ordered PR packages for a family."""
    if family == "pdf":
        return PDF_PR_PACKAGES
    # For other families, return empty (single-package families use publish-pr directly)
    return []
