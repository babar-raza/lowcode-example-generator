"""FormImporter version-watch automation.

Tracks the Aspose.PDF NuGet version and automatically retests the FormImporter
NullReferenceException defect (TC-PDF-FORMIMPORTER-RETEST) when the package
version advances beyond 26.5.0.

Defect context:
  - Aspose.PDF 26.5.0: NullReferenceException in Forms.Form.#=zZQILclhNTKUB
    for ALL input types when calling FormImporter.Process(options).
  - Repro harness: workspace/defect-repros/pdf-formimporter-nullref/
  - Block reason: WAVE_H_DEFERRED_LIBRARY_BUG

Usage:
    python -m plugin_examples package-watch-formimporter [--run-repro]
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# The version where the defect was confirmed
DEFECT_VERSION = "26.5.0"
# Package ID to watch
PACKAGE_ID = "Aspose.PDF"
# Repro harness path relative to repo root
REPRO_HARNESS_PATH = "workspace/defect-repros/pdf-formimporter-nullref"


@dataclass
class FormImporterWatchResult:
    """Result of a FormImporter version-watch check."""

    checked_at: str
    current_version: str | None
    latest_nuget_version: str | None
    defect_version: str
    version_advanced: bool
    retest_triggered: bool
    retest_passed: bool | None
    retest_output: str | None
    retest_exit_code: int | None
    verdict: str  # STILL_BLOCKED | RETEST_PASSED | RETEST_FAILED | CHECK_ONLY | ERROR
    notes: list[str] = field(default_factory=list)


def _compare_versions(a: str, b: str) -> int:
    """Compare two semver-like version strings. Returns -1, 0, or 1."""

    def parts(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.split(".") if x.isdigit())

    pa, pb = parts(a), parts(b)
    if pa < pb:
        return -1
    if pa > pb:
        return 1
    return 0


def _get_installed_version(repo_root: Path) -> str | None:
    """Read the installed Aspose.PDF version from Directory.Packages.props."""
    props_path = repo_root / "generated" / "Directory.Packages.props"
    if not props_path.exists():
        return None
    try:
        content = props_path.read_text(encoding="utf-8")
        # Find: <PackageVersion Include="Aspose.PDF" Version="..." />
        import re

        m = re.search(r'Include="Aspose\.PDF"[^>]*Version="([^"]+)"', content)
        if m:
            return m.group(1)
    except Exception as e:
        logger.warning("Could not read Directory.Packages.props: %s", e)
    return None


def _get_latest_nuget_version(package_id: str) -> str | None:
    """Fetch latest stable version from NuGet v3 API."""
    try:
        import urllib.request

        url = f"https://api.nuget.org/v3-flatcontainer/{package_id.lower()}/index.json"
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        versions = data.get("versions", [])
        stable = [v for v in versions if "-" not in v]
        return stable[-1] if stable else (versions[-1] if versions else None)
    except Exception as e:
        logger.warning("NuGet API request failed for %s: %s", package_id, e)
        return None


def _run_repro_harness(repo_root: Path) -> tuple[bool, str, int]:
    """Run the FormImporter repro harness and return (passed, output, exit_code).

    The harness is expected to print 'SUCCESS' on a fixed defect,
    or include 'NullReferenceException' on a still-broken version.
    """
    harness_path = repo_root / REPRO_HARNESS_PATH
    if not harness_path.exists():
        return False, f"Repro harness not found at {harness_path}", -1

    project_file = None
    for f in harness_path.glob("*.csproj"):
        project_file = f
        break

    if not project_file:
        return False, "No .csproj found in repro harness directory", -1

    try:
        # First restore
        restore = subprocess.run(
            ["dotnet", "restore", str(project_file)],
            capture_output=True,
            text=True,
            cwd=str(harness_path),
            timeout=120,
        )
        if restore.returncode != 0:
            return False, f"dotnet restore failed:\n{restore.stdout}\n{restore.stderr}", restore.returncode

        # Then run
        run = subprocess.run(
            ["dotnet", "run", "--project", str(project_file)],
            capture_output=True,
            text=True,
            cwd=str(harness_path),
            timeout=120,
        )
        combined = run.stdout + "\n" + run.stderr
        passed = run.returncode == 0 and "NullReferenceException" not in combined and "Exception" not in combined
        return passed, combined, run.returncode
    except subprocess.TimeoutExpired:
        return False, "Repro harness timed out after 120s", -1
    except Exception as e:
        return False, f"Repro harness execution error: {e}", -1


def check_formimporter(
    repo_root: Path,
    *,
    run_repro: bool = False,
) -> FormImporterWatchResult:
    """Check FormImporter defect status against current + latest NuGet version.

    Args:
        repo_root: Root of the lowcode-example-generator repo.
        run_repro: If True and version has advanced, run the repro harness.

    Returns:
        FormImporterWatchResult with full status.
    """
    checked_at = datetime.now(timezone.utc).isoformat()
    notes: list[str] = []

    current = _get_installed_version(repo_root)
    if current is None:
        notes.append("Could not determine installed Aspose.PDF version from Directory.Packages.props")

    latest = _get_latest_nuget_version(PACKAGE_ID)
    if latest is None:
        notes.append("Could not fetch latest NuGet version (network may be unavailable)")

    # Determine if version has advanced beyond defect version
    version_advanced = False
    if latest:
        version_advanced = _compare_versions(latest, DEFECT_VERSION) > 0
        if version_advanced:
            notes.append(f"NuGet latest {latest} > defect version {DEFECT_VERSION} — retest eligible")
        else:
            notes.append(f"NuGet latest {latest} <= defect version {DEFECT_VERSION} — still blocked")
    elif current:
        version_advanced = _compare_versions(current, DEFECT_VERSION) > 0
        notes.append(f"Using installed version {current} for comparison (NuGet unavailable)")

    # Decide on retest
    if not version_advanced or not run_repro:
        verdict = "STILL_BLOCKED" if not version_advanced else "CHECK_ONLY"
        return FormImporterWatchResult(
            checked_at=checked_at,
            current_version=current,
            latest_nuget_version=latest,
            defect_version=DEFECT_VERSION,
            version_advanced=version_advanced,
            retest_triggered=False,
            retest_passed=None,
            retest_output=None,
            retest_exit_code=None,
            verdict=verdict,
            notes=notes,
        )

    # Run repro
    notes.append(f"Running repro harness at {REPRO_HARNESS_PATH}")
    passed, output, exit_code = _run_repro_harness(repo_root)
    verdict = "RETEST_PASSED" if passed else "RETEST_FAILED"
    notes.append(f"Repro exit_code={exit_code}, passed={passed}")

    if passed:
        notes.append(
            "DEFECT FIXED — FormImporter NullReferenceException no longer reproduces. "
            "TC-PDF-FORMIMPORTER-RETEST can be closed. Proceed to Wave H generation."
        )
    else:
        notes.append(f"Defect still reproduces on version {latest}. " "TC-PDF-FORMIMPORTER-RETEST remains open.")

    return FormImporterWatchResult(
        checked_at=checked_at,
        current_version=current,
        latest_nuget_version=latest,
        defect_version=DEFECT_VERSION,
        version_advanced=version_advanced,
        retest_triggered=True,
        retest_passed=passed,
        retest_output=output[:2000] if output else None,  # cap output
        retest_exit_code=exit_code,
        verdict=verdict,
        notes=notes,
    )


def write_watch_report(result: FormImporterWatchResult, output_path: Path) -> Path:
    """Write a FormImporter watch report to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "checked_at": result.checked_at,
        "current_installed_version": result.current_version,
        "latest_nuget_version": result.latest_nuget_version,
        "defect_version": result.defect_version,
        "version_advanced_beyond_defect": result.version_advanced,
        "retest_triggered": result.retest_triggered,
        "retest_passed": result.retest_passed,
        "retest_exit_code": result.retest_exit_code,
        "retest_output_excerpt": result.retest_output,
        "verdict": result.verdict,
        "notes": result.notes,
        "taskcard": "TC-PDF-FORMIMPORTER-RETEST",
        "defect_repro_path": REPRO_HARNESS_PATH,
    }
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("FormImporter watch report written: %s", output_path)
    return output_path


