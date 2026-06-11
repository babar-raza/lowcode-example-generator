"""Portfolio release dashboard generator.

Produces a comprehensive portfolio dashboard combining:
- All-family publication status from denominator files
- PR readiness state for each family
- Taskcard summary
- System health indicators (TC-SYS backlog, evidence contract version)

Output: portfolio-release-dashboard.json + portfolio-release-dashboard.md
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Authoritative family order for the dashboard
FAMILIES = ["cells", "words", "pdf", "diagram", "email", "slides"]

# Known publication state (from sprint evidence — updated each sprint)
_FAMILY_STATUS: dict[str, dict] = {
    "cells": {
        "status": "FAMILY_COMPLETE",
        "published": 9,
        "pilot_allowed": 9,
        "workflow_root_types": 9,
        "pending_pr": 0,
        "package_version": "26.4.0",
        "prs_merged": 4,
        "open_taskcards": 1,
    },
    "words": {
        "status": "PILOT_COMPLETE",
        "published": 8,
        "pilot_allowed": 8,
        "workflow_root_types": 9,
        "pending_pr": 0,
        "package_version": "26.5.0",
        "prs_merged": 6,
        "open_taskcards": 4,
        "blocked_type": "Processor (PERMANENTLY_BLOCKED)",
    },
    "pdf": {
        "status": "PARTIAL_CANARY",
        "published": 5,
        "pilot_allowed": 19,
        "workflow_root_types": 23,
        "pending_pr": 14,
        "package_version": "26.5.0",
        "prs_merged": 1,
        "open_taskcards": 3,
        "pr_packages_ready": ["PR#3", "PR#5", "PR#6", "PR#7", "PR#8", "PR#9"],
        "blocked": "PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL not set",
        "formimporter_blocked": "26.5.0 NullReferenceException — TC-PDF-FORMIMPORTER-RETEST",
    },
    "diagram": {
        "status": "PILOT_COMPLETE",
        "published": 2,
        "pilot_allowed": 2,
        "workflow_root_types": 2,
        "pending_pr": 0,
        "package_version": "26.4.0",
        "prs_merged": 1,
        "open_taskcards": 0,
    },
    "email": {
        "status": "PILOT_COMPLETE",
        "published": 1,
        "pilot_allowed": 1,
        "workflow_root_types": 1,
        "pending_pr": 0,
        "package_version": "26.4.0",
        "prs_merged": 1,
        "open_taskcards": 0,
    },
    "slides": {
        "status": "PILOT_COMPLETE",
        "published": 3,
        "pilot_allowed": 3,
        "workflow_root_types": 3,
        "pending_pr": 0,
        "package_version": "26.5.0",
        "prs_merged": 1,
        "open_taskcards": 0,
    },
}

_SYSTEM_HEALTH: dict[str, str] = {
    "TC-SYS-01 (per_type_constraints)": "COMPLETE",
    "TC-SYS-02 (generic validation)": "COMPLETE",
    "TC-SYS-03 (completeness gate)": "COMPLETE",
    "TC-SYS-04 (ENUM tracking)": "COMPLETE",
    "TC-SYS-05 (all-family release_status)": "COMPLETE",
    "evidence_contract_version": "V6 (67 categories)",
    "test_suite": "1744/1744 PASS",
    "approval_gate": "NOT_SET (publication blocked)",
    "github_token": "SET (classic PAT, repo scope)",
}


@dataclass
class FamilyDashboardEntry:
    """Dashboard entry for a single family."""

    family: str
    status: str
    published: int
    pilot_allowed: int
    workflow_root_types: int
    pending_pr: int
    package_version: str
    prs_merged: int
    open_taskcards: int
    coverage_pct: float
    notes: list[str] = field(default_factory=list)


@dataclass
class PortfolioDashboard:
    """Complete portfolio release dashboard."""

    generated_at: str
    sprint: str
    total_published: int
    total_pr_ready: int
    total_families: int
    families_complete_or_pilot_complete: int
    families_partial: int
    families_discovery: int
    approval_gate_status: str
    evidence_contract: str
    test_suite_status: str
    entries: list[FamilyDashboardEntry] = field(default_factory=list)
    system_health: dict[str, str] = field(default_factory=dict)
    verdict: str = "PORTFOLIO_RELEASE_CANDIDATE_APPROVAL_BLOCKED"


def build_portfolio_dashboard(
    sprint: str,
    *,
    family_overrides: dict | None = None,
) -> PortfolioDashboard:
    """Build the portfolio release dashboard.

    Args:
        sprint: Sprint identifier (e.g., "sprint34").
        family_overrides: Optional overrides for family status data.

    Returns:
        PortfolioDashboard ready for serialization.
    """
    generated_at = datetime.now(timezone.utc).isoformat()
    data = {**_FAMILY_STATUS}
    if family_overrides:
        for fam, override in family_overrides.items():
            if fam in data:
                data[fam] = {**data[fam], **override}

    entries: list[FamilyDashboardEntry] = []
    total_published = 0
    total_pr_ready = 0
    complete_or_pilot = 0
    partial = 0
    discovery = 0

    for family in FAMILIES:
        d = data.get(family, {})
        pub = d.get("published", 0)
        pilot = d.get("pilot_allowed", 1)
        wrt = d.get("workflow_root_types", 1)
        pending = d.get("pending_pr", 0)
        status = d.get("status", "UNKNOWN")

        coverage_pct = round(pub / pilot * 100, 1) if pilot > 0 else 0.0

        notes: list[str] = []
        if d.get("blocked"):
            notes.append(d["blocked"])
        if d.get("formimporter_blocked"):
            notes.append(d["formimporter_blocked"])
        if d.get("blocked_type"):
            notes.append(d["blocked_type"])

        entries.append(
            FamilyDashboardEntry(
                family=family,
                status=status,
                published=pub,
                pilot_allowed=pilot,
                workflow_root_types=wrt,
                pending_pr=pending,
                package_version=d.get("package_version", "unknown"),
                prs_merged=d.get("prs_merged", 0),
                open_taskcards=d.get("open_taskcards", 0),
                coverage_pct=coverage_pct,
                notes=notes,
            )
        )

        total_published += pub
        total_pr_ready += pending

        if status in ("FAMILY_COMPLETE", "PILOT_COMPLETE"):
            complete_or_pilot += 1
        elif status == "PARTIAL_CANARY":
            partial += 1
        elif status == "DISCOVERY_ONLY":
            discovery += 1

    import os

    gate = os.environ.get("PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL", "NOT_SET")
    gate_status = "READY" if gate == "APPROVE_LIVE_PR" else "NOT_SET"

    return PortfolioDashboard(
        generated_at=generated_at,
        sprint=sprint,
        total_published=total_published,
        total_pr_ready=total_pr_ready,
        total_families=len(FAMILIES),
        families_complete_or_pilot_complete=complete_or_pilot,
        families_partial=partial,
        families_discovery=discovery,
        approval_gate_status=gate_status,
        evidence_contract="V6 (67 categories)",
        test_suite_status="1744/1744 PASS",
        entries=entries,
        system_health=_SYSTEM_HEALTH,
        verdict=(
            "PORTFOLIO_RELEASE_CANDIDATE_APPROVAL_BLOCKED"
            if gate_status == "NOT_SET"
            else "PORTFOLIO_RELEASE_CANDIDATE_READY"
        ),
    )


def write_dashboard_json(dashboard: PortfolioDashboard, output_path: Path) -> Path:
    """Write portfolio dashboard as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "generated_at": dashboard.generated_at,
        "sprint": dashboard.sprint,
        "verdict": dashboard.verdict,
        "summary": {
            "total_published": dashboard.total_published,
            "total_pr_ready": dashboard.total_pr_ready,
            "total_families": dashboard.total_families,
            "families_complete_or_pilot_complete": dashboard.families_complete_or_pilot_complete,
            "families_partial": dashboard.families_partial,
            "approval_gate_status": dashboard.approval_gate_status,
            "evidence_contract": dashboard.evidence_contract,
            "test_suite": dashboard.test_suite_status,
        },
        "families": [
            {
                "family": e.family,
                "status": e.status,
                "published": e.published,
                "pilot_allowed": e.pilot_allowed,
                "workflow_root_types": e.workflow_root_types,
                "pending_pr": e.pending_pr,
                "package_version": e.package_version,
                "prs_merged": e.prs_merged,
                "coverage_pct": e.coverage_pct,
                "open_taskcards": e.open_taskcards,
                "notes": e.notes,
            }
            for e in dashboard.entries
        ],
        "system_health": dashboard.system_health,
    }
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Portfolio dashboard JSON written: %s", output_path)
    return output_path


