"""
Pending Evidence Validators (PEV-01..PEV-03)

PEV-01: No COMPLETE taskcard may have 'PENDING' in its evidence field
PEV-02: No COMPLETE taskcard may have 'DEFERRED' in its evidence field
PEV-03: No COMPLETE taskcard may have an empty evidence field
"""

from dataclasses import dataclass, field


@dataclass
class PEVResult:
    rule_id: str
    status: str  # "PASS" | "FAIL"
    message: str
    details: dict = field(default_factory=dict)


def _evidence_str(tc: dict) -> str:
    """Convert evidence field to string for inspection."""
    ev = tc.get("evidence", "")
    if isinstance(ev, list):
        return " ".join(str(x) for x in ev)
    return str(ev)


def pev_01_no_pending_in_complete_evidence(taskcards: list) -> PEVResult:
    """PEV-01: COMPLETE taskcards must not have 'PENDING' in evidence."""
    violations = []
    for tc in taskcards:
        if tc.get("status") == "COMPLETE":
            ev = _evidence_str(tc)
            if "PENDING" in ev:
                violations.append({"id": tc.get("id", "?"), "evidence_excerpt": ev[:80]})
    if violations:
        return PEVResult(
            rule_id="PEV-01",
            status="FAIL",
            message=f"{len(violations)} COMPLETE taskcard(s) have 'PENDING' in evidence",
            details={"violations": violations},
        )
    return PEVResult(
        rule_id="PEV-01",
        status="PASS",
        message="No COMPLETE taskcards have 'PENDING' in evidence",
        details={"checked": len(taskcards)},
    )


def pev_02_no_deferred_in_complete_evidence(taskcards: list) -> PEVResult:
    """PEV-02: COMPLETE taskcards must not have 'DEFERRED' in evidence."""
    violations = []
    for tc in taskcards:
        if tc.get("status") == "COMPLETE":
            ev = _evidence_str(tc)
            if "DEFERRED" in ev:
                violations.append({"id": tc.get("id", "?"), "evidence_excerpt": ev[:80]})
    if violations:
        return PEVResult(
            rule_id="PEV-02",
            status="FAIL",
            message=f"{len(violations)} COMPLETE taskcard(s) have 'DEFERRED' in evidence",
            details={"violations": violations},
        )
    return PEVResult(
        rule_id="PEV-02",
        status="PASS",
        message="No COMPLETE taskcards have 'DEFERRED' in evidence",
        details={"checked": len(taskcards)},
    )


def pev_03_no_empty_evidence_on_complete(taskcards: list) -> PEVResult:
    """PEV-03: COMPLETE taskcards must not have empty evidence."""
    violations = []
    for tc in taskcards:
        if tc.get("status") == "COMPLETE":
            ev = _evidence_str(tc).strip()
            if not ev:
                violations.append({"id": tc.get("id", "?")})
    if violations:
        return PEVResult(
            rule_id="PEV-03",
            status="FAIL",
            message=f"{len(violations)} COMPLETE taskcard(s) have empty evidence",
            details={"violations": violations},
        )
    return PEVResult(
        rule_id="PEV-03",
        status="PASS",
        message="All COMPLETE taskcards have non-empty evidence",
        details={"checked": len(taskcards)},
    )


def run_all_pev(taskcards: list) -> list[PEVResult]:
    return [
        pev_01_no_pending_in_complete_evidence(taskcards),
        pev_02_no_deferred_in_complete_evidence(taskcards),
        pev_03_no_empty_evidence_on_complete(taskcards),
    ]