def run_watch_cli(argv: list[str] | None = None) -> int:
    """CLI entry point for formimporter watch command."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="formimporter-watch",
        description="Check FormImporter defect status against latest NuGet version",
    )
    parser.add_argument(
        "--run-repro",
        action="store_true",
        help="Run repro harness if version has advanced beyond defect version",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON report to this path (default: workspace/verification/latest/formimporter-watch-report.json)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Root of the repo (default: current directory)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    repo_root = args.repo_root.resolve()
    result = check_formimporter(repo_root, run_repro=args.run_repro)

    # Print summary
    print(f"FormImporter Watch — {result.checked_at}")
    print(f"  Installed: {result.current_version or 'unknown'}")
    print(f"  NuGet latest: {result.latest_nuget_version or 'unknown'}")
    print(f"  Defect version: {result.defect_version}")
    print(f"  Version advanced: {result.version_advanced}")
    print(f"  Verdict: {result.verdict}")
    for note in result.notes:
        print(f"  NOTE: {note}")

    output = args.output
    if output is None:
        output = repo_root / "workspace" / "verification" / "latest" / "formimporter-watch-report.json"

    write_watch_report(result, output)
    print(f"Report written: {output}")

    return 0 if result.verdict in ("RETEST_PASSED", "STILL_BLOCKED", "CHECK_ONLY") else 1


if __name__ == "__main__":
    sys.exit(run_watch_cli())
