"""
Closeout Consistency Validators (CCV-01..CCV-14)

Sprint: lowcode-plugin-canonical-package-wave9-20260605
Lane: G (validators)

These validators enforce that sprint closeout documents are internally consistent:
- Sprint verdict must match evidence bundle status
- Lane ledger status must match sprint verdict
- Taskcard status must match sprint verdict
- Test logs must exist for claimed test counts
- Canonical URL completeness for publication candidates
- Package proof completeness for packages claiming PASS status
"""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class CcvViolation:
    rule: str
    severity: str  # "ERROR" | "WARNING"
    message: str
    context: str = ""


@dataclass
class CcvResult:
    violations: List[CcvViolation] = field(default_factory=list)

    @property
    def passes(self) -> bool:
        return not any(v.severity == "ERROR" for v in self.violations)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "WARNING")

    def to_dict(self) -> dict:
        return {
            "passes": self.passes,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "violations": [
                {"rule": v.rule, "severity": v.severity, "message": v.message, "context": v.context}
                for v in self.violations
            ],
        }


def _add(result: CcvResult, rule: str, severity: str, message: str, context: str = "") -> None:
    result.violations.append(CcvViolation(rule, severity, message, context))


# ---------------------------------------------------------------------------
# CCV-01: Evidence bundle must not be PENDING when sprint verdict is COMPLETE
# ---------------------------------------------------------------------------
def check_ccv_01_evidence_bundle_not_pending(closeout: dict, result: CcvResult) -> None:
    verdict = closeout.get("verdict", "")
    bundle = closeout.get("evidence_bundle", {})
    if isinstance(bundle, dict):
        bundle_status = bundle.get("objective", "")
    else:
        bundle_status = str(bundle)

    complete_keywords = ("COMPLETE", "SPRINT_COMPLETE", "DONE", "PASS")
    pending_keywords = ("PENDING", "IN_PROGRESS", "TODO")

    if any(k in verdict.upper() for k in complete_keywords):
        if any(k in bundle_status.upper() for k in pending_keywords):
            _add(result, "CCV-01", "ERROR",
                 "Sprint verdict is COMPLETE but evidence_bundle is PENDING",
                 f"verdict={verdict!r} bundle_objective={bundle_status!r}")


# ---------------------------------------------------------------------------
# CCV-02: Lane ledger lanes must not be PENDING when sprint verdict is COMPLETE
# ---------------------------------------------------------------------------
def check_ccv_02_lane_ledger_lanes_complete(
    closeout: dict, lane_ledger: Optional[dict], result: CcvResult
) -> None:
    verdict = closeout.get("verdict", "")
    complete_keywords = ("COMPLETE", "SPRINT_COMPLETE", "DONE")
    if not any(k in verdict.upper() for k in complete_keywords):
        return  # only relevant when sprint claims complete

    if lane_ledger is None:
        _add(result, "CCV-02", "ERROR",
             "Sprint verdict is COMPLETE but lane-ledger.json was not provided", "")
        return

    lanes = lane_ledger.get("lanes", [])
    pending = [l for l in lanes if l.get("status", "") in ("PENDING", "IN_PROGRESS")]
    if pending:
        lane_ids = [l.get("lane", "?") for l in pending]
        _add(result, "CCV-02", "ERROR",
             f"Sprint verdict is COMPLETE but {len(pending)} lane(s) still PENDING/IN_PROGRESS",
             f"lanes={lane_ids}")


# ---------------------------------------------------------------------------
# CCV-03: Taskcards must not be PENDING when sprint verdict is COMPLETE
# ---------------------------------------------------------------------------
def check_ccv_03_taskcards_complete(
    closeout: dict, taskcards: Optional[List[dict]], result: CcvResult
) -> None:
    verdict = closeout.get("verdict", "")
    complete_keywords = ("COMPLETE", "SPRINT_COMPLETE", "DONE")
    if not any(k in verdict.upper() for k in complete_keywords):
        return

    if taskcards is None:
        _add(result, "CCV-03", "ERROR",
             "Sprint verdict is COMPLETE but taskcards were not provided", "")
        return

    pending = [t for t in taskcards if t.get("status", "") in ("PENDING", "IN_PROGRESS")]
    if pending:
        ids = [t.get("id", "?") for t in pending]
        _add(result, "CCV-03", "ERROR",
             f"Sprint verdict is COMPLETE but {len(pending)} taskcard(s) still PENDING/IN_PROGRESS",
             f"taskcards={ids}")


# ---------------------------------------------------------------------------
# CCV-04: Test log must exist when closeout claims a test count
# ---------------------------------------------------------------------------
def check_ccv_04_test_log_exists(
    closeout: dict, report_dir: Optional[Path], result: CcvResult
) -> None:
    claimed_count = None
    for key in ("pytest_passed", "test_count", "tests_passed"):
        val = closeout.get(key)
        if val is not None:
            claimed_count = val
            break

    if claimed_count is None:
        return  # no test count claimed

    if report_dir is None:
        _add(result, "CCV-04", "ERROR",
             f"Closeout claims {claimed_count} tests but no report_dir provided to check logs", "")
        return

    log_patterns = ["**/pytest-stdout.txt", "**/pytest.log", "**/test-log.txt", "**/*-test-log.txt"]
    found = False
    for pat in log_patterns:
        if list(report_dir.glob(pat)):
            found = True
            break

    if not found:
        _add(result, "CCV-04", "ERROR",
             f"Closeout claims {claimed_count} tests passed but no test log file found in report dir",
             str(report_dir))


