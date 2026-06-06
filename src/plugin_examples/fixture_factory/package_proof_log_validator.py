"""
Package Proof Log Validators (PPL-01..PPL-03)

PPL-01: Each proven package in the bundle must have a restore.log
PPL-02: Each proven package in the bundle must have a build.log
PPL-03: Each proven package in the bundle must have a run.log
"""

import zipfile
from dataclasses import dataclass, field


@dataclass
class PPLResult:
    rule_id: str
    status: str  # "PASS" | "FAIL"
    message: str
    details: dict = field(default_factory=dict)


def _find_package_log(names: set[str], family: str, slug: str, log_name: str) -> bool:
    """Return True if any bundle entry ends with {family}/{slug}/{log_name}."""
    suffix = f"{family}/{slug}/{log_name}"
    return any(n.endswith(suffix) for n in names)


def _check_log_for_all_packages(
    bundle_path: str, proven_packages: list[dict], log_name: str, rule_id: str
) -> PPLResult:
    try:
        with zipfile.ZipFile(bundle_path) as zf:
            names = set(zf.namelist())
    except Exception as e:
        return PPLResult(
            rule_id=rule_id,
            status="FAIL",
            message=f"Could not open bundle: {e}",
            details={"bundle_path": bundle_path},
        )

    missing = []
    for pkg in proven_packages:
        fam = pkg.get("family", "")
        slug = pkg.get("slug", "")
        if not _find_package_log(names, fam, slug, log_name):
            missing.append(f"{fam}/{slug}")

    if missing:
        return PPLResult(
            rule_id=rule_id,
            status="FAIL",
            message=f"{len(missing)} proven package(s) missing {log_name} in bundle",
            details={"missing": missing, "log_name": log_name},
        )
    return PPLResult(
        rule_id=rule_id,
        status="PASS",
        message=f"All {len(proven_packages)} proven packages have {log_name} in bundle",
        details={"total_checked": len(proven_packages), "log_name": log_name},
    )


def ppl_01_restore_log_present(bundle_path: str, proven_packages: list[dict]) -> PPLResult:
    """PPL-01: Each proven package must have restore.log in the bundle."""
    return _check_log_for_all_packages(bundle_path, proven_packages, "restore.log", "PPL-01")


def ppl_02_build_log_present(bundle_path: str, proven_packages: list[dict]) -> PPLResult:
    """PPL-02: Each proven package must have build.log in the bundle."""
    return _check_log_for_all_packages(bundle_path, proven_packages, "build.log", "PPL-02")


def ppl_03_run_log_present(bundle_path: str, proven_packages: list[dict]) -> PPLResult:
    """PPL-03: Each proven package must have run.log in the bundle."""
    return _check_log_for_all_packages(bundle_path, proven_packages, "run.log", "PPL-03")


def run_all_ppl(bundle_path: str, proven_packages: list[dict]) -> list[PPLResult]:
    return [
        ppl_01_restore_log_present(bundle_path, proven_packages),
        ppl_02_build_log_present(bundle_path, proven_packages),
        ppl_03_run_log_present(bundle_path, proven_packages),
    ]
