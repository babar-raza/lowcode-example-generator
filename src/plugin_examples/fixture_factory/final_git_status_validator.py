"""
Final Git Status Validators (FGS-01..FGS-02)

FGS-01: A final git-status file (not just preflight) must be present in the bundle
FGS-02: The final git-status must not contain any .pfx file paths
"""

import zipfile
from dataclasses import dataclass, field


@dataclass
class FGSResult:
    rule_id: str
    status: str  # "PASS" | "FAIL"
    message: str
    details: dict = field(default_factory=dict)


def _find_final_git_status(names: list[str]) -> list[str]:
    """Find bundle entries that look like a final (post-sprint) git status file."""
    # Must contain 'git-status' and NOT be under 'preflight/'
    candidates = [
        n for n in names
        if "git-status" in n and "preflight" not in n
    ]
    return candidates


def fgs_01_final_git_status_present_in_bundle(bundle_path: str) -> FGSResult:
    """FGS-01: A post-sprint final git-status file must be in the bundle."""
    try:
        with zipfile.ZipFile(bundle_path) as zf:
            names = zf.namelist()
    except Exception as e:
        return FGSResult(
            rule_id="FGS-01",
            status="FAIL",
            message=f"Could not open bundle: {e}",
            details={"bundle_path": bundle_path},
        )

    final_statuses = _find_final_git_status(names)
    if not final_statuses:
        return FGSResult(
            rule_id="FGS-01",
            status="FAIL",
            message="No final git-status file found in bundle (only preflight git-status is present)",
            details={"preflight_only": True, "all_git_status_entries": [n for n in names if "git-status" in n]},
        )
    return FGSResult(
        rule_id="FGS-01",
        status="PASS",
        message=f"Final git-status present: {final_statuses[0]}",
        details={"final_git_status_entries": final_statuses},
    )


def fgs_02_no_pfx_in_final_git_status(bundle_path: str) -> FGSResult:
    """FGS-02: The final git-status must not contain .pfx file references."""
    try:
        with zipfile.ZipFile(bundle_path) as zf:
            names = zf.namelist()
            final_statuses = _find_final_git_status(names)
            if not final_statuses:
                return FGSResult(
                    rule_id="FGS-02",
                    status="FAIL",
                    message="No final git-status file found — cannot check for .pfx",
                    details={"final_git_status": None},
                )
            # Read content of all final git-status files
            pfx_lines = []
            for entry in final_statuses:
                content = zf.read(entry).decode("utf-8", errors="replace")
                for line in content.splitlines():
                    if ".pfx" in line:
                        pfx_lines.append({"entry": entry, "line": line.strip()})
    except Exception as e:
        return FGSResult(
            rule_id="FGS-02",
            status="FAIL",
            message=f"Could not open bundle: {e}",
            details={"bundle_path": bundle_path},
        )

    if pfx_lines:
        return FGSResult(
            rule_id="FGS-02",
            status="FAIL",
            message=f"Final git-status contains {len(pfx_lines)} .pfx reference(s)",
            details={"pfx_lines": pfx_lines},
        )
    return FGSResult(
        rule_id="FGS-02",
        status="PASS",
        message="No .pfx references in final git-status",
        details={"final_git_status_entries": final_statuses},
    )


def run_all_fgs(bundle_path: str) -> list[FGSResult]:
    return [
        fgs_01_final_git_status_present_in_bundle(bundle_path),
        fgs_02_no_pfx_in_final_git_status(bundle_path),
    ]
