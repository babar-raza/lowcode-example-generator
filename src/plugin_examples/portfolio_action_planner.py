"""Portfolio Action Planner — computes ranked next actions from current repo state.

Given the current pipeline state (denominators, contracts, configs, release status,
blocker/taskcard state, dirty git state, and approval gate presence), this module
produces a ranked list of safe, actionable next steps for the pipeline agent.

Usage:
    from plugin_examples.portfolio_action_planner import compute_action_board
    board = compute_action_board(repo_root=Path("."))
    for action in board["actions"]:
        if action["safe_to_execute_now"]:
            print(action["id"], action["reason"])
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Action types
# ---------------------------------------------------------------------------

ACTION_TYPES = [
    "CLOSE_PREVIOUS_SPRINT",
    "MERGE_READY_PR",
    "PDF_PR_CONFLICT_RECOVERY",
    "LIVE_PUBLISH_READY_PACKAGE",
    "CONTRACT_BACKFILL",
    "DENOMINATOR_RECONCILIATION",
    "README_RECONCILIATION",
    "TARGET_REPO_HEALTH_REPAIR",
    "VERSION_DRIFT_RERUN",
    "BLOCKER_RETEST",
    "NEW_FAMILY_DISCOVERY",
    "NEXT_EXAMPLE_GENERATION",
    "EVIDENCE_HYGIENE_REPAIR",
    "GOVERNANCE_HARDENING",
    "AI_AUTONOMY_HARDENING",
]

# Families that have active LowCode pilots
ACTIVE_FAMILIES = ("cells", "words", "pdf", "diagram", "email", "slides")

# Families that are in discovery / dependency-blocked state
BLOCKED_FAMILIES = ("ocr", "psd")

ALL_FAMILIES = ACTIVE_FAMILIES + BLOCKED_FAMILIES

# Permanently blocked workflow roots
PERMANENTLY_BLOCKED = {
    "pdf/Timestamp": "External TSA ServerUrl required",
    "pdf/Ofd": "OFD input format, no programmatic fixture",
    "words/Processor": "No public constructor, no static entrypoint (CS1729+CS0120)",
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Action:
    id: str
    family: str
    type: str
    current_state: str
    desired_state: str
    blocker: str | None = None
    approval_required: str | None = None
    gate_present: bool = True
    risk: str = "low"
    impact: int = 0
    safe_to_execute_now: bool = False
    reason: str = ""
    evidence_required: list[str] = field(default_factory=list)
    tests_required: list[str] = field(default_factory=list)
    taskcard_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if d.get("taskcard_id") is None:
            del d["taskcard_id"]
        return d


@dataclass
class ActionBoard:
    generated_at: str = ""
    generated_from_head: str = ""
    git_dirty_summary: str = ""
    actions: list[Action] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "generated_from_head": self.generated_from_head,
            "git_dirty_summary": self.git_dirty_summary,
            "actions": [a.to_dict() for a in self.actions],
            "notes": self.notes,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def safe_actions(self) -> list[Action]:
        return [a for a in self.actions if a.safe_to_execute_now]

    def blocked_actions(self) -> list[Action]:
        return [a for a in self.actions if not a.safe_to_execute_now]

    def metrics_summary(self) -> dict[str, Any]:
        """Return a compact metrics dict suitable for evidence or dashboards."""
        return {
            "generated_at": self.generated_at,
            "generated_from_head": self.generated_from_head,
            "total_actions": len(self.actions),
            "safe_count": len(self.safe_actions()),
            "blocked_count": len(self.blocked_actions()),
            "action_ids": [a.id for a in self.actions],
            "blocked_ids": [a.id for a in self.blocked_actions()],
            "max_impact": max((a.impact for a in self.actions), default=0),
        }


# ---------------------------------------------------------------------------
# State readers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict | None:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _load_denominators(repo_root: Path) -> dict[str, dict]:
    denom_dir = repo_root / "pipeline" / "configs" / "denominators"
    result = {}
    for family in ACTIVE_FAMILIES:
        d = _load_json(denom_dir / f"{family}.json")
        if d:
            result[family] = d
    return result


def _count_contracts(repo_root: Path) -> dict[str, int]:
    contracts_dir = repo_root / "pipeline" / "contracts"
    counts = {}
    for family in ACTIVE_FAMILIES:
        family_dir = contracts_dir / family
        if family_dir.exists():
            counts[family] = len(list(family_dir.glob("*.json")))
        else:
            counts[family] = 0
    return counts


_DIRTY_EXCLUDE_PREFIXES = ("workspace/", "output.", "output/", "input.")
_DIRTY_EXCLUDE_EXACT = {"leg.zip", "test.pfx", "output.json"}


def _check_dirty_state(repo_root: Path) -> list[str]:
    """Return list of dirty source/config/test files (not workspace/evidence/artifacts)."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        )
        dirty = []
        for line in result.stdout.strip().splitlines():
            if not line or len(line) < 4:
                continue
            # Porcelain format: XY PATH — but leading spaces may be stripped
            # by text mode on Windows.  Find the first non-status character.
            # Status chars are in positions 0-1, separator space at position 2.
            # Robust approach: split on first space after status flags.
            path = line.lstrip(" MADRCU?!")[0:0]  # fallback empty
            # Simple: find first occurrence of a path-like char after status
            idx = 0
            while idx < len(line) and line[idx] in " MADRCU?!":
                idx += 1
            path = line[idx:].strip()
            # Handle renames: "R  old -> new"
            if " -> " in path:
                path = path.split(" -> ")[-1]
            if not path:
                continue
            if any(path.startswith(p) for p in _DIRTY_EXCLUDE_PREFIXES):
                continue
            if path in _DIRTY_EXCLUDE_EXACT:
                continue
            dirty.append(path)
        return dirty
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def _get_head_sha(repo_root: Path) -> str:
    """Return the current HEAD short SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unknown"


def _check_gate(env_var: str, expected_value: str) -> bool:
    """Check if an approval gate is set (without logging the value)."""
    return os.environ.get(env_var, "") == expected_value


# ---------------------------------------------------------------------------
# Action generators
# ---------------------------------------------------------------------------

def _gen_dirty_state_actions(dirty_files: list[str]) -> list[Action]:
    if not dirty_files:
        return []
    return [Action(
        id="CLOSE_DIRTY_STATE",
        family="cross-family",
        type="CLOSE_PREVIOUS_SPRINT",
        current_state=f"{len(dirty_files)} dirty source/config/test files",
        desired_state="committed or classified",
        impact=100,
        safe_to_execute_now=True,
        reason="Dirty source files must be resolved before any new work",
        evidence_required=["commit_sha", "git_status"],
    )]


def _gen_merge_actions(denoms: dict[str, dict]) -> list[Action]:
    actions = []
    pdf = denoms.get("pdf", {})
    pr_ready = pdf.get("pr_dry_run_ready_count", 0)
    if pr_ready > 0:
        gate_present = _check_gate(
            "PLUGIN_EXAMPLES_MERGE_PR_APPROVAL", "APPROVE_MERGE_PR"
        )
        actions.append(Action(
            id="PDF_MERGE_PRS",
            family="pdf",
            type="MERGE_READY_PR",
            current_state=f"{pr_ready} examples PR_DRY_RUN_READY",
            desired_state=f"{pdf.get('published_count', 0) + pr_ready} PDF examples published",
            approval_required="PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR",
            gate_present=gate_present,
            risk="medium",
            impact=95,
            safe_to_execute_now=gate_present,
            blocker=None if gate_present else "merge approval gate absent",
            reason="Highest-impact publication action" if gate_present else "Blocked by absent approval gate",
            evidence_required=["pr_status", "merge_report"],
            tests_required=["scenario_contracts", "release_status"],
        ))
    return actions


def _gen_conflict_recovery_actions(denoms: dict[str, dict]) -> list[Action]:
    """Generate PDF PR conflict recovery action if PRs exist and conflicts are likely."""
    pdf = denoms.get("pdf", {})
    pr_ready = pdf.get("pr_dry_run_ready_count", 0)
    if pr_ready <= 0:
        return []
    publish_gate = _check_gate(
        "PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL", "APPROVE_LIVE_PR"
    )
    return [Action(
        id="PDF_PR_CONFLICT_RECOVERY",
        family="pdf",
        type="PDF_PR_CONFLICT_RECOVERY",
        current_state=f"{pr_ready} PR-ready examples, PRs likely CONFLICTING",
        desired_state="PRs rebased or recreated with clean merge state",
        approval_required="PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR",
        gate_present=publish_gate,
        risk="medium",
        impact=92,
        safe_to_execute_now=publish_gate,
        blocker=None if publish_gate else "live publish approval gate absent",
        reason="Conflict recovery must precede merge" if publish_gate else "Blocked by absent publish gate",
        evidence_required=["pr_conflict_analysis", "pr_recreate_report"],
        tests_required=["scenario_contracts"],
        taskcard_id="TC-PDF-PR-CONFLICT-RESOLUTION",
    )]


def _gen_conservation_actions(denoms: dict[str, dict], contract_counts: dict[str, int]) -> list[Action]:
    actions = []
    for family in ACTIVE_FAMILIES:
        d = denoms.get(family, {})
        pilot = d.get("allowed_pilot_count") or d.get("runnable_scenarios", 0)
        contracts = contract_counts.get(family, 0)
        if contracts < pilot:
            actions.append(Action(
                id=f"CONTRACT_BACKFILL_{family.upper()}",
                family=family,
                type="CONTRACT_BACKFILL",
                current_state=f"{contracts} contracts, {pilot} pilot-allowed",
                desired_state=f"{pilot} contracts",
                impact=70,
                safe_to_execute_now=True,
                reason=f"{family} has contract deficit: {contracts} < {pilot}",
                evidence_required=["contract_files"],
                tests_required=["scenario_contracts"],
            ))
    return actions


def _gen_blocker_actions(denoms: dict[str, dict]) -> list[Action]:
    actions = []
    # FormImporter
    pdf = denoms.get("pdf", {})
    pdf_version = pdf.get("source_version", "")
    actions.append(Action(
        id="FORMIMPORTER_RETEST",
        family="pdf",
        type="BLOCKER_RETEST",
        current_state=f"blocked by Aspose.PDF {pdf_version} bug",
        desired_state="retest if newer version available",
        blocker=f"requires Aspose.PDF > {pdf_version}",
        impact=40,
        safe_to_execute_now=True,
        reason="Check-only — verify whether newer Aspose.PDF is available",
        taskcard_id="TC-PDF-FORMIMPORTER-RETEST",
    ))

    # OCR
    actions.append(Action(
        id="OCR_DEPENDENCY_RECHECK",
        family="ocr",
        type="BLOCKER_RETEST",
        current_state="DEPENDENCY_BLOCKED — Aspose.AI.LLM not on NuGet",
        desired_state="recheck availability",
        blocker="internal Aspose assembly",
        impact=30,
        safe_to_execute_now=True,
        reason="Periodic recheck is safe",
        taskcard_id="TC-OCR-REFLECTION",
    ))

    # PSD
    actions.append(Action(
        id="PSD_DEPENDENCY_RECHECK",
        family="psd",
        type="BLOCKER_RETEST",
        current_state="DEPENDENCY_BLOCKED — Aspose.JavaAttributes not on NuGet",
        desired_state="recheck availability",
        blocker="internal Aspose assembly",
        impact=30,
        safe_to_execute_now=True,
        reason="Periodic recheck is safe",
        taskcard_id="TC-PSD-REFLECTION",
    ))

    # Permanently blocked
    actions.append(Action(
        id="PERMANENTLY_BLOCKED_WATCH",
        family="cross-family",
        type="BLOCKER_RETEST",
        current_state=f"{len(PERMANENTLY_BLOCKED)} permanently blocked roots",
        desired_state="confirm no new evidence invalidates blocks",
        impact=20,
        safe_to_execute_now=True,
        reason="Preserve and verify permanent block state",
    ))

    return actions


def _gen_version_drift_actions(denoms: dict[str, dict]) -> list[Action]:
    return [Action(
        id="VERSION_DRIFT_CHECK",
        family="cross-family",
        type="VERSION_DRIFT_RERUN",
        current_state="last checked versions: " + ", ".join(
            f"{f}={denoms.get(f, {}).get('source_version', '?')}" for f in ACTIVE_FAMILIES
        ),
        desired_state="drift status verified",
        impact=60,
        safe_to_execute_now=True,
        reason="Version drift check is safe read-only operation",
        evidence_required=["version-drift-raw"],
        tests_required=["test_version_drift_checker"],
    )]


def _gen_portfolio_check_actions() -> list[Action]:
    return [Action(
        id="PORTFOLIO_CONSERVATION_CHECK",
        family="cross-family",
        type="DENOMINATOR_RECONCILIATION",
        current_state="needs re-verification",
        desired_state="all conservation equations pass",
        impact=75,
        safe_to_execute_now=True,
        reason="Conservation equations must be re-verified after any commit",
        evidence_required=["conservation-check-report"],
        tests_required=["scenario_contracts"],
    )]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def compute_action_board(repo_root: Path) -> ActionBoard:
    """Compute a ranked action board from current repo state."""
    from datetime import datetime, timezone

    # Freshness metadata
    head_sha = _get_head_sha(repo_root)
    dirty_files = _check_dirty_state(repo_root)
    dirty_summary = f"{len(dirty_files)} dirty" if dirty_files else "clean"

    board = ActionBoard(
        generated_at=datetime.now(timezone.utc).isoformat(),
        generated_from_head=head_sha,
        git_dirty_summary=dirty_summary,
    )

    # Read state
    denoms = _load_denominators(repo_root)
    contract_counts = _count_contracts(repo_root)

    # Generate actions from all sources
    all_actions: list[Action] = []
    all_actions.extend(_gen_dirty_state_actions(dirty_files))
    all_actions.extend(_gen_merge_actions(denoms))
    all_actions.extend(_gen_conflict_recovery_actions(denoms))
    all_actions.extend(_gen_portfolio_check_actions())
    all_actions.extend(_gen_conservation_actions(denoms, contract_counts))
    all_actions.extend(_gen_version_drift_actions(denoms))
    all_actions.extend(_gen_blocker_actions(denoms))

    # Sort by impact descending
    all_actions.sort(key=lambda a: a.impact, reverse=True)

    board.actions = all_actions

    # Summary notes
    safe_count = len(board.safe_actions())
    blocked_count = len(board.blocked_actions())
    board.notes.append(f"{safe_count} safe actions, {blocked_count} blocked actions")
    board.notes.append(f"Active families: {len(denoms)}")
    board.notes.append(f"Total contracts: {sum(contract_counts.values())}")

    return board


def render_markdown(board: ActionBoard) -> str:
    """Render the action board as human-readable markdown."""
    lines = [
        "# Next Actions", "",
        f"Generated: {board.generated_at}",
        f"HEAD: {board.generated_from_head}",
        f"Dirty: {board.git_dirty_summary}", "",
    ]
    lines.append("| Rank | ID | Family | Type | Impact | Safe | Blocker |")
    lines.append("|------|----|--------|------|--------|------|---------|")
    for i, a in enumerate(board.actions, 1):
        safe = "YES" if a.safe_to_execute_now else "NO"
        blocker = a.blocker or "-"
        lines.append(f"| {i} | {a.id} | {a.family} | {a.type} | {a.impact} | {safe} | {blocker} |")
    lines.append("")
    for note in board.notes:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)
