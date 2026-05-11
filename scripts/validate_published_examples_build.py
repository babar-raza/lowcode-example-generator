#!/usr/bin/env python3
"""Validate that published examples still build with dotnet.

This script clones each family's target repository (shallow, depth=1)
and runs ``dotnet build`` to verify examples compile successfully.

Usage:
    python scripts/validate_published_examples_build.py [--output PATH]

Exit codes:
    0 — all families build successfully
    1 — one or more families have build failures
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

FAMILY_REPO_MAP: dict[str, str] = {
    "cells": "aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples",
    "words": "aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples",
    "pdf": "aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples",
}


@dataclass
class FamilyBuildResult:
    family: str
    repo: str
    build_exit_code: int = -1
    build_stdout: str = ""
    build_stderr: str = ""
    verdict: str = "NOT_RUN"  # PASS, REGRESSED, CLONE_FAILED, NOT_RUN
    error: str | None = None


@dataclass
class MonthlyBuildReport:
    generated_at: str = ""
    families_checked: int = 0
    families_passed: int = 0
    families_regressed: int = 0
    overall_verdict: str = "NOT_RUN"  # ALL_PASS, REGRESSION_DETECTED, PARTIAL, NOT_RUN
    results: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def discover_published_families(repo_root: Path) -> dict[str, str]:
    """Discover families with merge results (published examples)."""
    published: dict[str, str] = {}
    verification_dir = repo_root / "workspace" / "verification" / "latest"
    for family, repo in FAMILY_REPO_MAP.items():
        merge_file = verification_dir / f"{family}-merge-result.json"
        if merge_file.exists():
            try:
                data = json.loads(merge_file.read_text(encoding="utf-8"))
                target = data.get("target_repo", repo)
                published[family] = target
            except (json.JSONDecodeError, KeyError):
                published[family] = repo
    return published


def clone_and_build(family: str, repo: str, token: str | None = None) -> FamilyBuildResult:
    """Shallow-clone a repo and run dotnet build."""
    result = FamilyBuildResult(family=family, repo=repo)
    tmpdir = tempfile.mkdtemp(prefix=f"build-check-{family}-")

    try:
        # Build clone URL
        if token:
            clone_url = f"https://x-access-token:{token}@github.com/{repo}.git"
        else:
            clone_url = f"https://github.com/{repo}.git"

        # Shallow clone
        clone_proc = subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, tmpdir],
            capture_output=True, text=True, timeout=120,
        )
        if clone_proc.returncode != 0:
            result.verdict = "CLONE_FAILED"
            result.error = clone_proc.stderr[:500]
            return result

        # Find .sln or .csproj
        build_target = _find_build_target(Path(tmpdir))
        if not build_target:
            result.verdict = "REGRESSED"
            result.error = "No .sln or .csproj found in repo root"
            return result

        # Run dotnet build
        build_proc = subprocess.run(
            ["dotnet", "build", str(build_target), "-c", "Release", "--nologo"],
            capture_output=True, text=True, timeout=300,
            cwd=tmpdir,
        )
        result.build_exit_code = build_proc.returncode
        result.build_stdout = build_proc.stdout[:2000]
        result.build_stderr = build_proc.stderr[:2000]

        if build_proc.returncode == 0:
            result.verdict = "PASS"
        else:
            result.verdict = "REGRESSED"
            result.error = "dotnet build failed (exit code {})".format(build_proc.returncode)

    except subprocess.TimeoutExpired:
        result.verdict = "REGRESSED"
        result.error = "Build timed out"
    except Exception as exc:
        result.verdict = "REGRESSED"
        result.error = str(exc)[:500]
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    return result


def _find_build_target(repo_dir: Path) -> Path | None:
    """Find .sln or .csproj at repo root or one level deep."""
    for ext in ("*.sln", "*.csproj"):
        matches = list(repo_dir.glob(ext))
        if matches:
            return matches[0]
    # Check one level deep
    for ext in ("*.sln", "*.csproj"):
        matches = list(repo_dir.glob(f"*/{ext}"))
        if matches:
            return matches[0]
    return None


def build_report(results: list[FamilyBuildResult]) -> MonthlyBuildReport:
    """Build the monthly report from individual results."""
    report = MonthlyBuildReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        families_checked=len(results),
        families_passed=sum(1 for r in results if r.verdict == "PASS"),
        families_regressed=sum(1 for r in results if r.verdict == "REGRESSED"),
        results=[asdict(r) for r in results],
    )

    if report.families_regressed > 0:
        report.overall_verdict = "REGRESSION_DETECTED"
    elif report.families_passed == report.families_checked:
        report.overall_verdict = "ALL_PASS"
    else:
        report.overall_verdict = "PARTIAL"

    return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate published examples build")
    parser.add_argument(
        "--output", default=None,
        help="Output JSON path (default: workspace/verification/latest/monthly-build-regression-report.json)",
    )
    parser.add_argument(
        "--repo-root", default=None,
        help="Repository root (default: auto-detect)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else Path(__file__).resolve().parents[1]
    token = os.environ.get("GITHUB_TOKEN")

    published = discover_published_families(repo_root)
    if not published:
        print("No published families found. Nothing to validate.")
        return 0

    results: list[FamilyBuildResult] = []
    for family, repo in sorted(published.items()):
        print(f"Checking {family} ({repo})...")
        result = clone_and_build(family, repo, token=token)
        results.append(result)
        print(f"  -> {result.verdict}")

    report = build_report(results)

    output_path = Path(args.output) if args.output else (
        repo_root / "workspace" / "verification" / "latest" / "monthly-build-regression-report.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    print(f"\nReport written to {output_path}")
    print(f"Overall verdict: {report.overall_verdict}")

    return 1 if report.families_regressed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
