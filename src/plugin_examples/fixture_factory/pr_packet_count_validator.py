"""
PR Packet Count Validators (PRC-01..PRC-02)

PRC-01: Bundle PR packet count must be >= pclc_total
PRC-02: Each PCLC package must have a pr-packet.json inside the bundle
"""

import zipfile
from dataclasses import dataclass, field


@dataclass
class PRCResult:
    rule_id: str
    status: str  # "PASS" | "FAIL"
    message: str
    details: dict = field(default_factory=dict)


def prc_01_bundle_pr_packet_count_gte_pclc_total(
    bundle_path: str, pclc_total: int
) -> PRCResult:
    """PRC-01: count of pr-packet.json in bundle >= pclc_total."""
    try:
        with zipfile.ZipFile(bundle_path) as zf:
            pr_packets = [n for n in zf.namelist() if n.endswith("pr-packet.json")]
    except Exception as e:
        return PRCResult(
            rule_id="PRC-01",
            status="FAIL",
            message=f"Could not open bundle: {e}",
            details={"bundle_path": bundle_path},
        )
    count = len(pr_packets)
    if count < pclc_total:
        return PRCResult(
            rule_id="PRC-01",
            status="FAIL",
            message=f"Bundle has {count} PR packets but pclc_total={pclc_total}",
            details={"bundle_pr_packet_count": count, "pclc_total": pclc_total, "pr_packets": pr_packets},
        )
    return PRCResult(
        rule_id="PRC-01",
        status="PASS",
        message=f"Bundle has {count} PR packets >= pclc_total={pclc_total}",
        details={"bundle_pr_packet_count": count, "pclc_total": pclc_total},
    )


def prc_02_each_pclc_package_has_pr_packet_in_bundle(
    bundle_path: str, pclc_packages: list[dict]
) -> PRCResult:
    """PRC-02: Each PCLC package (family/slug) must have a pr-packet.json in bundle."""
    try:
        with zipfile.ZipFile(bundle_path) as zf:
            names = set(zf.namelist())
    except Exception as e:
        return PRCResult(
            rule_id="PRC-02",
            status="FAIL",
            message=f"Could not open bundle: {e}",
            details={"bundle_path": bundle_path},
        )

    missing = []
    for pkg in pclc_packages:
        fam = pkg.get("family", "")
        slug = pkg.get("slug", "")
        # Check if any bundle entry matches pr-packets/{family}/{slug}/pr-packet.json
        expected_suffix = f"pr-packets/{fam}/{slug}/pr-packet.json"
        found = any(n.endswith(expected_suffix) for n in names)
        if not found:
            missing.append(f"{fam}/{slug}")

    if missing:
        return PRCResult(
            rule_id="PRC-02",
            status="FAIL",
            message=f"{len(missing)} PCLC package(s) missing pr-packet.json in bundle",
            details={"missing": missing, "total_checked": len(pclc_packages)},
        )
    return PRCResult(
        rule_id="PRC-02",
        status="PASS",
        message=f"All {len(pclc_packages)} PCLC packages have pr-packet.json in bundle",
        details={"total_checked": len(pclc_packages)},
    )


def run_all_prc(
    bundle_path: str, pclc_total: int, pclc_packages: list[dict]
) -> list[PRCResult]:
    return [
        prc_01_bundle_pr_packet_count_gte_pclc_total(bundle_path, pclc_total),
        prc_02_each_pclc_package_has_pr_packet_in_bundle(bundle_path, pclc_packages),
    ]
