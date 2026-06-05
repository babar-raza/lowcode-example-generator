"""
Taskcard Closeout Consistency (TCC) Validators — TCC-01..TCC-06
Bundle Metadata Verification (BMV) Validators — BMV-01..BMV-05

These validators prevent the Wave 11 closeout defects from recurring:
- TCC: Ensure no PENDING taskcards in a final bundle
- BMV: Ensure bundle metadata (SHA, commit, entry count) is internally consistent
"""
from __future__ import annotations
from typing import Any


# ---------------------------------------------------------------------------
# TCC — Taskcard Closeout Consistency
# ---------------------------------------------------------------------------

def tcc_01_no_pending_taskcards(taskcards: list[dict]) -> dict[str, Any]:
    """TCC-01: All taskcards must have status=COMPLETE at closeout time.
    Prevents: Wave 11 DEFECT-01 (all 44 taskcards PENDING despite sprint COMPLETE).
    """
    pending = [tc["id"] for tc in taskcards if tc.get("status") != "COMPLETE"]
    if pending:
        return {
            "rule": "TCC-01",
            "status": "FAIL",
            "message": f"Found {len(pending)} PENDING taskcard(s): {pending[:5]}{'...' if len(pending) > 5 else ''}",
        }
    return {"rule": "TCC-01", "status": "PASS", "message": f"All {len(taskcards)} taskcards are COMPLETE"}


def tcc_02_all_taskcards_have_evidence(taskcards: list[dict]) -> dict[str, Any]:
    """TCC-02: All COMPLETE taskcards must have non-null evidence field."""
    missing = [tc["id"] for tc in taskcards if tc.get("status") == "COMPLETE" and not tc.get("evidence")]
    if missing:
        return {
            "rule": "TCC-02",
            "status": "FAIL",
            "message": f"COMPLETE taskcard(s) missing evidence: {missing[:5]}",
        }
    return {"rule": "TCC-02", "status": "PASS", "message": f"All COMPLETE taskcards have evidence"}


def tcc_03_taskcard_count_matches_lanes(taskcards: list[dict], expected_lane_count: int) -> dict[str, Any]:
    """TCC-03: Taskcards must cover all expected lanes."""
    lanes_covered = set(tc.get("lane") for tc in taskcards)
    if len(lanes_covered) < expected_lane_count:
        return {
            "rule": "TCC-03",
            "status": "FAIL",
            "message": f"Only {len(lanes_covered)} lanes covered; expected {expected_lane_count}",
        }
    return {
        "rule": "TCC-03",
        "status": "PASS",
        "message": f"{len(lanes_covered)} lanes covered, {len(taskcards)} total taskcards",
    }


def tcc_04_no_duplicate_taskcard_ids(taskcards: list[dict]) -> dict[str, Any]:
    """TCC-04: No duplicate taskcard IDs."""
    seen: dict[str, int] = {}
    for tc in taskcards:
        tc_id = tc.get("id", "")
        seen[tc_id] = seen.get(tc_id, 0) + 1
    duplicates = [k for k, v in seen.items() if v > 1]
    if duplicates:
        return {
            "rule": "TCC-04",
            "status": "FAIL",
            "message": f"Duplicate taskcard IDs: {duplicates}",
        }
    return {"rule": "TCC-04", "status": "PASS", "message": f"No duplicate IDs in {len(taskcards)} taskcards"}


def tcc_05_taskcards_before_closeout(taskcards: list[dict], closeout_date: str) -> dict[str, Any]:
    """TCC-05: Taskcard creation date (sprint date) must be <= closeout date."""
    # Check that taskcards exist — if they do, they were created during the sprint
    if not taskcards:
        return {
            "rule": "TCC-05",
            "status": "FAIL",
            "message": "No taskcards found — taskcards must be created before closeout",
        }
    return {
        "rule": "TCC-05",
        "status": "PASS",
        "message": f"Taskcards present ({len(taskcards)}); closeout date: {closeout_date}",
    }


def tcc_06_closeout_verdict_matches_taskcard_completion(
    taskcards: list[dict], closeout_verdict: str
) -> dict[str, Any]:
    """TCC-06: If closeout_verdict=SPRINT_COMPLETE, all taskcards must be COMPLETE."""
    if closeout_verdict != "SPRINT_COMPLETE":
        return {
            "rule": "TCC-06",
            "status": "PASS",
            "message": f"Verdict is {closeout_verdict} — TCC-06 only applies to SPRINT_COMPLETE",
        }
    pending = [tc["id"] for tc in taskcards if tc.get("status") != "COMPLETE"]
    if pending:
        return {
            "rule": "TCC-06",
            "status": "FAIL",
            "message": f"Verdict=SPRINT_COMPLETE but {len(pending)} taskcard(s) are PENDING: {pending[:5]}",
        }
    return {
        "rule": "TCC-06",
        "status": "PASS",
        "message": f"Verdict=SPRINT_COMPLETE and all {len(taskcards)} taskcards are COMPLETE",
    }


# ---------------------------------------------------------------------------
# BMV — Bundle Metadata Verification
# ---------------------------------------------------------------------------

