"""
Taskcard Count Validators (TCV-01..TCV-03)

TCV-01: taskcards.total must equal len(taskcards array)
TCV-02: complete + pending must equal total
TCV-03: pending must equal 0 at sprint close
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TCVResult:
    rule_id: str
    status: str  # "PASS" | "FAIL"
    message: str
    details: dict = field(default_factory=dict)


def tcv_01_total_matches_array_length(closeout: dict, taskcards_array: list) -> TCVResult:
    """TCV-01: claimed total must equal actual array length."""
    claimed = closeout.get("taskcards", {}).get("total", None)
    actual = len(taskcards_array)
    if claimed is None:
        return TCVResult(
            rule_id="TCV-01",
            status="FAIL",
            message="taskcards.total field missing from closeout",
            details={"claimed": None, "actual": actual},
        )
    if claimed != actual:
        return TCVResult(
            rule_id="TCV-01",
            status="FAIL",
            message=f"taskcards.total={claimed} does not match actual array length={actual}",
            details={"claimed": claimed, "actual": actual, "delta": actual - claimed},
        )
    return TCVResult(
        rule_id="TCV-01",
        status="PASS",
        message=f"taskcards.total={claimed} matches array length={actual}",
        details={"total": actual},
    )


def tcv_02_complete_plus_pending_equals_total(closeout: dict) -> TCVResult:
    """TCV-02: complete + pending must equal total."""
    tc = closeout.get("taskcards", {})
    total = tc.get("total")
    complete = tc.get("complete")
    pending = tc.get("pending")
    if any(v is None for v in [total, complete, pending]):
        return TCVResult(
            rule_id="TCV-02",
            status="FAIL",
            message="One or more of taskcards.total/complete/pending is missing",
            details={"total": total, "complete": complete, "pending": pending},
        )
    if complete + pending != total:
        return TCVResult(
            rule_id="TCV-02",
            status="FAIL",
            message=f"complete({complete}) + pending({pending}) = {complete+pending} != total({total})",
            details={"total": total, "complete": complete, "pending": pending},
        )
    return TCVResult(
        rule_id="TCV-02",
        status="PASS",
        message=f"complete({complete}) + pending({pending}) = total({total})",
        details={"total": total, "complete": complete, "pending": pending},
    )


def tcv_03_pending_zero_at_sprint_close(closeout: dict) -> TCVResult:
    """TCV-03: pending must equal 0 at sprint close."""
    pending = closeout.get("taskcards", {}).get("pending")
    if pending is None:
        return TCVResult(
            rule_id="TCV-03",
            status="FAIL",
            message="taskcards.pending field missing from closeout",
            details={"pending": None},
        )
    if pending != 0:
        return TCVResult(
            rule_id="TCV-03",
            status="FAIL",
            message=f"taskcards.pending={pending} != 0 at sprint close",
            details={"pending": pending},
        )
    return TCVResult(
        rule_id="TCV-03",
        status="PASS",
        message="taskcards.pending=0 at sprint close",
        details={"pending": 0},
    )


def run_all_tcv(closeout: dict, taskcards_array: list) -> list[TCVResult]:
    return [
        tcv_01_total_matches_array_length(closeout, taskcards_array),
        tcv_02_complete_plus_pending_equals_total(closeout),
        tcv_03_pending_zero_at_sprint_close(closeout),
    ]
