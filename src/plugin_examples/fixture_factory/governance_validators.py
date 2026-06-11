"""
Governance artifact validators (GOV-01..GOV-06).

These validators ensure that key governance, ownership, and operational
artifacts are present and non-empty in the repository. They run as part
of sprint closeout to prevent silent regression of governance quality.

Each validator follows the standard (context: dict) -> list[dict] signature
used by the evidence validator rule engine.

Validator IDs:
  GOV-01  CODEOWNERS file is present and non-empty
  GOV-02  CHANGELOG.md is present and contains current project version
  GOV-03  ADR directory exists with at least one ADR file
  GOV-04  Incident response document is present
  GOV-05  SLA document is present
  GOV-06  Release process document is present
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _finding(
    validator_id: str,
    title: str,
    severity: str,
    description: str,
    evidence_path: str = "",
) -> dict[str, Any]:
    return {
        "validator_id": validator_id,
        "title": title,
        "severity": severity,
        "description": description,
        "evidence_path": evidence_path,
        "status": "FAIL",
    }


def _pass(validator_id: str, title: str, evidence_path: str = "") -> dict[str, Any]:
    return {
        "validator_id": validator_id,
        "title": title,
        "severity": "info",
        "description": "OK",
        "evidence_path": evidence_path,
        "status": "PASS",
    }


# ---------------------------------------------------------------------------
# GOV-01 — CODEOWNERS
# ---------------------------------------------------------------------------

def validate_codeowners(context: dict) -> list[dict]:
    """GOV-01: CODEOWNERS file must be present and non-empty.

    A missing or empty CODEOWNERS file means there is no declared code
    ownership, which lowers the project's governance/readiness score.
    """
    repo_root = Path(context.get("repo_root", "."))
    codeowners = repo_root / ".github" / "CODEOWNERS"

    if not codeowners.exists():
        return [_finding(
            "GOV-01",
            "CODEOWNERS missing",
            "error",
            f"Expected {codeowners} to exist. Add a CODEOWNERS file under .github/.",
            str(codeowners),
        )]

    content = codeowners.read_text(encoding="utf-8").strip()
    if not content or all(line.startswith("#") for line in content.splitlines() if line.strip()):
        return [_finding(
            "GOV-01",
            "CODEOWNERS is empty or comment-only",
            "error",
            "CODEOWNERS exists but contains no ownership rules. Add at least one path rule.",
            str(codeowners),
        )]

    return [_pass("GOV-01", "CODEOWNERS present and non-empty", str(codeowners))]


# ---------------------------------------------------------------------------
# GOV-02 — CHANGELOG.md with current version
# ---------------------------------------------------------------------------

def validate_changelog(context: dict) -> list[dict]:
    """GOV-02: CHANGELOG.md must be present and reference the current version.

    CHANGELOG.md is a primary R3 (Released) signal. It must exist and contain
    an entry for the current project version.
    """
    repo_root = Path(context.get("repo_root", "."))
    changelog = repo_root / "CHANGELOG.md"
    version = context.get("project_version", "")

    if not changelog.exists():
        return [_finding(
            "GOV-02",
            "CHANGELOG.md missing",
            "error",
            f"Expected {changelog}. Create a CHANGELOG.md following Keep a Changelog format.",
            str(changelog),
        )]

    content = changelog.read_text(encoding="utf-8")
    if not content.strip():
        return [_finding(
            "GOV-02",
            "CHANGELOG.md is empty",
            "error",
            "CHANGELOG.md exists but is empty. Add release notes.",
            str(changelog),
        )]

    if version and f"[{version}]" not in content:
        return [_finding(
            "GOV-02",
            f"CHANGELOG.md missing entry for version {version}",
            "warning",
            f"Current version is {version} but CHANGELOG.md has no entry for [{version}].",
            str(changelog),
        )]

    return [_pass("GOV-02", "CHANGELOG.md present with version entry", str(changelog))]


# ---------------------------------------------------------------------------
# GOV-03 — ADR directory
# ---------------------------------------------------------------------------

def validate_adr_directory(context: dict) -> list[dict]:
    """GOV-03: docs/adr/ directory must exist with at least one ADR file.

    ADRs are an explicit R5 (Auditable) requirement. Without them, the
    readiness score cannot reach R5.
    """
    repo_root = Path(context.get("repo_root", "."))
    adr_dir = repo_root / "docs" / "adr"

    if not adr_dir.exists() or not adr_dir.is_dir():
        return [_finding(
            "GOV-03",
            "ADR directory missing",
            "warning",
            f"Expected {adr_dir}. Create docs/adr/ with at least one ADR-NNN-*.md file.",
            str(adr_dir),
        )]

    adr_files = [f for f in adr_dir.glob("ADR-*.md")]
    if not adr_files:
        return [_finding(
            "GOV-03",
            "ADR directory empty — no ADR-*.md files found",
            "warning",
            "docs/adr/ exists but contains no ADR-NNN-*.md files.",
            str(adr_dir),
        )]

    return [_pass("GOV-03", f"ADR directory present with {len(adr_files)} ADR(s)", str(adr_dir))]


# ---------------------------------------------------------------------------
# GOV-04 — Incident response document
# ---------------------------------------------------------------------------

def validate_incident_response(context: dict) -> list[dict]:
    """GOV-04: docs/operations/incident-response.md must be present.

    Incident response documentation is an R6 (Controlled) signal. Without it,
    the readiness score cannot reach R6.
    """
    repo_root = Path(context.get("repo_root", "."))
    ir_doc = repo_root / "docs" / "operations" / "incident-response.md"

    if not ir_doc.exists():
        return [_finding(
            "GOV-04",
            "Incident response document missing",
            "warning",
            f"Expected {ir_doc}. Create docs/operations/incident-response.md.",
            str(ir_doc),
        )]

    content = ir_doc.read_text(encoding="utf-8").strip()
    if len(content) < 200:
        return [_finding(
            "GOV-04",
            "Incident response document is too short (< 200 chars)",
            "warning",
            "incident-response.md exists but may be a placeholder. Add triage steps and escalation paths.",
            str(ir_doc),
        )]

    return [_pass("GOV-04", "Incident response document present", str(ir_doc))]


# ---------------------------------------------------------------------------
# GOV-05 — SLA document
# ---------------------------------------------------------------------------

def validate_sla(context: dict) -> list[dict]:
    """GOV-05: docs/operations/sla.md must be present.

    SLA documentation is an R4 (Governed) signal — it evidences that the
    project has defined measurable service targets.
    """
    repo_root = Path(context.get("repo_root", "."))
    sla_doc = repo_root / "docs" / "operations" / "sla.md"

    if not sla_doc.exists():
        return [_finding(
            "GOV-05",
            "SLA document missing",
            "warning",
            f"Expected {sla_doc}. Create docs/operations/sla.md with measurable SLOs.",
            str(sla_doc),
        )]

    return [_pass("GOV-05", "SLA document present", str(sla_doc))]


# ---------------------------------------------------------------------------
# GOV-06 — Release process document
# ---------------------------------------------------------------------------

def validate_release_process(context: dict) -> list[dict]:
    """GOV-06: docs/operations/release-process.md must be present.

    A documented release process is an R3 (Released) signal. CHANGELOG.md
    alone does not prove there is a repeatable release process.
    """
    repo_root = Path(context.get("repo_root", "."))
    rp_doc = repo_root / "docs" / "operations" / "release-process.md"

    if not rp_doc.exists():
        return [_finding(
            "GOV-06",
            "Release process document missing",
            "warning",
            f"Expected {rp_doc}. Create docs/operations/release-process.md.",
            str(rp_doc),
        )]

    return [_pass("GOV-06", "Release process document present", str(rp_doc))]


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------

ALL_GOVERNANCE_VALIDATORS = [
    validate_codeowners,
    validate_changelog,
    validate_adr_directory,
    validate_incident_response,
    validate_sla,
    validate_release_process,
]


def run_all_governance_validators(context: dict) -> list[dict]:
    """Run all GOV-01..GOV-06 validators and return combined findings."""
    results: list[dict] = []
    for validator in ALL_GOVERNANCE_VALIDATORS:
        results.extend(validator(context))
    return results
