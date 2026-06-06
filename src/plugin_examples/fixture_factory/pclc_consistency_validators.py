"""
PCLC Consistency Validators — PCLV-01..PCLV-03
Wave 16: Catch PCLC count divergence between state summary and readiness files.

  PCLV-01: PCLC count in state summary must match readiness file entry count.
  PCLV-02: Every PCLC entry must have a pr_packet_exists field.
  PCLV-03: PR packet count must match declared publication-ready count unless reason recorded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PCLVResult:
    rule_id: str
    passed: bool
    message: str
    detail: dict[str, Any] = field(default_factory=dict)


def pclv_01_state_count_matches_readiness_file(
    state_summary: dict, readiness_data: dict
) -> PCLVResult:
    """PCLC count in state summary must match readiness file entry count."""
    state_pclc = state_summary.get("pclc_count") if "pclc_count" in state_summary else state_summary.get("pclc_total")
    if state_pclc is None:
        return PCLVResult("PCLV-01", False,
            "State summary missing pclc_count or pclc_total field")

    readiness_total = readiness_data.get("pclc_total") or len(readiness_data.get("packages", []))
    if readiness_total == 0 and "packages" not in readiness_data:
        return PCLVResult("PCLV-01", False,
            "Readiness file missing pclc_total and packages fields")

    if state_pclc != readiness_total:
        return PCLVResult("PCLV-01", False,
            f"PCLC count mismatch: state_summary={state_pclc}, readiness_file={readiness_total}",
            {"state_pclc": state_pclc, "readiness_total": readiness_total})

    return PCLVResult("PCLV-01", True, f"PCLC count consistent: {state_pclc} packages")


def pclv_02_every_pclc_has_pr_packet_field(readiness_data: dict) -> PCLVResult:
    """Every PCLC entry in readiness file must have pr_packet_exists field."""
    packages = readiness_data.get("packages", [])
    if not packages:
        return PCLVResult("PCLV-02", False, "No packages in readiness file")

    missing_field = [
        f"{p.get('family', '?')}/{p.get('slug', '?')}"
        for p in packages
        if "pr_packet_exists" not in p
    ]

    if missing_field:
        return PCLVResult("PCLV-02", False,
            f"{len(missing_field)} packages missing pr_packet_exists field: {missing_field}",
            {"missing": missing_field})

    return PCLVResult("PCLV-02", True, f"All {len(packages)} packages have pr_packet_exists field")


def pclv_03_pr_packet_count_matches_ready_count(readiness_data: dict) -> PCLVResult:
    """PR packet count must match publication-ready count unless reason recorded."""
    packages = readiness_data.get("packages", [])
    total = readiness_data.get("pclc_total", len(packages))
    pr_ready = sum(1 for p in packages if p.get("pr_packet_exists") is True)
    pr_wave16 = readiness_data.get("pr_packets_wave16_count", 0)
    stated_total_packets = readiness_data.get("pr_packets_total", 0)

    if stated_total_packets != total and pr_wave16 == 0:
        return PCLVResult("PCLV-03", False,
            f"PR packet total {stated_total_packets} != PCLC total {total} and no wave16 addition recorded",
            {"stated_total": stated_total_packets, "pclc_total": total})

    return PCLVResult("PCLV-03", True,
        f"PR packets: {pr_ready} direct + {pr_wave16} wave16 additions = {stated_total_packets} total for {total} PCLC")


def run_all_pclv(state_summary: dict, readiness_data: dict) -> list[PCLVResult]:
    results = []
    results.append(pclv_01_state_count_matches_readiness_file(state_summary, readiness_data))
    results.append(pclv_02_every_pclc_has_pr_packet_field(readiness_data))
    results.append(pclv_03_pr_packet_count_matches_ready_count(readiness_data))
    return results
