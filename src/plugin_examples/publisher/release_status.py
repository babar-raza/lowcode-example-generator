"""Release status reader — reads evidence files to produce per-family release state report."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Taskcard ID prefixes that indicate a family association.
_FAMILY_TASKCARD_PREFIXES: dict[str, str] = {
    "cells": "followup-cells-",
    "words": "followup-words-",
    "pdf": "followup-pdf-",
}

_TASKCARD_MATRIX_FILENAME = "open-taskcard-closure-matrix.json"


def _load_open_taskcards_from_matrix(
    verification_dir: Path, family: str
) -> tuple[list[str], str]:
    """Read open taskcards for a family from the authoritative JSON matrix.

    Returns:
        (list_of_open_taskcard_ids, evidence_source_tag)
    """
    matrix_path = verification_dir / "latest" / _TASKCARD_MATRIX_FILENAME
    if not matrix_path.exists():
        logger.warning(
            "Taskcard matrix not found at %s — open_followups will be empty", matrix_path
        )
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
    open_ids = [
        tc["id"]
        for tc in taskcards
        if tc.get("status") == "OPEN" and tc["id"].startswith(prefix)
    ]
    return open_ids, str(matrix_path)


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return {}


def _get_next_action(family: str, post_merge_status: str, merge_sha: str | None) -> str:
    """Derive next required action from current state."""
    if not merge_sha:
        return "create_live_pr — no merge SHA recorded; PR not yet merged"
    if post_merge_status not in ("POST_MERGE_VERIFIED", "ALL_PASS"):
        return "post_merge_validation — merge SHA recorded but post-merge validation not complete"
    if family == "words":
        return "resolve_open_taskcards_for_broader_generation (followup-words-* series)"
    if family == "cells":
        return "monitor_for_package_updates — all examples published"
    return "monitor"


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
        # Source of truth version from discovery
        discovery = _load_json(latest / "all-family-lowcode-discovery.json")
        source_version = None
        for entry in discovery.get("families", []):
            if entry.get("family") == family:
                source_version = entry.get("nuget_version") or entry.get("package_version")
                break

        # Latest published version from live PR result
        live_pr = _load_json(latest / f"{family}-live-pr-result.json")
        published_version = live_pr.get("nuget_version")
        published_count = live_pr.get("examples_count", 0)
        last_pr_url = live_pr.get("pr_url")
        last_pr_number = live_pr.get("pr_number")

        # Merge SHA from merge result
        merge_result = _load_json(latest / f"{family}-merge-result.json")
        merge_sha = merge_result.get("merge_commit_sha")
        merge_date = merge_result.get("merge_date")

        # Post-merge validation status
        post_merge = _load_json(
            latest / f"{family}-post-merge-clean-checkout-validation.json"
        )
        post_merge_status = post_merge.get("summary", {}).get("overall_result", "NOT_RUN")
        post_merge_passed = post_merge.get("summary", {}).get("passed", 0)
        post_merge_total = post_merge.get("summary", {}).get("total_examples", 0)

        # Open followups for this family — read from authoritative JSON matrix
        open_followups, taskcard_source = _load_open_taskcards_from_matrix(
            verification_dir, family
        )

        next_action = _get_next_action(family, post_merge_status, merge_sha)

        results.append({
            "family": family,
            "source_of_truth_version": source_version,
            "latest_published_version": published_version,
            "published_examples_count": published_count,
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
        })

    all_merged = all(r["last_merge_sha"] is not None for r in results)
    all_validated = all(
        r["last_post_merge_validation_status"] in ("POST_MERGE_VERIFIED", "ALL_PASS")
        for r in results
    )

    return {
        "report_type": "release_status",
        "families_checked": families,
        "all_merged": all_merged,
        "all_post_merge_validated": all_validated,
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
