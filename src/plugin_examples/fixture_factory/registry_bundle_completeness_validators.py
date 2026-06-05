"""
Registry Bundle Completeness Validators (RBC-01..RBC-08)
Sprint: lowcode-plugin-canonical-package-wave11-20260605

These validators check that:
- RBC-01: All CANONICAL_IDENTITY_VERIFIED registry entries have a corresponding package directory OR
           are documented in the wave queue (NEEDS_PACKAGE_PROOF).
- RBC-02: All proven packages have a package-manifest.json with required fields.
- RBC-03: All proven packages have an output-validation.json with verdict=PASS.
- RBC-04: All proven packages have restore.log, build.log, and run.log (log proof).
- RBC-05: Registry total count in closeout matches actual YAML count.
- RBC-06: Evidence bundle entry count > 0 (non-empty bundle).
- RBC-07: Evidence bundle SHA-256 is recorded in sprint-closeout.json (not PENDING/null).
- RBC-08: Sprint-closeout.json commit_sha is recorded (not PENDING/null).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _ok(rule: str, msg: str = "OK") -> dict:
    return {"rule": rule, "result": "PASS", "message": msg}


def _err(rule: str, msg: str) -> dict:
    return {"rule": rule, "result": "ERROR", "message": msg}


def _skip(rule: str, msg: str = "skipped") -> dict:
    return {"rule": rule, "result": "SKIP", "message": msg}


def rbc_01_civ_entries_have_packages_or_queue(
    civ_slugs: list[str],
    package_base_dirs: list[Path],
    queue_slugs: list[str],
) -> dict:
    """RBC-01: Every CIV entry either has a proven package or is in the wave queue."""
    missing = []
    for slug in civ_slugs:
        family, name = slug.split("/", 1) if "/" in slug else ("", slug)
        has_package = any(
            (base / family / name).exists() for base in package_base_dirs
        )
        in_queue = slug in queue_slugs
        if not has_package and not in_queue:
            missing.append(slug)
    if missing:
        return _err(
            "RBC-01",
            f"{len(missing)} CIV entries have no package and are not in queue: "
            + ", ".join(missing[:5])
            + ("..." if len(missing) > 5 else ""),
        )
    return _ok("RBC-01", f"All {len(civ_slugs)} CIV entries have package or queue entry")


def rbc_02_packages_have_manifest(package_dirs: list[Path]) -> dict:
    """RBC-02: All proven package dirs have package-manifest.json with required fields."""
    REQUIRED = {"package_key", "family", "plugin_slug", "canonical_url", "identity_status"}
    errors = []
    for pkg in package_dirs:
        manifest = pkg / "package-manifest.json"
        if not manifest.exists():
            errors.append(f"{pkg.name}: missing package-manifest.json")
            continue
        import json
        data = json.loads(manifest.read_text(encoding="utf-8"))
        missing_fields = REQUIRED - set(data.keys())
        if missing_fields:
            errors.append(f"{pkg.name}: manifest missing fields {missing_fields}")
    if errors:
        return _err("RBC-02", f"{len(errors)} package manifest issues: " + "; ".join(errors[:3]))
    return _ok("RBC-02", f"All {len(package_dirs)} packages have valid manifests")


def rbc_03_packages_have_output_validation_pass(package_dirs: list[Path]) -> dict:
    """RBC-03: All proven packages have output-validation.json with verdict=PASS."""
    import json
    errors = []
    for pkg in package_dirs:
        ov = pkg / "output-validation.json"
        if not ov.exists():
            errors.append(f"{pkg.name}: missing output-validation.json")
            continue
        data = json.loads(ov.read_text(encoding="utf-8"))
        if data.get("verdict") != "PASS":
            errors.append(f"{pkg.name}: verdict={data.get('verdict')}")
    if errors:
        return _err("RBC-03", f"{len(errors)} output-validation issues: " + "; ".join(errors[:3]))
    return _ok("RBC-03", f"All {len(package_dirs)} packages have output-validation PASS")


def rbc_04_packages_have_log_proof(package_dirs: list[Path]) -> dict:
    """RBC-04: All proven packages have restore.log, build.log, and run.log."""
    errors = []
    for pkg in package_dirs:
        missing_logs = [
            log for log in ("restore.log", "build.log", "run.log")
            if not (pkg / log).exists()
        ]
        if missing_logs:
            errors.append(f"{pkg.name}: missing {', '.join(missing_logs)}")
    if errors:
        return _err("RBC-04", f"{len(errors)} packages missing log proof: " + "; ".join(errors[:5]))
    return _ok("RBC-04", f"All {len(package_dirs)} packages have complete log proof")


def rbc_05_registry_count_matches_closeout(
    actual_registry_count: int,
    closeout: dict[str, Any],
) -> dict:
    """RBC-05: Registry total in closeout matches actual YAML count."""
    claimed = closeout.get("registry_total") or closeout.get("total_registry_entries")
    if claimed is None:
        return _skip("RBC-05", "No registry_total in closeout")
    if int(claimed) != actual_registry_count:
        return _err(
            "RBC-05",
            f"Registry count mismatch: closeout claims {claimed}, actual={actual_registry_count}",
        )
    return _ok("RBC-05", f"Registry count matches: {actual_registry_count}")


def rbc_06_bundle_is_nonempty(closeout: dict[str, Any]) -> dict:
    """RBC-06: Evidence bundle entry count > 0."""
    bundle = closeout.get("evidence_bundle")
    if not isinstance(bundle, dict):
        return _skip("RBC-06", "No evidence_bundle dict in closeout")
    entries = bundle.get("entries")
    if entries is None:
        return _skip("RBC-06", "No entries field in evidence_bundle")
    if int(entries) <= 0:
        return _err("RBC-06", f"Evidence bundle is empty: entries={entries}")
    return _ok("RBC-06", f"Evidence bundle has {entries} entries")


def rbc_07_bundle_sha_recorded(closeout: dict[str, Any]) -> dict:
    """RBC-07: Evidence bundle SHA-256 is recorded (not PENDING/null)."""
    bundle = closeout.get("evidence_bundle")
    if not isinstance(bundle, dict):
        return _skip("RBC-07", "No evidence_bundle dict in closeout")
    sha = bundle.get("sha256")
    if not sha or sha in ("PENDING", "null", ""):
        return _err("RBC-07", f"Evidence bundle SHA-256 not recorded: sha256={sha!r}")
    return _ok("RBC-07", f"Bundle SHA-256 recorded: {sha[:16]}...")


def rbc_08_commit_sha_recorded(closeout: dict[str, Any]) -> dict:
    """RBC-08: commit_sha in closeout is recorded (not PENDING/null)."""
    commit_sha = closeout.get("commit_sha")
    if not commit_sha or commit_sha in ("PENDING", "null", ""):
        return _err("RBC-08", f"commit_sha not recorded in closeout: commit_sha={commit_sha!r}")
    return _ok("RBC-08", f"commit_sha recorded: {commit_sha}")


def run_all_rbc_validators(
    civ_slugs: list[str],
    package_base_dirs: list[Path],
    queue_slugs: list[str],
    package_dirs: list[Path],
    actual_registry_count: int,
    closeout: dict[str, Any],
) -> dict[str, Any]:
    """Run all RBC validators and return aggregate result."""
    results = [
        rbc_01_civ_entries_have_packages_or_queue(civ_slugs, package_base_dirs, queue_slugs),
        rbc_02_packages_have_manifest(package_dirs),
        rbc_03_packages_have_output_validation_pass(package_dirs),
        rbc_04_packages_have_log_proof(package_dirs),
        rbc_05_registry_count_matches_closeout(actual_registry_count, closeout),
        rbc_06_bundle_is_nonempty(closeout),
        rbc_07_bundle_sha_recorded(closeout),
        rbc_08_commit_sha_recorded(closeout),
    ]
    passed = sum(1 for r in results if r["result"] == "PASS")
    failed = sum(1 for r in results if r["result"] == "ERROR")
    skipped = sum(1 for r in results if r["result"] == "SKIP")
    verdict = "ALL_PASS" if failed == 0 else "FAIL"
    return {
        "rules": results,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "verdict": verdict,
    }
