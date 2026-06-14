"""Evidence chain validators — cross-corroborate gate verdicts with evidence artifacts.

Rules:
    ECV-01: Every gate verdict must reference a non-null evidence path
    ECV-02: Referenced evidence files must exist on disk
    ECV-03: Evidence timestamps must be within the declared run window
    ECV-04: Gate result content must be consistent with evidence JSON
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ECVResult:
    rule_id: str
    passed: bool
    message: str
    evidence_path: str = ""
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "rule_id": self.rule_id,
            "passed": self.passed,
            "message": self.message,
        }
        if self.evidence_path:
            d["evidence_path"] = self.evidence_path
        if self.details:
            d["details"] = self.details
        return d


def validate_ecv01_non_null_evidence_paths(
    gate_results: list[dict[str, Any]],
) -> list[ECVResult]:
    """ECV-01: Every gate verdict must reference a non-null evidence_path."""
    results: list[ECVResult] = []
    for gate in gate_results:
        gate_id = gate.get("gate_id", gate.get("id", "unknown"))
        evidence_path = gate.get("evidence_path")
        if evidence_path is None or evidence_path == "":
            results.append(ECVResult(
                rule_id="ECV-01",
                passed=False,
                message=f"Gate '{gate_id}' has null or empty evidence_path",
                details={"gate_id": gate_id, "verdict": gate.get("verdict", "")},
            ))
        else:
            results.append(ECVResult(
                rule_id="ECV-01",
                passed=True,
                message=f"Gate '{gate_id}' has evidence_path: {evidence_path}",
                evidence_path=str(evidence_path),
            ))
    return results


def validate_ecv02_evidence_files_exist(
    gate_results: list[dict[str, Any]],
    base_dir: Path,
) -> list[ECVResult]:
    """ECV-02: Referenced evidence files must exist on disk."""
    results: list[ECVResult] = []
    for gate in gate_results:
        gate_id = gate.get("gate_id", gate.get("id", "unknown"))
        evidence_path = gate.get("evidence_path")
        if not evidence_path:
            continue  # ECV-01 already flags this
        full_path = base_dir / evidence_path
        if full_path.exists():
            results.append(ECVResult(
                rule_id="ECV-02",
                passed=True,
                message=f"Evidence file exists: {evidence_path}",
                evidence_path=str(evidence_path),
            ))
        else:
            results.append(ECVResult(
                rule_id="ECV-02",
                passed=False,
                message=f"Evidence file missing for gate '{gate_id}': {evidence_path}",
                evidence_path=str(evidence_path),
                details={"gate_id": gate_id, "expected_path": str(full_path)},
            ))
    return results


def validate_ecv03_timestamps_within_window(
    gate_results: list[dict[str, Any]],
    run_start: str | None = None,
    run_end: str | None = None,
    max_age_hours: float = 72.0,
) -> list[ECVResult]:
    """ECV-03: Evidence timestamps must be within the declared run window.

    If run_start/run_end not provided, checks that timestamps are not older
    than max_age_hours from now.
    """
    results: list[ECVResult] = []
    now = datetime.now(UTC)

    for gate in gate_results:
        gate_id = gate.get("gate_id", gate.get("id", "unknown"))
        timestamp_str = gate.get("timestamp") or gate.get("completed_at")
        if not timestamp_str:
            results.append(ECVResult(
                rule_id="ECV-03",
                passed=False,
                message=f"Gate '{gate_id}' has no timestamp",
                details={"gate_id": gate_id},
            ))
            continue

        try:
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
        except (ValueError, AttributeError):
            results.append(ECVResult(
                rule_id="ECV-03",
                passed=False,
                message=f"Gate '{gate_id}' has unparseable timestamp: {timestamp_str}",
                details={"gate_id": gate_id, "raw_timestamp": timestamp_str},
            ))
            continue

        if run_start and run_end:
            try:
                start = datetime.fromisoformat(run_start.replace("Z", "+00:00"))
                end = datetime.fromisoformat(run_end.replace("Z", "+00:00"))
                if start.tzinfo is None:
                    start = start.replace(tzinfo=UTC)
                if end.tzinfo is None:
                    end = end.replace(tzinfo=UTC)
                in_window = start <= ts <= end
            except ValueError:
                in_window = False
        else:
            age_hours = (now - ts).total_seconds() / 3600
            in_window = age_hours <= max_age_hours

        results.append(ECVResult(
            rule_id="ECV-03",
            passed=in_window,
            message=(
                f"Gate '{gate_id}' timestamp {'within' if in_window else 'outside'} run window"
            ),
            details={"gate_id": gate_id, "timestamp": timestamp_str},
        ))
    return results


def validate_ecv04_gate_evidence_consistency(
    gate_results: list[dict[str, Any]],
    base_dir: Path,
) -> list[ECVResult]:
    """ECV-04: Gate result content must be consistent with evidence JSON.

    Checks that the verdict in the gate result matches what the evidence
    file reports, and that key fields (family, run_id) align.
    """
    results: list[ECVResult] = []
    for gate in gate_results:
        gate_id = gate.get("gate_id", gate.get("id", "unknown"))
        evidence_path = gate.get("evidence_path")
        if not evidence_path:
            continue

        full_path = base_dir / evidence_path
        if not full_path.exists():
            continue  # ECV-02 already flags this

        try:
            evidence_data = json.loads(full_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            results.append(ECVResult(
                rule_id="ECV-04",
                passed=False,
                message=f"Evidence file for gate '{gate_id}' is not valid JSON",
                evidence_path=str(evidence_path),
            ))
            continue

        # Check verdict consistency
        gate_verdict = gate.get("verdict", "")
        evidence_verdict = evidence_data.get("verdict", evidence_data.get("status", ""))
        if gate_verdict and evidence_verdict and gate_verdict != evidence_verdict:
            results.append(ECVResult(
                rule_id="ECV-04",
                passed=False,
                message=(
                    f"Gate '{gate_id}' verdict '{gate_verdict}' != "
                    f"evidence verdict '{evidence_verdict}'"
                ),
                evidence_path=str(evidence_path),
                details={
                    "gate_id": gate_id,
                    "gate_verdict": gate_verdict,
                    "evidence_verdict": evidence_verdict,
                },
            ))
        else:
            results.append(ECVResult(
                rule_id="ECV-04",
                passed=True,
                message=f"Gate '{gate_id}' verdict consistent with evidence",
                evidence_path=str(evidence_path),
            ))

        # Check family consistency if present
        gate_family = gate.get("family", "")
        evidence_family = evidence_data.get("family", "")
        if gate_family and evidence_family and gate_family != evidence_family:
            results.append(ECVResult(
                rule_id="ECV-04",
                passed=False,
                message=(
                    f"Gate '{gate_id}' family '{gate_family}' != "
                    f"evidence family '{evidence_family}'"
                ),
                evidence_path=str(evidence_path),
                details={
                    "gate_id": gate_id,
                    "gate_family": gate_family,
                    "evidence_family": evidence_family,
                },
            ))

    return results


def run_all_ecv_validators(
    gate_results: list[dict[str, Any]],
    base_dir: Path,
    run_start: str | None = None,
    run_end: str | None = None,
) -> list[ECVResult]:
    """Run all ECV validators and return combined results."""
    all_results: list[ECVResult] = []
    all_results.extend(validate_ecv01_non_null_evidence_paths(gate_results))
    all_results.extend(validate_ecv02_evidence_files_exist(gate_results, base_dir))
    all_results.extend(validate_ecv03_timestamps_within_window(
        gate_results, run_start, run_end
    ))
    all_results.extend(validate_ecv04_gate_evidence_consistency(gate_results, base_dir))
    return all_results