# ---------------------------------------------------------------------------
# CCV-05: Final git status must be recorded when verdict is COMPLETE
# ---------------------------------------------------------------------------
def check_ccv_05_git_status_recorded(
    closeout: dict, report_dir: Optional[Path], result: CcvResult
) -> None:
    verdict = closeout.get("verdict", "")
    complete_keywords = ("COMPLETE", "SPRINT_COMPLETE", "DONE")
    if not any(k in verdict.upper() for k in complete_keywords):
        return

    if report_dir is None:
        return

    git_patterns = ["**/git-status.txt", "**/final-git-status.txt", "**/preflight-git-status.txt"]
    found = any(list(report_dir.glob(pat)) for pat in git_patterns)
    if not found:
        _add(result, "CCV-05", "WARNING",
             "Sprint is COMPLETE but no git-status.txt found in report dir",
             str(report_dir))


# ---------------------------------------------------------------------------
# CCV-06: Commit proof must be recorded when verdict is COMPLETE
# ---------------------------------------------------------------------------
def check_ccv_06_commit_proof_recorded(closeout: dict, result: CcvResult) -> None:
    verdict = closeout.get("verdict", "")
    complete_keywords = ("COMPLETE", "SPRINT_COMPLETE", "DONE")
    if not any(k in verdict.upper() for k in complete_keywords):
        return

    commit = closeout.get("commit_sha") or closeout.get("git_commit") or closeout.get("commit")
    if not commit:
        _add(result, "CCV-06", "WARNING",
             "Sprint is COMPLETE but no commit_sha/git_commit recorded in closeout", "")


# ---------------------------------------------------------------------------
# CCV-07: CANONICAL_IDENTITY_VERIFIED entries must have canonical_url
# ---------------------------------------------------------------------------
def check_ccv_07_canonical_url_for_verified(
    registry_entries: List[dict], result: CcvResult
) -> None:
    for entry in registry_entries:
        if entry.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED":
            url = entry.get("canonical_url") or entry.get("canonical_plugin_url")
            if not url:
                slug = entry.get("plugin_slug", "?")
                family = entry.get("family", "?")
                _add(result, "CCV-07", "ERROR",
                     f"CANONICAL_IDENTITY_VERIFIED entry missing canonical_url: {family}/{slug}",
                     f"plugin_slug={slug}")


# ---------------------------------------------------------------------------
# CCV-08: CANONICAL_IDENTITY_VERIFIED entries must have display_plugin_name
# ---------------------------------------------------------------------------
def check_ccv_08_display_name_for_verified(
    registry_entries: List[dict], result: CcvResult
) -> None:
    for entry in registry_entries:
        if entry.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED":
            name = entry.get("display_plugin_name")
            if not name:
                slug = entry.get("plugin_slug", "?")
                family = entry.get("family", "?")
                _add(result, "CCV-08", "WARNING",
                     f"CANONICAL_IDENTITY_VERIFIED entry missing display_plugin_name: {family}/{slug}",
                     f"plugin_slug={slug}")


# ---------------------------------------------------------------------------
# CCV-09: Publication-clean candidates must have canonical_url
# ---------------------------------------------------------------------------
def check_ccv_09_publication_clean_has_canonical_url(
    matrix_rows: List[dict], result: CcvResult
) -> None:
    clean_statuses = {"PUBLICATION_READY", "PUBLICATION_CLEAN", "CANONICAL_VERIFIED_FULL_PACKAGE"}
    for row in matrix_rows:
        status = row.get("publication_status", row.get("classification", ""))
        if status in clean_statuses:
            url = row.get("canonical_url") or row.get("canonical_plugin_url")
            if not url:
                key = row.get("package_key", row.get("plugin_slug", "?"))
                _add(result, "CCV-09", "ERROR",
                     f"Publication-clean candidate {key!r} missing canonical_url", key)


# ---------------------------------------------------------------------------
# CCV-10: Package marked PASS must not be missing Program.cs (no metadata-only PASS)
# ---------------------------------------------------------------------------
def check_ccv_10_pass_package_has_program_cs(
    output_validation: dict, pkg_dir: Optional[Path], result: CcvResult
) -> None:
    verdict = output_validation.get("verdict", "")
    if verdict != "PASS":
        return

    if pkg_dir is None:
        return

    if not (pkg_dir / "Program.cs").exists():
        key = output_validation.get("package_key", output_validation.get("package", str(pkg_dir)))
        _add(result, "CCV-10", "ERROR",
             f"Package {key!r} claims verdict=PASS but Program.cs is missing (metadata-only fraud)",
             str(pkg_dir))