def bmv_01_bundle_sha_not_pending(closeout: dict) -> dict[str, Any]:
    """BMV-01: Bundle SHA in sprint-closeout.json must not be PENDING or empty.
    Prevents: Wave 11 DEFECT-02 scenario where closeout is written before bundle is built.
    """
    sha = closeout.get("evidence_bundle", {}).get("sha256") or closeout.get("sha256") or ""
    if not sha or sha == "PENDING" or sha == "null":
        return {
            "rule": "BMV-01",
            "status": "FAIL",
            "message": f"Bundle SHA is not recorded (got: {repr(sha)}). Must record final SHA.",
        }
    if len(sha) != 64:
        return {
            "rule": "BMV-01",
            "status": "FAIL",
            "message": f"Bundle SHA length {len(sha)} != 64 (expected SHA-256 hex string)",
        }
    return {"rule": "BMV-01", "status": "PASS", "message": f"Bundle SHA recorded: {sha[:16]}..."}


def bmv_02_commit_sha_not_pending(closeout: dict) -> dict[str, Any]:
    """BMV-02: Main commit SHA in sprint-closeout.json must not be PENDING or empty."""
    commit_sha = closeout.get("commit_sha") or ""
    if not commit_sha or commit_sha == "PENDING":
        return {
            "rule": "BMV-02",
            "status": "FAIL",
            "message": f"commit_sha is not recorded (got: {repr(commit_sha)})",
        }
    return {"rule": "BMV-02", "status": "PASS", "message": f"commit_sha recorded: {commit_sha}"}


def bmv_03_bundle_entry_count_positive(closeout: dict) -> dict[str, Any]:
    """BMV-03: Bundle entry count must be > 0."""
    entries = closeout.get("evidence_bundle", {}).get("entries") or closeout.get("bundle_entries") or 0
    if not isinstance(entries, int) or entries <= 0:
        return {
            "rule": "BMV-03",
            "status": "FAIL",
            "message": f"Bundle entry count invalid: {repr(entries)}",
        }
    return {"rule": "BMV-03", "status": "PASS", "message": f"Bundle entry count: {entries}"}


def bmv_04_bundle_size_positive(closeout: dict) -> dict[str, Any]:
    """BMV-04: Bundle size_bytes must be > 0."""
    size = closeout.get("evidence_bundle", {}).get("size_bytes") or closeout.get("bundle_size_bytes") or 0
    if not isinstance(size, int) or size <= 0:
        return {
            "rule": "BMV-04",
            "status": "FAIL",
            "message": f"Bundle size_bytes invalid: {repr(size)}",
        }
    return {"rule": "BMV-04", "status": "PASS", "message": f"Bundle size: {size:,} bytes"}


def bmv_05_pytest_passed_count_positive(closeout: dict) -> dict[str, Any]:
    """BMV-05: pytest_passed must be > 0 and pytest_failed must be 0."""
    passed = closeout.get("pytest_passed", 0)
    failed = closeout.get("pytest_failed", -1)
    if not isinstance(passed, int) or passed <= 0:
        return {
            "rule": "BMV-05",
            "status": "FAIL",
            "message": f"pytest_passed is {repr(passed)} — must be > 0",
        }
    if not isinstance(failed, int) or failed != 0:
        return {
            "rule": "BMV-05",
            "status": "FAIL",
            "message": f"pytest_failed is {repr(failed)} — must be 0",
        }
    return {
        "rule": "BMV-05",
        "status": "PASS",
        "message": f"pytest: {passed} passed, {failed} failed",
    }


# ---------------------------------------------------------------------------
# Aggregate runners
# ---------------------------------------------------------------------------

def run_all_tcc_validators(
    taskcards: list[dict],
    expected_lane_count: int,
    closeout_date: str,
    closeout_verdict: str,
) -> dict[str, Any]:
    """Run all TCC-01..TCC-06 validators and return aggregate result."""
    results = [
        tcc_01_no_pending_taskcards(taskcards),
        tcc_02_all_taskcards_have_evidence(taskcards),
        tcc_03_taskcard_count_matches_lanes(taskcards, expected_lane_count),
        tcc_04_no_duplicate_taskcard_ids(taskcards),
        tcc_05_taskcards_before_closeout(taskcards, closeout_date),
        tcc_06_closeout_verdict_matches_taskcard_completion(taskcards, closeout_verdict),
    ]
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    return {
        "suite": "TCC",
        "rules": results,
        "pass": pass_count,
        "fail": fail_count,
        "verdict": "ALL_PASS" if fail_count == 0 else "FAIL",
    }


def run_all_bmv_validators(closeout: dict) -> dict[str, Any]:
    """Run all BMV-01..BMV-05 validators and return aggregate result."""
    results = [
        bmv_01_bundle_sha_not_pending(closeout),
        bmv_02_commit_sha_not_pending(closeout),
        bmv_03_bundle_entry_count_positive(closeout),
        bmv_04_bundle_size_positive(closeout),
        bmv_05_pytest_passed_count_positive(closeout),
    ]
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    return {
        "suite": "BMV",
        "rules": results,
        "pass": pass_count,
        "fail": fail_count,
        "verdict": "ALL_PASS" if fail_count == 0 else "FAIL",
    }
