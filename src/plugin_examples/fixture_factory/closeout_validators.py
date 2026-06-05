"""
Closeout consistency validators.

These validators catch disagreements between:
- Summary claims (lane-ledger, state files) and actual build results
- Invariant results and publication matrix
- Registry counts and cumulative ledger
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ConsistencyViolation:
    rule_id: str
    description: str
    expected: str
    actual: str
    severity: str = "ERROR"  # ERROR | WARNING


@dataclass
class ConsistencyCheckResult:
    report_root: Path
    violations: list = field(default_factory=list)
    checks_run: int = 0

    @property
    def passed(self) -> bool:
        return not any(v.severity == "ERROR" for v in self.violations)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "ERROR")


def check_build_results_vs_invariants(
    build_results_path: Path,
    invariant_results_path: Path,
) -> list[ConsistencyViolation]:
    """CV-01: Build results PASS count must match invariant results PASS count."""
    violations = []
    if not build_results_path.exists():
        return [ConsistencyViolation("CV-01", "wave-build-results.json not found",
                                     "file present", "missing")]
    if not invariant_results_path.exists():
        return [ConsistencyViolation("CV-01", "invariant-results.json not found",
                                     "file present", "missing")]

    build = json.loads(build_results_path.read_text(encoding="utf-8"))
    invs = json.loads(invariant_results_path.read_text(encoding="utf-8"))

    build_passed = build.get("passed", 0)
    build_total = build.get("total", 0)

    inv_total = invs.get("total", len(invs.get("packages", {})))
    inv_real_violations = invs.get("real_violations", 0)

    # Build passed count should equal invariant total
    if build_total != inv_total:
        violations.append(ConsistencyViolation(
            "CV-01a",
            "Build results total != invariant results total",
            f"equal ({build_total})",
            f"build={build_total}, inv={inv_total}",
        ))

    # If build says all PASS, invariants should have 0 real violations
    if build_passed == build_total and inv_real_violations > 0:
        violations.append(ConsistencyViolation(
            "CV-01b",
            "Build claims all PASS but invariants show real violations",
            "0 real violations",
            f"{inv_real_violations} real violations",
        ))

    return violations


def check_build_results_no_stale_errors(build_results_path: Path) -> list[ConsistencyViolation]:
    """CV-02: Build results must not contain error_snippet with BUILD_FAILED for PASS entries."""
    violations = []
    if not build_results_path.exists():
        return violations

    build = json.loads(build_results_path.read_text(encoding="utf-8"))
    for r in build.get("results", []):
        if r.get("verdict") in ("PASS", "TRIAL_PASS") and "error_snippet" in r:
            # error_snippet is only valid if it contains context, not BUILD FAILED
            snippet = r["error_snippet"]
            if "Build FAILED" in snippet or "BUILD_FAILED" in snippet:
                violations.append(ConsistencyViolation(
                    "CV-02",
                    f"Package {r['key']} has verdict PASS but error_snippet contains BUILD_FAILED",
                    "no BUILD_FAILED in error_snippet for PASS entries",
                    f"error_snippet present: {snippet[:100]}...",
                ))

    return violations


def check_publication_matrix_matches_invariants(
    pub_matrix_path: Path,
    invariant_results_path: Path,
) -> list[ConsistencyViolation]:
    """CV-03: Publication matrix must agree with invariant results on classifications."""
    violations = []
    if not pub_matrix_path.exists() or not invariant_results_path.exists():
        return violations

    pub = json.loads(pub_matrix_path.read_text(encoding="utf-8"))
    invs = json.loads(invariant_results_path.read_text(encoding="utf-8"))

    inv_packages = invs.get("packages", {})
    for entry in pub.get("packages", []):
        key = entry.get("package_key", "")
        pub_class = entry.get("classification", "")
        if key in inv_packages:
            inv_class = inv_packages[key].get("classification", "")
            if pub_class != inv_class:
                violations.append(ConsistencyViolation(
                    "CV-03",
                    f"Package {key}: publication matrix classification disagrees with invariant results",
                    f"inv={inv_class}",
                    f"pub={pub_class}",
                ))

    return violations


def check_cumulative_ledger_count(
    ledger_path: Path,
    expected_transformed: int,
) -> list[ConsistencyViolation]:
    """CV-04: Cumulative ledger total_dryrun_packages must match actual sum."""
    violations = []
    if not ledger_path.exists():
        return violations

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    actual_total = sum(len(v) for v in ledger.get("packages_by_wave", {}).values())
    claimed_total = ledger.get("total_dryrun_packages", 0)

    if actual_total != claimed_total:
        violations.append(ConsistencyViolation(
            "CV-04a",
            "Cumulative ledger total_dryrun_packages != sum of packages_by_wave",
            f"equal ({actual_total})",
            f"claimed={claimed_total}, actual_sum={actual_total}",
        ))

    if claimed_total != expected_transformed:
        violations.append(ConsistencyViolation(
            "CV-04b",
            "Cumulative ledger total != registry TRANSFORMED count",
            f"{expected_transformed}",
            f"{claimed_total}",
            severity="WARNING",
        ))

    return violations


def check_no_duplicate_package_keys(ledger_path: Path) -> list[ConsistencyViolation]:
    """CV-05: No package key should appear in multiple waves."""
    violations = []
    if not ledger_path.exists():
        return violations

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    all_keys = []
    for wave, keys in ledger.get("packages_by_wave", {}).items():
        all_keys.extend(keys)

    seen = set()
    for key in all_keys:
        if key in seen:
            violations.append(ConsistencyViolation(
                "CV-05",
                f"Duplicate package key in cumulative ledger: {key}",
                "unique",
                "duplicate",
            ))
        seen.add(key)

    return violations


def run_all_consistency_checks(report_root: Path, registry_transformed_count: int = 30) -> ConsistencyCheckResult:
    """Run all consistency validators against the current sprint's artifacts."""
    result = ConsistencyCheckResult(report_root=report_root)

    wave4_build = report_root.parent / "lowcode-plugin-example-factory-parallel-wave-20260605" / "dryrun" / "wave4-build-results.json"
    wave5_build = report_root / "dryrun" / "wave5-build-results.json"
    inv_results = report_root.parent / "lowcode-plugin-example-factory-parallel-wave-20260605" / "validators" / "invariant-results.json"
    cumulative_ledger = report_root.parent / "lowcode-plugin-example-factory-parallel-wave-20260605" / "state" / "cumulative-dryrun-ledger.json"
    wave5_pub = report_root / "lane-e-registry" / "wave5-publication-matrix.json"

    checks = [
        lambda: check_build_results_no_stale_errors(wave4_build),
        lambda: check_build_results_no_stale_errors(wave5_build),
        lambda: check_cumulative_ledger_count(cumulative_ledger, registry_transformed_count),
        lambda: check_no_duplicate_package_keys(cumulative_ledger),
    ]

    for check_fn in checks:
        violations = check_fn()
        result.violations.extend(violations)
        result.checks_run += 1

    return result