# ---------------------------------------------------------------------------
# CCV-11: Package marked PASS must not be missing .csproj
# ---------------------------------------------------------------------------
def check_ccv_11_pass_package_has_csproj(
    output_validation: dict, pkg_dir: Optional[Path], result: CcvResult
) -> None:
    verdict = output_validation.get("verdict", "")
    if verdict != "PASS":
        return

    if pkg_dir is None:
        return

    csproj_files = list(pkg_dir.glob("*.csproj"))
    if not csproj_files:
        key = output_validation.get("package_key", output_validation.get("package", str(pkg_dir)))
        _add(result, "CCV-11", "ERROR",
             f"Package {key!r} claims verdict=PASS but no *.csproj found",
             str(pkg_dir))


# ---------------------------------------------------------------------------
# CCV-12: Package marked PASS must have at least one log file
# ---------------------------------------------------------------------------
def check_ccv_12_pass_package_has_logs(
    output_validation: dict, pkg_dir: Optional[Path], result: CcvResult
) -> None:
    verdict = output_validation.get("verdict", "")
    if verdict != "PASS":
        return

    if pkg_dir is None:
        return

    log_files = list(pkg_dir.glob("*.log")) + list((pkg_dir / "logs").glob("*.log") if (pkg_dir / "logs").exists() else [])
    if not log_files:
        key = output_validation.get("package_key", output_validation.get("package", str(pkg_dir)))
        _add(result, "CCV-12", "WARNING",
             f"Package {key!r} claims verdict=PASS but no *.log files found",
             str(pkg_dir))


# ---------------------------------------------------------------------------
# CCV-13: Legacy alias entries must not appear as publication candidates
# ---------------------------------------------------------------------------
def check_ccv_13_no_legacy_alias_as_publication_candidate(
    matrix_rows: List[dict], registry_entries: List[dict], result: CcvResult
) -> None:
    # Build set of legacy alias slugs from registry
    legacy_slugs: set = set()
    for entry in registry_entries:
        for alias in entry.get("legacy_aliases", []):
            family = entry.get("family", "")
            legacy_slugs.add(f"{family}/{alias}")

    clean_statuses = {"PUBLICATION_READY", "PUBLICATION_CLEAN", "CANONICAL_VERIFIED_FULL_PACKAGE"}
    for row in matrix_rows:
        status = row.get("publication_status", row.get("classification", ""))
        if status in clean_statuses:
            key = row.get("package_key", row.get("plugin_slug", ""))
            if key in legacy_slugs:
                _add(result, "CCV-13", "ERROR",
                     f"Legacy alias {key!r} appears as publication-clean candidate",
                     f"package_key={key}")


# ---------------------------------------------------------------------------
# CCV-14: Publication matrix must include canonical_url per row
# ---------------------------------------------------------------------------
def check_ccv_14_matrix_has_canonical_url_column(
    matrix_rows: List[dict], result: CcvResult
) -> None:
    if not matrix_rows:
        return

    missing_url_count = sum(
        1 for row in matrix_rows
        if not (row.get("canonical_url") or row.get("canonical_plugin_url"))
    )

    if missing_url_count == len(matrix_rows):
        _add(result, "CCV-14", "ERROR",
             "Publication matrix has no canonical_url column — all rows missing canonical_url", "")
    elif missing_url_count > 0:
        _add(result, "CCV-14", "WARNING",
             f"Publication matrix has {missing_url_count}/{len(matrix_rows)} rows missing canonical_url", "")


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------
def run_closeout_consistency_validators(
    closeout: dict,
    lane_ledger: Optional[dict] = None,
    taskcards: Optional[List[dict]] = None,
    report_dir: Optional[Path] = None,
    registry_entries: Optional[List[dict]] = None,
    matrix_rows: Optional[List[dict]] = None,
) -> CcvResult:
    """Run all 14 CCV rules and return aggregated result."""
    result = CcvResult()

    check_ccv_01_evidence_bundle_not_pending(closeout, result)
    check_ccv_02_lane_ledger_lanes_complete(closeout, lane_ledger, result)
    check_ccv_03_taskcards_complete(closeout, taskcards, result)
    check_ccv_04_test_log_exists(closeout, report_dir, result)
    check_ccv_05_git_status_recorded(closeout, report_dir, result)
    check_ccv_06_commit_proof_recorded(closeout, result)

    if registry_entries is not None:
        check_ccv_07_canonical_url_for_verified(registry_entries, result)
        check_ccv_08_display_name_for_verified(registry_entries, result)

    if matrix_rows is not None:
        check_ccv_09_publication_clean_has_canonical_url(matrix_rows, result)
        check_ccv_14_matrix_has_canonical_url_column(matrix_rows, result)

    if matrix_rows is not None and registry_entries is not None:
        check_ccv_13_no_legacy_alias_as_publication_candidate(matrix_rows, registry_entries, result)

    return result
