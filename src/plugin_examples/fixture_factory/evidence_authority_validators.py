"""
Evidence Authority Validators — EAV-01..EAV-06
Wave 16: Prevent Wave 15 defect patterns from recurring.

Protocol v2 rules:
  EAV-01: IV cannot be final PASS while current sprint taskcards are PENDING.
  EAV-02: Adversarial review cannot be final PASS while taskcards are PENDING.
  EAV-03: External .sha256 sidecar must exist and content must match pattern.
  EAV-04: External final-attestation.json must exist with all required fields.
  EAV-05: Inside-bundle pre-bundle closeout must NOT claim to be final SHA authority.
  EAV-06: Bundle entry count in attestation must match actual ZIP entry count.
"""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from dataclasses import dataclass, field
from typing import Any


REQUIRED_ATTESTATION_FIELDS = [
    "path",
    "sha256",
    "size_bytes",
    "entry_count",
    "feat_commit",
    "sidecar_path",
    "protocol_version",
]


@dataclass
class EAVResult:
    rule_id: str
    passed: bool
    message: str
    detail: dict[str, Any] = field(default_factory=dict)


def eav_01_iv_not_final_pass_with_pending_taskcards(iv_results: dict, taskcards: dict) -> EAVResult:
    """IV cannot be final PASS while any current sprint taskcard is PENDING."""
    iv_verdict = iv_results.get("verdict", "")
    is_final = iv_results.get("is_final", True)  # default: assume final unless marked PARTIAL

    if not is_final:
        return EAVResult("EAV-01", True, "IV explicitly marked non-final (PARTIAL) — EAV-01 not applicable")

    if iv_verdict != "IV_PASS":
        return EAVResult("EAV-01", True, f"IV verdict is {iv_verdict} (not IV_PASS) — EAV-01 not applicable")

    pending = [t["id"] for t in taskcards.get("taskcards", []) if t.get("status") == "PENDING"]
    if pending:
        return EAVResult(
            "EAV-01",
            False,
            f"IV claims IV_PASS but {len(pending)} taskcards are PENDING: {pending}",
            {"pending_taskcards": pending, "iv_verdict": iv_verdict},
        )

    return EAVResult("EAV-01", True, f"IV_PASS with 0 PENDING taskcards — OK")


def eav_02_ar_not_final_pass_with_pending_taskcards(ar_results: dict, taskcards: dict) -> EAVResult:
    """Adversarial review cannot be final PASS while taskcards are PENDING."""
    ar_verdict = ar_results.get("verdict", "")
    review_type = ar_results.get("review_type", "FINAL")

    if review_type != "FINAL":
        return EAVResult("EAV-02", True, f"AR review_type={review_type} (not FINAL) — EAV-02 not applicable")

    if ar_verdict != "ADVERSARIAL_REVIEW_PASS":
        return EAVResult("EAV-02", True, f"AR verdict is {ar_verdict} (not PASS) — EAV-02 not applicable")

    pending = [t["id"] for t in taskcards.get("taskcards", []) if t.get("status") == "PENDING"]
    if pending:
        return EAVResult(
            "EAV-02",
            False,
            f"Adversarial review FINAL PASS but {len(pending)} taskcards PENDING: {pending}",
            {"pending_taskcards": pending},
        )

    return EAVResult("EAV-02", True, "Adversarial review FINAL PASS with 0 PENDING taskcards — OK")


