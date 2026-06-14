"""
Bundle vs Attestation Validators (BAV-01..BAV-03)

BAV-01: bundle SHA256 in attestation must match computed SHA256 of actual ZIP
BAV-02: bundle entry_count in attestation must match actual ZIP entry count
BAV-03: bundle size_bytes in attestation must match actual ZIP file size
"""

import hashlib
import os
import zipfile
from dataclasses import dataclass, field


@dataclass
class BAVResult:
    rule_id: str
    status: str  # "PASS" | "FAIL"
    message: str
    details: dict = field(default_factory=dict)


def _compute_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def bav_01_bundle_sha_matches_attestation(bundle_path: str, attestation: dict) -> BAVResult:
    """BAV-01: SHA256 of bundle ZIP must match attestation sha256 field."""
    if not os.path.isfile(bundle_path):
        return BAVResult(
            rule_id="BAV-01",
            status="FAIL",
            message=f"Bundle file not found: {bundle_path}",
            details={"bundle_path": bundle_path},
        )
    claimed_sha = attestation.get("sha256")
    if not claimed_sha:
        return BAVResult(
            rule_id="BAV-01",
            status="FAIL",
            message="attestation.sha256 field missing or empty",
            details={"attestation_sha256": None},
        )
    actual_sha = _compute_sha256(bundle_path)
    if actual_sha != claimed_sha:
        return BAVResult(
            rule_id="BAV-01",
            status="FAIL",
            message="Bundle SHA256 does not match attestation sha256",
            details={"actual_sha256": actual_sha, "attestation_sha256": claimed_sha},
        )
    return BAVResult(
        rule_id="BAV-01",
        status="PASS",
        message="Bundle SHA256 matches attestation",
        details={"sha256": actual_sha},
    )


def bav_02_bundle_entry_count_matches_attestation(bundle_path: str, attestation: dict) -> BAVResult:
    """BAV-02: Entry count of bundle ZIP must match attestation entry_count field."""
    if not os.path.isfile(bundle_path):
        return BAVResult(
            rule_id="BAV-02",
            status="FAIL",
            message=f"Bundle file not found: {bundle_path}",
            details={"bundle_path": bundle_path},
        )
    claimed = attestation.get("entry_count")
    if claimed is None:
        return BAVResult(
            rule_id="BAV-02",
            status="FAIL",
            message="attestation.entry_count field missing",
            details={"entry_count": None},
        )
    with zipfile.ZipFile(bundle_path) as zf:
        actual = len(zf.namelist())
    if actual != claimed:
        return BAVResult(
            rule_id="BAV-02",
            status="FAIL",
            message=f"Bundle entry count {actual} != attestation entry_count {claimed}",
            details={"actual_entry_count": actual, "attestation_entry_count": claimed},
        )
    return BAVResult(
        rule_id="BAV-02",
        status="PASS",
        message=f"Bundle entry count {actual} matches attestation",
        details={"entry_count": actual},
    )


def bav_03_bundle_size_matches_attestation(bundle_path: str, attestation: dict) -> BAVResult:
    """BAV-03: File size of bundle ZIP must match attestation size_bytes field."""
    if not os.path.isfile(bundle_path):
        return BAVResult(
            rule_id="BAV-03",
            status="FAIL",
            message=f"Bundle file not found: {bundle_path}",
            details={"bundle_path": bundle_path},
        )
    claimed = attestation.get("size_bytes")
    if claimed is None:
        return BAVResult(
            rule_id="BAV-03",
            status="FAIL",
            message="attestation.size_bytes field missing",
            details={"size_bytes": None},
        )
    actual = os.path.getsize(bundle_path)
    if actual != claimed:
        return BAVResult(
            rule_id="BAV-03",
            status="FAIL",
            message=f"Bundle size {actual} bytes != attestation size_bytes {claimed}",
            details={"actual_size_bytes": actual, "attestation_size_bytes": claimed},
        )
    return BAVResult(
        rule_id="BAV-03",
        status="PASS",
        message=f"Bundle size {actual} bytes matches attestation",
        details={"size_bytes": actual},
    )


def run_all_bav(bundle_path: str, attestation: dict) -> list[BAVResult]:
    return [
        bav_01_bundle_sha_matches_attestation(bundle_path, attestation),
        bav_02_bundle_entry_count_matches_attestation(bundle_path, attestation),
        bav_03_bundle_size_matches_attestation(bundle_path, attestation),
    ]
