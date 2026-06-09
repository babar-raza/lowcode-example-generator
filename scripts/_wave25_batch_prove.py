"""Wave 25 — Lane E: Batch prove DRYRUN packages.

Derives the backlog dynamically from registry YAMLs (never hardcoded).
Attempts restore → build → run for each DRYRUN package.
Records exact blocker classes per package.
Updates registry status for PASS packages only.

Usage:
    python scripts/_wave25_batch_prove.py [--dry-run] [--family FAMILY]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

REGISTRY_DIR = Path("pipeline/plugin-code-registry/family")
REPORT_DIR = Path("reports/lowcode-plugin-production-heal-wave25-20260609/generation")
EXAMPLES_ROOT = Path("examples")
DATE = "2026-06-09"
WAVE = "wave25"

BLOCKER_CLASSES = {
    "scaffold_missing": "SCAFFOLD_NOT_FOUND",
    "restore": "RESTORE_FAILED",
    "build": "BUILD_FAILED",
    "run": "RUN_FAILED",
    "output_empty": "OUTPUT_VALIDATION_FAILED",
    "fixture_missing": "FIXTURE_BLOCKED",
    "net_framework": "TARGET_FRAMEWORK_BLOCKED",
    "license_restriction": "LICENSE_BLOCKED",
    "network_required": "EXTERNAL_NETWORK_BLOCKED",
}

# Known pre-existing blockers from MEMORY.md
KNOWN_BLOCKERS: dict[str, str] = {
    "omr/generate-omr-template": "TARGET_FRAMEWORK_BLOCKED",   # net8.0 not supported
    "omr/recognize-omr": "TARGET_FRAMEWORK_BLOCKED",
    "font/render-text-with-font": "LICENSE_BLOCKED",            # Arial triggers LicenseRestrictionException
}


@dataclass
class DryRunEntry:
    family: str
    slug: str
    pkg_path: str | None
    status: str = "PENDING"
    blocker_class: str | None = None


@dataclass
class PackageResult:
    family: str
    slug: str
    pkg_path: str | None
    build_status: str       # BUILD_PASS | BUILD_FAIL_* | SCAFFOLD_NOT_FOUND | SKIPPED
    restore_exit: int | None = None
    build_exit: int | None = None
    run_exit: int | None = None
    output_files: list[str] = field(default_factory=list)
    blocker_class: str | None = None
    repair_applied: bool = False
    log_path: str | None = None
    known_blocker: bool = False


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_dryrun_backlog(family_filter: str | None = None) -> list[DryRunEntry]:
    """Scan registry YAMLs at runtime. Never hardcodes the count."""
    backlog: list[DryRunEntry] = []
    for family_yaml in sorted(REGISTRY_DIR.glob("*.yaml")):
        data = yaml.safe_load(family_yaml.read_text(encoding="utf-8"))
        family = data.get("family", family_yaml.stem)
        if family_filter and family != family_filter:
            continue
        for plugin in data.get("plugins", []):
            if plugin.get("registry_status") == "TRANSFORMED_TO_EXAMPLE_DRYRUN":
                slug = plugin.get("plugin_slug", "")
                pkg_path = _find_package_dir(family, slug)
                backlog.append(DryRunEntry(
                    family=family,
                    slug=slug,
                    pkg_path=pkg_path,
                ))
    return backlog


def _find_package_dir(family: str, slug: str) -> str | None:
    """Find the package directory if scaffold exists."""
    candidates = [
        EXAMPLES_ROOT / family / slug,
        Path(f"workspace/{family}/{slug}"),
        Path(f".local/{family}/{slug}"),
    ]
    for c in candidates:
        if c.exists() and any(c.glob("*.csproj")):
            return str(c)
    return None


def _attempt_build(entry: DryRunEntry, log_dir: Path, dry_run: bool = False) -> PackageResult:
    """Attempt restore → build → run for a single package."""
    family_slug = f"{entry.family}/{entry.slug}"
    log_path = log_dir / f"{entry.family}_{entry.slug}.log"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Check known pre-existing blockers first
    if family_slug in KNOWN_BLOCKERS:
        reason = KNOWN_BLOCKERS[family_slug]
        return PackageResult(
            family=entry.family, slug=entry.slug, pkg_path=entry.pkg_path,
            build_status=f"BUILD_FAIL_{reason}", blocker_class=reason,
            known_blocker=True, log_path=str(log_path),
        )

    # Check scaffold exists
    if not entry.pkg_path:
        return PackageResult(
            family=entry.family, slug=entry.slug, pkg_path=None,
            build_status="SCAFFOLD_NOT_FOUND",
            blocker_class=BLOCKER_CLASSES["scaffold_missing"],
            log_path=str(log_path),
        )

    if dry_run:
        return PackageResult(
            family=entry.family, slug=entry.slug, pkg_path=entry.pkg_path,
            build_status="DRY_RUN_SKIPPED",
            log_path=str(log_path),
        )

    pkg_dir = Path(entry.pkg_path)

    # Find .csproj
    csproj_files = list(pkg_dir.glob("*.csproj"))
    if not csproj_files:
        return PackageResult(
            family=entry.family, slug=entry.slug, pkg_path=entry.pkg_path,
            build_status="BUILD_FAIL_NO_CSPROJ",
            blocker_class=BLOCKER_CLASSES["scaffold_missing"],
            log_path=str(log_path),
        )

    csproj = str(csproj_files[0])

    # dotnet restore
    restore_result = subprocess.run(
        ["dotnet", "restore", csproj],
        capture_output=True, text=True, cwd=pkg_dir,
    )
    log_path.write_text(
        f"=== RESTORE ===\n{restore_result.stdout}\n{restore_result.stderr}\n",
        encoding="utf-8",
    )

    if restore_result.returncode != 0:
        return PackageResult(
            family=entry.family, slug=entry.slug, pkg_path=entry.pkg_path,
            build_status="BUILD_FAIL_RESTORE",
            restore_exit=restore_result.returncode,
            blocker_class=BLOCKER_CLASSES["restore"],
            log_path=str(log_path),
        )

    # dotnet build
    build_result = subprocess.run(
        ["dotnet", "build", csproj, "--no-restore", "-c", "Release"],
        capture_output=True, text=True, cwd=pkg_dir,
    )
    with open(log_path, "a", encoding="utf-8") as lf:
        lf.write(f"\n=== BUILD ===\n{build_result.stdout}\n{build_result.stderr}\n")

    if build_result.returncode != 0:
        blocker = BLOCKER_CLASSES["build"]
        # Detect common known failures
        stderr_combined = build_result.stdout + build_result.stderr
        if "net8.0" in stderr_combined or "net6.0" in stderr_combined:
            blocker = BLOCKER_CLASSES["net_framework"]
        return PackageResult(
            family=entry.family, slug=entry.slug, pkg_path=entry.pkg_path,
            build_status="BUILD_FAIL_BUILD",
            restore_exit=restore_result.returncode,
            build_exit=build_result.returncode,
            blocker_class=blocker,
            log_path=str(log_path),
        )

    # dotnet run
    run_result = subprocess.run(
        ["dotnet", "run", "--project", csproj, "--no-build", "-c", "Release"],
        capture_output=True, text=True, cwd=pkg_dir,
        timeout=120,
    )
    with open(log_path, "a", encoding="utf-8") as lf:
        lf.write(f"\n=== RUN ===\n{run_result.stdout}\n{run_result.stderr}\n")

    output_files = _find_output_files(pkg_dir)

    if run_result.returncode != 0:
        return PackageResult(
            family=entry.family, slug=entry.slug, pkg_path=entry.pkg_path,
            build_status="BUILD_FAIL_RUN",
            restore_exit=restore_result.returncode,
            build_exit=build_result.returncode,
            run_exit=run_result.returncode,
            output_files=output_files,
            blocker_class=BLOCKER_CLASSES["run"],
            log_path=str(log_path),
        )

    if not output_files:
        return PackageResult(
            family=entry.family, slug=entry.slug, pkg_path=entry.pkg_path,
            build_status="BUILD_FAIL_NO_OUTPUT",
            restore_exit=restore_result.returncode,
            build_exit=build_result.returncode,
            run_exit=run_result.returncode,
            output_files=[],
            blocker_class=BLOCKER_CLASSES["output_empty"],
            log_path=str(log_path),
        )

    return PackageResult(
        family=entry.family, slug=entry.slug, pkg_path=entry.pkg_path,
        build_status="BUILD_PASS",
        restore_exit=restore_result.returncode,
        build_exit=build_result.returncode,
        run_exit=run_result.returncode,
        output_files=output_files,
        blocker_class=None,
        log_path=str(log_path),
    )


def _find_output_files(pkg_dir: Path) -> list[str]:
    """Find output files produced by the run."""
    output_exts = {
        ".pdf", ".png", ".jpg", ".jpeg", ".svg", ".xlsx", ".docx",
        ".csv", ".html", ".zip", ".json", ".txt", ".glb", ".3ds", ".fbx",
    }
    results = []
    for f in pkg_dir.rglob("*"):
        if f.is_file() and f.suffix.lower() in output_exts:
            # Skip source files
            if "bin" in f.parts or "obj" in f.parts or f.name.endswith(".csproj"):
                continue
            results.append(str(f))
    return results[:10]  # cap


def update_registry_status(family: str, slug: str, new_status: str, wave: str, proven_at: str) -> None:
    """Update a single plugin's registry_status to new_status."""
    yaml_path = REGISTRY_DIR / f"{family}.yaml"
    if not yaml_path.exists():
        return
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    for plugin in data.get("plugins", []):
        if plugin.get("plugin_slug") == slug:
            plugin["registry_status"] = new_status
            plugin["proven_wave"] = wave
            plugin["proven_at"] = proven_at
            break
    yaml_path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Wave 25 DRYRUN batch prove")
    parser.add_argument("--dry-run", action="store_true", help="Validate scaffold existence only")
    parser.add_argument("--family", help="Limit to a specific family")
    args = parser.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    log_dir = REPORT_DIR / "build-logs"

    print("=== Wave 25 — Lane E: DRYRUN Batch Prove ===")

    # Step 1: Derive backlog dynamically
    backlog = build_dryrun_backlog(family_filter=args.family)
    print(f"[LE] Backlog derived from registry: {len(backlog)} packages")

    # Write dryrun-backlog.json as FIRST evidence artifact (before any building)
    backlog_doc = {
        "sprint": "lowcode-plugin-production-heal-wave25-20260609",
        "date": DATE,
        "generated_at": _utcnow(),
        "source": "registry YAMLs scanned at runtime (not hardcoded)",
        "total_dryrun_packages": len(backlog),
        "packages": [
            {
                "family": e.family,
                "slug": e.slug,
                "pkg_path": e.pkg_path,
                "status": "PENDING",
            }
            for e in backlog
        ],
    }
    backlog_path = REPORT_DIR / "dryrun-backlog.json"
    backlog_path.write_text(json.dumps(backlog_doc, indent=2), encoding="utf-8")
    print(f"[LE] dryrun-backlog.json written: {backlog_path}")

    # Step 2: Attempt build per package
    results: list[PackageResult] = []
    for entry in backlog:
        print(f"[LE] Proving {entry.family}/{entry.slug}... ", end="", flush=True)
        result = _attempt_build(entry, log_dir, dry_run=args.dry_run)
        results.append(result)
        print(result.build_status)

    # Step 3: Write build-matrix.json
    matrix = {
        "sprint": "lowcode-plugin-production-heal-wave25-20260609",
        "date": DATE,
        "generated_at": _utcnow(),
        "total": len(results),
        "passed": sum(1 for r in results if r.build_status == "BUILD_PASS"),
        "failed": sum(1 for r in results if r.build_status.startswith("BUILD_FAIL")),
        "scaffold_missing": sum(1 for r in results if r.build_status == "SCAFFOLD_NOT_FOUND"),
        "dry_run_skipped": sum(1 for r in results if r.build_status == "DRY_RUN_SKIPPED"),
        "results": [asdict(r) for r in results],
    }
    matrix_path = REPORT_DIR / "build-matrix.json"
    matrix_path.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    print(f"[LE] build-matrix.json written: pass={matrix['passed']} fail={matrix['failed']} scaffold_missing={matrix['scaffold_missing']}")

    # Step 4: Update registry only for PASS
    transitions: list[dict] = []
    proven_at = DATE
    for result in results:
        if result.build_status == "BUILD_PASS":
            update_registry_status(result.family, result.slug, "CANONICAL_PACKAGE_PROVEN", WAVE, proven_at)
            transitions.append({
                "family": result.family,
                "slug": result.slug,
                "from_status": "TRANSFORMED_TO_EXAMPLE_DRYRUN",
                "to_status": "CANONICAL_PACKAGE_PROVEN",
                "wave": WAVE,
                "proven_at": proven_at,
            })
        elif result.blocker_class:
            transitions.append({
                "family": result.family,
                "slug": result.slug,
                "from_status": "TRANSFORMED_TO_EXAMPLE_DRYRUN",
                "to_status": "DRYRUN_BLOCKED",
                "blocker": result.blocker_class,
                "known_blocker": result.known_blocker,
                "wave": WAVE,
            })

    # Step 5: Write registry-transition-ledger.json
    ledger = {
        "sprint": "lowcode-plugin-production-heal-wave25-20260609",
        "date": DATE,
        "generated_at": _utcnow(),
        "wave": WAVE,
        "from_status": "TRANSFORMED_TO_EXAMPLE_DRYRUN",
        "total_transitions": len(transitions),
        "promoted_to_proven": sum(1 for t in transitions if t.get("to_status") == "CANONICAL_PACKAGE_PROVEN"),
        "blocked": sum(1 for t in transitions if t.get("to_status") == "DRYRUN_BLOCKED"),
        "transitions": transitions,
    }
    ledger_path = REPORT_DIR / "registry-transition-ledger.json"
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(f"[LE] registry-transition-ledger.json written: {ledger['promoted_to_proven']} promoted, {ledger['blocked']} blocked")

    print(f"[LE] Lane E COMPLETE")


if __name__ == "__main__":
    main()
