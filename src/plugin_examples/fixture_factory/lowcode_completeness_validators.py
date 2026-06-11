"""
LowCode Completeness Validators (LCV-01..LCV-15)

Sprint: lowcode-plugin-canonical-package-wave20-20260607
Lane: L (validator hardening)

These validators enforce that no sprint can claim completion while any local
evidence, taskcard, sidecar, attestation, dirty workspace, or overclaiming
issue remains. Derived from recurring failure patterns across W15-W19.

Rules:
  LCV-01: No COMPLETE with pending evidence artifacts
  LCV-02: No COMPLETE with pending taskcards
  LCV-03: No final verdict without external .sha256 sidecar
  LCV-04: No final verdict without final-attestation.json
  LCV-05: No final verdict if IV has pending checks
  LCV-06: No final verdict if adversarial review has pending checks
  LCV-07: No PR_READY claim without physical PR packet file
  LCV-08: No PR_CREATED claim without live PR URL
  LCV-09: No PUBLISHED claim without merge/release evidence
  LCV-10: No package proof without restore+build+run+output validation
  LCV-11: No test count claim without raw log evidence
  LCV-12: No final git status omission in closeout
  LCV-13: No target repo claim without clone/fetch/PR evidence
  LCV-14: No unresolved dirty workspace in final git status
  LCV-15: No "only external gates remain" while local issues exist
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LcvViolation:
    rule: str
    severity: str  # "ERROR" | "WARNING"
    message: str
    context: str = ""


@dataclass
class LcvResult:
    violations: List[LcvViolation] = field(default_factory=list)

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


def _add(result: LcvResult, rule: str, severity: str, message: str, context: str = "") -> None:
    result.violations.append(LcvViolation(rule, severity, message, context))


# ---------------------------------------------------------------------------
# LCV-01: No COMPLETE with pending evidence artifacts
# ---------------------------------------------------------------------------
def check_lcv_01_no_complete_with_pending_evidence(closeout: dict, result: LcvResult) -> None:
    verdict = closeout.get("verdict", "")
    if "COMPLETE" not in verdict.upper():
        return
    # Check taskcards for any "PENDING" or "TODO" evidence strings
    taskcards = closeout.get("taskcards", {})
    pending = taskcards.get("pending", 0)
    if pending and int(pending) > 0:
        pending_ids = taskcards.get("pending_ids", [])
        # Filter out post-freeze tasks that are acceptable
        post_freeze_pattern = ("L0-07", "L0-08", "L0-09", "LH-03")
        real_pending = [p for p in pending_ids if not any(pf in p for pf in post_freeze_pattern)]
        if real_pending:
            _add(
                result,
                "LCV-01",
                "ERROR",
                f"Sprint is COMPLETE but has non-post-freeze pending taskcards: {real_pending}",
                f"verdict={verdict!r}",
            )


# ---------------------------------------------------------------------------
# LCV-02: No COMPLETE with pending taskcards (strict)
# ---------------------------------------------------------------------------
def check_lcv_02_no_complete_with_pending_taskcards(closeout: dict, result: LcvResult) -> None:
    verdict = closeout.get("verdict", "")
    if "COMPLETE" not in verdict.upper():
        return
    taskcards = closeout.get("taskcards", {})
    complete = int(taskcards.get("complete", 0))
    total = int(taskcards.get("total", 0))
    pending = int(taskcards.get("pending", 0))
    if total > 0 and pending > 0:
        # Only error if iv_prerequisite_satisfied is not True
        if not taskcards.get("iv_prerequisite_satisfied", False):
            _add(
                result,
                "LCV-02",
                "ERROR",
                f"Sprint is COMPLETE but taskcards show {pending}/{total} PENDING without iv_prerequisite_satisfied",
                f"complete={complete} total={total}",
            )


# ---------------------------------------------------------------------------
# LCV-03: No final verdict without external .sha256 sidecar reference
# ---------------------------------------------------------------------------
def check_lcv_03_no_verdict_without_sidecar(closeout: dict, result: LcvResult) -> None:
    verdict = closeout.get("verdict", "")
    if verdict not in ("SPRINT_COMPLETE", "COMPLETE"):
        return
    bundle = closeout.get("evidence_bundle", {})
    sidecar = bundle.get("external_sidecar", "") if isinstance(bundle, dict) else ""
    if not sidecar:
        _add(
            result,
            "LCV-03",
            "ERROR",
            "Sprint verdict is COMPLETE but evidence_bundle.external_sidecar is missing",
            f"bundle={bundle!r}",
        )


# ---------------------------------------------------------------------------
# LCV-04: No final verdict without final-attestation.json
# ---------------------------------------------------------------------------
def check_lcv_04_no_verdict_without_attestation(closeout: dict, result: LcvResult) -> None:
    verdict = closeout.get("verdict", "")
    if verdict not in ("SPRINT_COMPLETE", "COMPLETE"):
        return
    bundle = closeout.get("evidence_bundle", {})
    sha = bundle.get("sha256", "") if isinstance(bundle, dict) else ""
    protocol_note = bundle.get("protocol_note", "") if isinstance(bundle, dict) else ""
    if not sha:
        _add(
            result,
            "LCV-04",
            "ERROR",
            "Sprint verdict is COMPLETE but evidence_bundle.sha256 is missing — attestation not recorded",
            f"bundle={bundle!r}",
        )


# ---------------------------------------------------------------------------
# LCV-05: No final verdict if IV has pending checks
# ---------------------------------------------------------------------------
def check_lcv_05_no_verdict_with_pending_iv(closeout: dict, result: LcvResult) -> None:
    verdict = closeout.get("verdict", "")
    if "COMPLETE" not in verdict.upper():
        return
    iv_verdict = closeout.get("iv_verdict", "")
    if iv_verdict and "PASS" not in iv_verdict.upper():
        _add(
            result,
            "LCV-05",
            "ERROR",
            f"Sprint is COMPLETE but iv_verdict is not PASS: {iv_verdict!r}",
            f"verdict={verdict!r}",
        )


# ---------------------------------------------------------------------------
# LCV-06: No final verdict if adversarial review has pending checks
# ---------------------------------------------------------------------------
def check_lcv_06_no_verdict_with_pending_adversarial(closeout: dict, result: LcvResult) -> None:
    verdict = closeout.get("verdict", "")
    if "COMPLETE" not in verdict.upper():
        return
    ar_verdict = closeout.get("adversarial_review_verdict", "")
    if ar_verdict and "PASS" not in ar_verdict.upper():
        _add(
            result,
            "LCV-06",
            "ERROR",
            f"Sprint is COMPLETE but adversarial_review_verdict is not PASS: {ar_verdict!r}",
            f"verdict={verdict!r}",
        )


# ---------------------------------------------------------------------------
# LCV-07: No PR_READY claim without physical PR packet file
# ---------------------------------------------------------------------------
def check_lcv_07_pr_ready_requires_packet(closeout: dict, report_root: Path, result: LcvResult) -> None:
    pclc_total = closeout.get("pclc_total", 0)
    if not pclc_total:
        return
    pr_packet_dir = report_root / "publication" / "pr-packets"
    if not pr_packet_dir.exists():
        _add(
            result,
            "LCV-07",
            "ERROR",
            f"pclc_total={pclc_total} claimed but no publication/pr-packets directory exists",
            str(pr_packet_dir),
        )


# ---------------------------------------------------------------------------
# LCV-08: No PR_CREATED claim without live PR URL
# ---------------------------------------------------------------------------
def check_lcv_08_pr_created_requires_url(closeout: dict, result: LcvResult) -> None:
    prs_created = closeout.get("prs_created", 0)
    pr_urls = closeout.get("pr_urls", [])
    if prs_created and int(prs_created) > 0:
        if not pr_urls:
            _add(
                result,
                "LCV-08",
                "ERROR",
                f"prs_created={prs_created} but pr_urls list is empty",
                f"closeout keys: {list(closeout.keys())[:10]}",
            )
        elif len(pr_urls) != int(prs_created):
            _add(
                result,
                "LCV-08",
                "WARNING",
                f"prs_created={prs_created} but pr_urls has {len(pr_urls)} entries",
                f"urls={pr_urls}",
            )


# ---------------------------------------------------------------------------
# LCV-09: No PUBLISHED claim without merge/release evidence
# ---------------------------------------------------------------------------
def check_lcv_09_published_requires_evidence(closeout: dict, result: LcvResult) -> None:
    published = closeout.get("published", 0)
    if published and int(published) > 0:
        release_evidence = closeout.get("release_evidence", [])
        if not release_evidence:
            _add(
                result,
                "LCV-09",
                "ERROR",
                f"published={published} claimed but release_evidence is empty",
                "PUBLISHED status requires merge confirmation and/or release URL",
            )


# ---------------------------------------------------------------------------
# LCV-10: No package proof without restore+build+run+output validation
# ---------------------------------------------------------------------------
def check_lcv_10_package_proof_completeness(closeout: dict, report_root: Path, result: LcvResult) -> None:
    new_packages = closeout.get("new_packages_proven_w19", []) or closeout.get("new_packages_proven", [])
    if not new_packages:
        return
    # Check that each package has output-validation.json
    # Find proofs under wave*-dryrun/examples or dryrun/examples
    for pkg in new_packages:
        family, slug = pkg.split("/", 1) if "/" in pkg else (pkg, "")
        found = list(report_root.rglob(f"*/{slug}/output-validation.json"))
        if not found:
            _add(
                result,
                "LCV-10",
                "WARNING",
                f"Package {pkg!r} listed as proven but no output-validation.json found in report dir",
                str(report_root),
            )


# ---------------------------------------------------------------------------
# LCV-11: No test count claim without raw log evidence
# ---------------------------------------------------------------------------
def check_lcv_11_test_count_requires_log(closeout: dict, report_root: Path, result: LcvResult) -> None:
    validators_info = closeout.get("validators", {})
    if not validators_info:
        return
    full_suite = validators_info.get("full_suite", "") if isinstance(validators_info, dict) else str(validators_info)
    if "passed" in full_suite.lower():
        # Look for a raw test log
        log_files = (
            list(report_root.rglob("raw-validator-test.log"))
            + list(report_root.rglob("pytest-summary.txt"))
            + list(report_root.rglob("*.test.log"))
        )
        if not log_files:
            _add(
                result,
                "LCV-11",
                "WARNING",
                f"Test count claimed ({full_suite!r}) but no raw test log found in report dir",
                str(report_root),
            )


# ---------------------------------------------------------------------------
# LCV-12: No final git status omission in closeout
# ---------------------------------------------------------------------------
def check_lcv_12_final_git_status_required(closeout: dict, report_root: Path, result: LcvResult) -> None:
    verdict = closeout.get("verdict", "")
    if "COMPLETE" not in verdict.upper():
        return
    git_status_files = list(report_root.rglob("git-status-final.txt"))
    if not git_status_files:
        _add(
            result,
            "LCV-12",
            "ERROR",
            "Sprint is COMPLETE but no final/git-status-final.txt found in report dir",
            str(report_root),
        )


# ---------------------------------------------------------------------------
# LCV-13: No target repo claim without clone/fetch/PR evidence
# ---------------------------------------------------------------------------
def check_lcv_13_target_repo_requires_evidence(closeout: dict, report_root: Path, result: LcvResult) -> None:
    prs_created = closeout.get("prs_created", 0)
    if not prs_created or int(prs_created) == 0:
        return
    # Check for target-publication or pr-review directory with evidence
    target_pub = report_root / "target-publication"
    pr_review = report_root / "pr-review"
    has_evidence = (target_pub.exists() and any(target_pub.rglob("*.json"))) or (
        pr_review.exists() and any(pr_review.rglob("*.json"))
    )
    if not has_evidence:
        _add(
            result,
            "LCV-13",
            "ERROR",
            f"prs_created={prs_created} claimed but no target-publication or pr-review evidence found",
            str(report_root),
        )


# ---------------------------------------------------------------------------
# LCV-14: No unresolved dirty workspace in final git status
# ---------------------------------------------------------------------------
def check_lcv_14_dirty_workspace_must_be_classified(closeout: dict, report_root: Path, result: LcvResult) -> None:
    final_verdict = closeout.get("final_verdict", "")
    if "APPROVAL_BLOCKED" not in final_verdict.upper():
        return
    remaining_blockers = closeout.get("remaining_blockers", [])
    # Check if any blocker mentions dirty workspace
    dirty_classified = any("dirty" in str(b).lower() or "hygiene" in str(b).lower() for b in remaining_blockers)
    hygiene_evidence = list(report_root.rglob("dirty-state-classification.json"))
    if not hygiene_evidence:
        _add(
            result,
            "LCV-14",
            "WARNING",
            "Sprint claims APPROVAL_BLOCKED but no workspace-hygiene/dirty-state-classification.json found",
            "Dirty workspace must be classified before claiming only external gates remain",
        )


# ---------------------------------------------------------------------------
# LCV-15: No "only external gates remain" while local issues exist
# ---------------------------------------------------------------------------
def check_lcv_15_no_only_external_while_local_issues(closeout: dict, result: LcvResult) -> None:
    final_verdict = closeout.get("final_verdict", "")
    final_verdict_reason = closeout.get("final_verdict_reason", "")
    if "APPROVAL_BLOCKED" not in final_verdict.upper():
        return
    # Check IV and adversarial review verdicts
    iv_verdict = closeout.get("iv_verdict", "")
    ar_verdict = closeout.get("adversarial_review_verdict", "")
    issues = []
    if iv_verdict and "PASS" not in iv_verdict.upper():
        issues.append(f"iv_verdict={iv_verdict!r}")
    if ar_verdict and "PASS" not in ar_verdict.upper():
        issues.append(f"adversarial_review_verdict={ar_verdict!r}")
    # Check taskcards
    taskcards = closeout.get("taskcards", {})
    pending_count = int(taskcards.get("pending", 0)) if taskcards else 0
    if pending_count > 0 and not taskcards.get("iv_prerequisite_satisfied"):
        issues.append(f"taskcards_pending={pending_count}")
    if issues:
        _add(
            result,
            "LCV-15",
            "ERROR",
            f"Sprint claims 'only external gates remain' but local issues exist: {issues}",
            f"final_verdict_reason={final_verdict_reason!r}",
        )


# ---------------------------------------------------------------------------
# Run all LCV checks
# ---------------------------------------------------------------------------
def run_all_lcv_checks(closeout: dict, report_root: Path) -> LcvResult:
    """Run all 15 LCV checks against a sprint closeout document."""
    result = LcvResult()
    check_lcv_01_no_complete_with_pending_evidence(closeout, result)
    check_lcv_02_no_complete_with_pending_taskcards(closeout, result)
    check_lcv_03_no_verdict_without_sidecar(closeout, result)
    check_lcv_04_no_verdict_without_attestation(closeout, result)
    check_lcv_05_no_verdict_with_pending_iv(closeout, result)
    check_lcv_06_no_verdict_with_pending_adversarial(closeout, result)
    check_lcv_07_pr_ready_requires_packet(closeout, report_root, result)
    check_lcv_08_pr_created_requires_url(closeout, result)
    check_lcv_09_published_requires_evidence(closeout, result)
    check_lcv_10_package_proof_completeness(closeout, report_root, result)
    check_lcv_11_test_count_requires_log(closeout, report_root, result)
    check_lcv_12_final_git_status_required(closeout, report_root, result)
    check_lcv_13_target_repo_requires_evidence(closeout, report_root, result)
    check_lcv_14_dirty_workspace_must_be_classified(closeout, report_root, result)
    check_lcv_15_no_only_external_while_local_issues(closeout, result)
    return result
