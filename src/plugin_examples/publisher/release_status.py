"""Release status reader — reads evidence files to produce per-family release state report."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

ALL_RELEASE_FAMILIES = ["cells", "words", "pdf", "diagram", "email", "slides"]

# Taskcard ID prefixes that indicate a family association.
_FAMILY_TASKCARD_PREFIXES: dict[str, str] = {
    "cells": "followup-cells-",
    "words": "followup-words-",
    "pdf": "followup-pdf-",
    "diagram": "followup-diagram-",
    "email": "followup-email-",
    "slides": "followup-slides-",
}

_TASKCARD_MATRIX_FILENAME = "open-taskcard-closure-matrix.json"


def _repo_root_from_verification_dir(verification_dir: Path) -> Path:
    """Return repo root from workspace/verification."""
    return verification_dir.resolve().parents[1]


def _load_open_taskcards_from_matrix(verification_dir: Path, family: str) -> tuple[list[str], str]:
    """Read open taskcards for a family from the authoritative JSON matrix.

    Returns:
        (list_of_open_taskcard_ids, evidence_source_tag)
    """
    matrix_path = verification_dir / "latest" / _TASKCARD_MATRIX_FILENAME
    if not matrix_path.exists():
        logger.warning("Taskcard matrix not found at %s — open_followups will be empty", matrix_path)
        return [], "missing_taskcard_matrix"

    try:
        # Use errors='replace' to tolerate non-UTF-8 bytes in evidence files;
        # only the 'id' and 'status' fields are read, which are pure ASCII.
        matrix = json.loads(matrix_path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read taskcard matrix %s: %s", matrix_path, exc)
        return [], "unreadable_taskcard_matrix"

    taskcards = matrix.get("taskcards", [])
    prefix = _FAMILY_TASKCARD_PREFIXES.get(family, f"followup-{family}-")
    open_ids = [tc["id"] for tc in taskcards if tc.get("status") == "OPEN" and tc["id"].startswith(prefix)]
    return open_ids, str(matrix_path)


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return {}


def _count_cumulative_prs(family: str, latest: Path) -> int:
    """Count distinct merged PRs for a family by scanning all *merge-result*.json files.

    Scans latest/ for files matching the pattern ``{family}*merge-result*.json``,
    loads each, and counts unique non-null ``merge_commit_sha`` values.
    """
    shas: set[str] = set()
    for path in latest.glob(f"{family}*merge-result*.json"):
        data = _load_json(path)
        sha = data.get("merge_commit_sha")
        if sha:
            shas.add(sha)
    return len(shas)


def _load_denominator(verification_dir: Path, family: str) -> dict:
    repo_root = _repo_root_from_verification_dir(verification_dir)
    return _load_json(repo_root / "pipeline" / "configs" / "denominators" / f"{family}.json")


def _compute_release_scope_status(denominator: dict, published_count: int) -> tuple[str, str]:
    """Classify release completeness for reporting.

    The primary status answers "what should an operator believe about this family now?"
    It intentionally separates pilot completion from family completion.
    """
    basis = denominator.get("denominator_basis")
    workflow_roots = denominator.get("workflow_root_types")
    allowed_pilot = denominator.get("allowed_pilot_count")

    if basis == "DISCOVERY_ONLY":
        return "DISCOVERY_ONLY", "Pilot not launched; generation/publish intentionally blocked."

    if workflow_roots is None:
        return "NEEDS_CLASSIFICATION", "workflow_root_types is null; family completeness cannot be determined."

    if basis == "PILOT_ALLOWED":
        if allowed_pilot is None:
            return "BLOCKED", "PILOT_ALLOWED denominator is missing allowed_pilot_count."
        if allowed_pilot > 0 and published_count >= allowed_pilot:
            return (
                "PILOT_COMPLETE",
                f"{published_count}/{allowed_pilot} pilot types published; "
                f"{published_count}/{workflow_roots} workflow roots published overall.",
            )
        return (
            "PARTIAL_CANARY",
            f"{published_count}/{allowed_pilot or 0} pilot types published; "
            f"{published_count}/{workflow_roots} workflow roots published overall.",
        )

    if workflow_roots > 0 and published_count >= workflow_roots:
        return "FAMILY_COMPLETE", f"{published_count}/{workflow_roots} workflow roots published."

    if published_count > 0:
        return "PARTIAL_FAMILY_COVERAGE", f"{published_count}/{workflow_roots} workflow roots published."

    return "BLOCKED", f"0/{workflow_roots} workflow roots published."


def _compute_family_coverage_status(denominator: dict, published_count: int) -> tuple[str, str]:
    workflow_roots = denominator.get("workflow_root_types")
    basis = denominator.get("denominator_basis")

    if basis == "DISCOVERY_ONLY":
        return "DISCOVERY_ONLY", "Pilot not launched; family coverage intentionally deferred."
    if workflow_roots is None:
        return "NEEDS_CLASSIFICATION", "workflow_root_types is null."
    if workflow_roots > 0 and published_count >= workflow_roots:
        return "FAMILY_COMPLETE", f"{published_count}/{workflow_roots} workflow roots published."
    if published_count > 0:
        return "PARTIAL_FAMILY_COVERAGE", f"{published_count}/{workflow_roots} workflow roots published."
    return "BLOCKED", f"0/{workflow_roots} workflow roots published."


def _get_next_action(family: str, post_merge_status: str, merge_sha: str | None) -> str:
    """Derive next required action from current state."""
    if not merge_sha:
        return "create_live_pr — no merge SHA recorded; PR not yet merged"
    if post_merge_status not in ("POST_MERGE_VERIFIED", "ALL_PASS"):
        return "post_merge_validation — merge SHA recorded but post-merge validation not complete"
    _family_actions = {
        "words": "resolve_open_taskcards_for_broader_generation (followup-words-* series)",
        "cells": "monitor_for_package_updates — all examples published",
        "pdf": "resolve_open_taskcards_for_pilot_expansion (followup-pdf-* series)",
        "diagram": "monitor_for_package_updates — pilot examples published",
        "email": "expand_email_pilot — Converter published; expand to additional Email LowCode types",
        "slides": "expand_slides_pilot — Compress/Convert/Merger published; expand to additional Slides LowCode types",
    }
    return _family_actions.get(family, f"monitor — {family} pilot complete")


def compute_release_status(families: list[str], verification_dir: Path) -> dict:
    """Read evidence and compute per-family release status.

    Args:
        families: List of family names to report on.
        verification_dir: Path to workspace/verification directory.

    Returns:
        Dict with ``families`` list and ``summary`` fields.
    """
    latest = verification_dir / "latest"
    results = []

    for family in families:
        denominator = _load_denominator(verification_dir, family)

        # Source of truth version from discovery
        discovery = _load_json(latest / "all-family-lowcode-discovery.json")
        source_version = denominator.get("source_version")
        for entry in discovery.get("families", []):
            if entry.get("family") == family:
                source_version = entry.get("nuget_version") or entry.get("package_version") or source_version
                break

        # Latest published version from live PR result
        live_pr = _load_json(latest / f"{family}-live-pr-result.json")
        published_version = live_pr.get("nuget_version")
        # Use denominator published_count as authoritative cumulative total;
        # fall back to last-PR examples_count for families without a denominator entry.
        published_count = denominator.get("published_count") or live_pr.get("examples_count", 0)
        last_pr_url = live_pr.get("pr_url")
        last_pr_number = live_pr.get("pr_number")

        # Merge SHA from merge result
        merge_result = _load_json(latest / f"{family}-merge-result.json")
        merge_sha = merge_result.get("merge_commit_sha")
        merge_date = merge_result.get("merge_date")

        # Post-merge validation status
        post_merge = _load_json(latest / f"{family}-post-merge-clean-checkout-validation.json")
        post_merge_status = post_merge.get("summary", {}).get("overall_result", "NOT_RUN")
        post_merge_passed = post_merge.get("summary", {}).get("passed", 0)
        post_merge_total = post_merge.get("summary", {}).get("total_examples", 0)

        # Open followups for this family — read from authoritative JSON matrix
        open_followups, taskcard_source = _load_open_taskcards_from_matrix(verification_dir, family)

        cumulative_pr_count = _count_cumulative_prs(family, latest)
        scope_status, scope_reason = _compute_release_scope_status(denominator, published_count)
        family_coverage_status, family_coverage_reason = _compute_family_coverage_status(denominator, published_count)
        if scope_status == "DISCOVERY_ONLY":
            next_action = (
                f"pilot_not_yet_launched - status discovery_only; "
                f"do not create live PR until fixture strategy and pilot approval are complete"
            )
        else:
            next_action = _get_next_action(family, post_merge_status, merge_sha)

        results.append(
            {
                "family": family,
                "source_of_truth_version": source_version,
                "latest_published_version": published_version,
                "published_examples_count": published_count,
                "release_scope_status": scope_status,
                "release_scope_reason": scope_reason,
                "family_coverage_status": family_coverage_status,
                "family_coverage_reason": family_coverage_reason,
                "denominator_basis": denominator.get("denominator_basis"),
                "workflow_root_types": denominator.get("workflow_root_types"),
                "allowed_pilot_count": denominator.get("allowed_pilot_count"),
                "total_lowcode_types": denominator.get("total_lowcode_types"),
                "last_pr_url": last_pr_url,
                "last_pr_number": last_pr_number,
                "last_merge_sha": merge_sha,
                "last_merge_date": merge_date,
                "last_post_merge_validation_status": post_merge_status,
                "post_merge_passed": post_merge_passed,
                "post_merge_total": post_merge_total,
                "open_followups": open_followups,
                "taskcard_evidence_source": taskcard_source,
                "next_required_action": next_action,
                "cumulative_pr_count": cumulative_pr_count,
            }
        )

    all_merged = all(r["last_merge_sha"] is not None for r in results)
    all_validated = all(r["last_post_merge_validation_status"] in ("POST_MERGE_VERIFIED", "ALL_PASS") for r in results)

    # Compute accurate top-level summary fields from denominator data
    total_published = sum(r["published_examples_count"] for r in results)
    total_contracts = sum((r["allowed_pilot_count"] or r["workflow_root_types"] or 0) for r in results)
    # pr_ready comes from denominator pr_dry_run_ready_count
    total_pr_ready = 0
    for family in families:
        d = _load_denominator(verification_dir, family)
        total_pr_ready += d.get("pr_dry_run_ready_count", 0)

    all_published = total_contracts > 0 and total_published >= total_contracts
    all_contracts_accounted = total_contracts > 0 and (total_published + total_pr_ready) >= total_contracts
    families_complete = sum(1 for r in results if r["release_scope_status"] in ("FAMILY_COMPLETE", "PILOT_COMPLETE"))
    families_partial = sum(
        1 for r in results if r["release_scope_status"] in ("PARTIAL_CANARY", "PARTIAL_FAMILY_COVERAGE")
    )
    approval_blocked = total_pr_ready  # PR-ready but not yet published

    return {
        "report_type": "release_status",
        "generated_at": datetime.now(UTC).isoformat(),
        "families_checked": families,
        "all_merged": all_merged,
        "all_post_merge_validated": all_validated,
        "all_published": all_published,
        "all_contracts_accounted_for": all_contracts_accounted,
        "published_count": total_published,
        "pr_ready_count": total_pr_ready,
        "total_contracts": total_contracts,
        "approval_blocked_count": approval_blocked,
        "families_complete_count": families_complete,
        "families_partial_count": families_partial,
        "families": results,
    }


def write_release_status_report(status: dict, verification_dir: Path) -> Path:
    """Write release status report to workspace/verification/latest/."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "release-status.json"
    path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    logger.info("Release status report written: %s", path)
    return path