def eav_03_external_sidecar_exists_and_valid(sidecar_path: str, bundle_path: str) -> EAVResult:
    """External .sha256 sidecar must exist and match bundle SHA."""
    if not os.path.exists(sidecar_path):
        return EAVResult("EAV-03", False, f"External sidecar missing: {sidecar_path}")

    if not os.path.exists(bundle_path):
        return EAVResult("EAV-03", False, f"Bundle missing for sidecar verification: {bundle_path}")

    with open(sidecar_path) as f:
        content = f.read().strip()
    parts = content.split()
    if not parts:
        return EAVResult("EAV-03", False, f"Sidecar is empty: {sidecar_path}")

    sidecar_sha = parts[0]

    sha256 = hashlib.sha256()
    with open(bundle_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    actual_sha = sha256.hexdigest()

    if sidecar_sha != actual_sha:
        return EAVResult(
            "EAV-03",
            False,
            f"Sidecar SHA mismatch: sidecar={sidecar_sha[:16]}..., bundle={actual_sha[:16]}...",
            {"sidecar_sha": sidecar_sha, "bundle_sha": actual_sha},
        )

    return EAVResult("EAV-03", True, f"Sidecar matches bundle: {actual_sha[:16]}...")


def eav_04_external_attestation_exists_and_complete(
    attestation_path: str,
) -> EAVResult:
    """External final-attestation.json must exist with all required fields."""
    if not os.path.exists(attestation_path):
        return EAVResult("EAV-04", False, f"External attestation missing: {attestation_path}")

    try:
        with open(attestation_path) as f:
            attestation = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return EAVResult("EAV-04", False, f"Attestation not readable: {e}")

    missing = [field for field in REQUIRED_ATTESTATION_FIELDS if field not in attestation]
    if missing:
        return EAVResult(
            "EAV-04",
            False,
            f"Attestation missing required fields: {missing}",
            {"missing_fields": missing, "present_fields": list(attestation.keys())},
        )

    protocol = attestation.get("protocol_version", "")
    if protocol != "v2":
        return EAVResult("EAV-04", False, f"Attestation protocol_version={protocol!r} (expected 'v2')")

    return EAVResult(
        "EAV-04",
        True,
        f"Attestation complete with all {len(REQUIRED_ATTESTATION_FIELDS)} required fields, protocol_version=v2",
    )


def eav_05_prebundle_closeout_not_claiming_final_authority(
    bundle_path: str,
) -> EAVResult:
    """Inside-bundle closeout must NOT claim to be final SHA authority (must be PRE_BUNDLE_CLOSEOUT)."""
    if not os.path.exists(bundle_path):
        return EAVResult("EAV-05", False, f"Bundle missing: {bundle_path}")

    with zipfile.ZipFile(bundle_path) as zf:
        names = zf.namelist()
        closeout_entries = [n for n in names if "sprint-closeout" in n and n.endswith(".json")]

        if not closeout_entries:
            # No closeout inside bundle — this is acceptable under protocol v2
            return EAVResult("EAV-05", True, "No sprint-closeout inside bundle (acceptable under protocol v2)")

        for entry in closeout_entries:
            content = json.loads(zf.read(entry))
            closeout_type = content.get("closeout_type", "")
            verdict = content.get("verdict", "")

            # If it claims FINAL authority, fail
            if closeout_type == "FINAL" or (verdict == "SPRINT_COMPLETE" and "sha256" in content):
                sha_in_closeout = content.get("evidence_bundle", {}).get("sha256") or content.get("sha256")
                if sha_in_closeout:
                    return EAVResult(
                        "EAV-05",
                        False,
                        f"Inside-bundle closeout {entry!r} claims final SHA authority: {sha_in_closeout[:16]}... "
                        f"This is the ZIP-contains-own-SHA flaw. Must be labeled PRE_BUNDLE_CLOSEOUT.",
                        {"entry": entry, "sha_in_closeout": sha_in_closeout, "closeout_type": closeout_type},
                    )

    return EAVResult("EAV-05", True, "Inside-bundle closeout(s) do not claim final SHA authority — OK")


def eav_06_bundle_entry_count_matches_attestation(bundle_path: str, attestation_path: str) -> EAVResult:
    """Bundle entry count in attestation must match actual ZIP entry count."""
    if not os.path.exists(bundle_path):
        return EAVResult("EAV-06", False, f"Bundle missing: {bundle_path}")
    if not os.path.exists(attestation_path):
        return EAVResult("EAV-06", False, f"Attestation missing: {attestation_path}")

    with zipfile.ZipFile(bundle_path) as zf:
        actual_entries = len(zf.namelist())

    with open(attestation_path) as f:
        attestation = json.load(f)

    claimed_entries = attestation.get("entry_count")
    if claimed_entries is None:
        return EAVResult("EAV-06", False, "Attestation missing entry_count field")

    if actual_entries != claimed_entries:
        return EAVResult(
            "EAV-06",
            False,
            f"Entry count mismatch: bundle={actual_entries}, attestation={claimed_entries}",
            {"bundle_entries": actual_entries, "attestation_entries": claimed_entries},
        )

    return EAVResult("EAV-06", True, f"Entry count matches: {actual_entries} entries")


def run_all_eav(
    iv_results: dict,
    ar_results: dict,
    taskcards: dict,
    bundle_path: str,
    sidecar_path: str,
    attestation_path: str,
) -> list[EAVResult]:
    """Run all EAV rules and return results list."""
    results = []
    results.append(eav_01_iv_not_final_pass_with_pending_taskcards(iv_results, taskcards))
    results.append(eav_02_ar_not_final_pass_with_pending_taskcards(ar_results, taskcards))
    results.append(eav_03_external_sidecar_exists_and_valid(sidecar_path, bundle_path))
    results.append(eav_04_external_attestation_exists_and_complete(attestation_path))
    results.append(eav_05_prebundle_closeout_not_claiming_final_authority(bundle_path))
    results.append(eav_06_bundle_entry_count_matches_attestation(bundle_path, attestation_path))
    return results