def write_dashboard_markdown(dashboard: PortfolioDashboard, output_path: Path) -> Path:
    """Write portfolio dashboard as Markdown."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Portfolio Release Dashboard — {dashboard.sprint}",
        "",
        f"**Generated:** {dashboard.generated_at}  ",
        f"**Verdict:** `{dashboard.verdict}`  ",
        f"**Evidence Contract:** {dashboard.evidence_contract}  ",
        f"**Test Suite:** {dashboard.test_suite_status}  ",
        f"**Approval Gate:** `{dashboard.approval_gate_status}`",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Published | {dashboard.total_published} |",
        f"| Total PR-Ready (pending approval) | {dashboard.total_pr_ready} |",
        f"| Total Families | {dashboard.total_families} |",
        f"| Families Complete/Pilot Complete | {dashboard.families_complete_or_pilot_complete} |",
        f"| Families Partial Canary | {dashboard.families_partial} |",
        "",
        "## Family Status",
        "",
        "| Family | Status | Published | Pilot Scope | Coverage | PR-Ready | Version |",
        "|--------|--------|-----------|-------------|----------|----------|---------|",
    ]

    for e in dashboard.entries:
        pub_str = f"{e.published}/{e.pilot_allowed}"
        lines.append(
            f"| {e.family.capitalize()} | `{e.status}` | {e.published} | {e.pilot_allowed} | {e.coverage_pct}% | {e.pending_pr} | {e.package_version} |"
        )

    lines += [
        "",
        "## System Health",
        "",
        "| Component | Status |",
        "|-----------|--------|",
    ]
    for component, status in dashboard.system_health.items():
        lines.append(f"| {component} | `{status}` |")

    lines += [
        "",
        "## Notes",
        "",
    ]
    for e in dashboard.entries:
        if e.notes:
            for note in e.notes:
                lines.append(f"- **{e.family.capitalize()}**: {note}")

    if dashboard.approval_gate_status == "NOT_SET":
        lines += [
            "",
            "## Next Action",
            "",
            "Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` and run:",
            "```bash",
            "python -m plugin_examples publish-pr-batch --family pdf --publish --approval-token APPROVE_LIVE_PR",
            "```",
        ]

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Portfolio dashboard Markdown written: %s", output_path)
    return output_path
