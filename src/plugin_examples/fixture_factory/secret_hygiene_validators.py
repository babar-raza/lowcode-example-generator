"""
Secret Hygiene Validators — SHV-01..SHV-03
Wave 16: Detect certificate/secret files in git status that could be accidentally committed.

  SHV-01: Fail if any .pfx file appears as untracked or staged in git status lines.
  SHV-02: Fail if any .pem, .key, or .p12 file appears as untracked or staged.
  SHV-03: Fail if any pattern matching TOKEN or CREDENTIAL appears in staged filenames.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# Secret file extensions that must never be committed/staged/bundled without explicit approval
SECRET_EXTENSIONS = {".pfx", ".pem", ".key", ".p12"}
SECRET_PATTERNS = re.compile(r"\.(pfx|pem|key|p12)$", re.IGNORECASE)
CREDENTIAL_PATTERNS = re.compile(r"(secret|credential|token|password|api.?key)", re.IGNORECASE)


@dataclass
class SHVResult:
    rule_id: str
    passed: bool
    message: str
    detail: dict[str, Any] = field(default_factory=dict)


def _parse_git_status_lines(git_status_text: str) -> list[tuple[str, str]]:
    """Parse git status --short output into (status_code, filename) pairs."""
    entries = []
    for line in git_status_text.splitlines():
        if len(line) < 2:
            continue
        status_code = line[:2].strip()
        filename = line[3:].strip().strip('"')
        entries.append((status_code, filename))
    return entries


def shv_01_no_pfx_untracked_or_staged(git_status_text: str) -> SHVResult:
    """Fail if any .pfx file appears as untracked or staged."""
    entries = _parse_git_status_lines(git_status_text)
    violations = [
        (code, fname) for code, fname in entries
        if fname.lower().endswith(".pfx") and ("?" in code or code not in {"!!", "  "})
    ]
    if violations:
        return SHVResult("SHV-01", False,
            f"{len(violations)} .pfx file(s) untracked or staged: {[f for _, f in violations]}",
            {"violations": [{"status": c, "file": f} for c, f in violations]})
    return SHVResult("SHV-01", True, "No .pfx files untracked or staged")


def shv_02_no_pem_key_p12_untracked_or_staged(git_status_text: str) -> SHVResult:
    """Fail if any .pem, .key, or .p12 files appear as untracked or staged."""
    entries = _parse_git_status_lines(git_status_text)
    violations = [
        (code, fname) for code, fname in entries
        if SECRET_PATTERNS.search(fname) and not fname.lower().endswith(".pfx")
        and ("?" in code or code not in {"!!", "  "})
    ]
    if violations:
        return SHVResult("SHV-02", False,
            f"{len(violations)} secret file(s) untracked or staged: {[f for _, f in violations]}",
            {"violations": [{"status": c, "file": f} for c, f in violations]})
    return SHVResult("SHV-02", True, "No .pem/.key/.p12 files untracked or staged")


def shv_03_no_credential_filenames_staged(git_status_text: str) -> SHVResult:
    """Fail if any staged file name matches credential/token patterns."""
    entries = _parse_git_status_lines(git_status_text)
    staged = [
        (code, fname) for code, fname in entries
        if code and code[0] in {"A", "M"} and CREDENTIAL_PATTERNS.search(fname)
    ]
    if staged:
        return SHVResult("SHV-03", False,
            f"{len(staged)} possibly-sensitive file(s) staged: {[f for _, f in staged]}",
            {"staged": [{"status": c, "file": f} for c, f in staged]})
    return SHVResult("SHV-03", True, "No credential-pattern filenames staged")


def run_all_shv(git_status_text: str) -> list[SHVResult]:
    results = []
    results.append(shv_01_no_pfx_untracked_or_staged(git_status_text))
    results.append(shv_02_no_pem_key_p12_untracked_or_staged(git_status_text))
    results.append(shv_03_no_credential_filenames_staged(git_status_text))
    return results
