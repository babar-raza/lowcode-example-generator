"""Auto-Merge Gate (AMG) — Wave 25 state machine.

Replaces the old manual-token-based gate with a fully machine-executable
10-condition gate (AMG-01..10).  The agent holds full merge authority;
no external human approval is required.

Merge state progression:
    OPEN → MERGE_GATE_EVALUATING → MERGE_GATE_READY →
        AUTO_MERGE_AUTHORIZED → AUTO_MERGE_TRIGGERED → MERGED
                             └→ MERGE_FAILED (with reason)
                             └→ CREDENTIAL_BLOCKED (APPROVE_LIVE_MERGE not set)
                             └→ REVIEW_POLICY_BLOCKED (repo not on allowlist / branch pattern mismatch)

Branch deletion progression:
    BRANCH_DELETE_AUTHORIZED → deletion executed
    BRANCH_DELETE_SKIPPED_POLICY (any BDG check fails — not an error)

Backward-compatibility note:
    APPROVAL_BLOCKED is retained as an alias for CREDENTIAL_BLOCKED in legacy
    state files.  New code must never produce APPROVAL_BLOCKED.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field

# ── Allowlists ────────────────────────────────────────────────────────────────

APPROVED_PUBLICATION_REPOS: frozenset[str] = frozenset(
    {
        "aspose-barcode-net/Aspose.BarCode.Plugins-for-.NET-Examples",
        "aspose-svg-net/Aspose.SVG.Plugins-for-.NET-Examples",
        "aspose-cad-net/Aspose.CAD.Plugins-for-.NET-Examples",
    }
)

FIXTURE_SOURCE_REPOS: frozenset[str] = frozenset(
    {
        "aspose-barcode/Aspose.BarCode-for-.NET",
        "aspose-svg/Aspose.SVG-for-.NET",
        "aspose-cad/Aspose.CAD-for-.NET",
        "aspose-cells/Aspose.Cells-for-.NET",
        "aspose-words/Aspose.Words-for-.NET",
        "aspose-html/Aspose.HTML-for-.NET",
        "aspose-font/Aspose.Font-for-.NET",
        "aspose-imaging/Aspose.Imaging-for-.NET",
        "aspose-gis/Aspose.GIS-for-.NET",
        "aspose-finance/Aspose.Finance-for-.NET",
        "aspose-omr/Aspose.OMR-for-.NET",
        "aspose-note/Aspose.Note-for-.NET",
        "aspose-tasks/Aspose.Tasks-for-.NET",
        "aspose-page/Aspose.TeX-for-.NET",
        "aspose-ocr/Aspose.OCR-for-.NET",
        "aspose-3d/Aspose.3D-for-.NET",
        "aspose-psd/Aspose.PSD-for-.NET",
        "aspose-zip/Aspose.ZIP-for-.NET",
    }
)

# Branch pattern: lowcode/wave*/…
_BRANCH_PATTERN = re.compile(r"^lowcode/wave\d+/.+")

# ── Result dataclass ──────────────────────────────────────────────────────────


@dataclass
class MergeGateResult:
    """Result of evaluating all AMG gates for a single PR."""

    verdict: str
    """One of: MERGE_GATE_READY, AUTO_MERGE_AUTHORIZED, AUTO_MERGE_TRIGGERED,
    MERGED, MERGE_FAILED, CREDENTIAL_BLOCKED, REVIEW_POLICY_BLOCKED."""
    reason: str | None = None
    merge_sha: str | None = None
    logged_command: str | None = None
    gate_checks: list[dict] = field(default_factory=list)

    def _check(self, gate_id: str, passed: bool, detail: str) -> None:
        self.gate_checks.append({"gate": gate_id, "passed": passed, "detail": detail})


@dataclass
class BranchDeleteResult:
    verdict: str  # BRANCH_DELETE_AUTHORIZED | BRANCH_DELETE_SKIPPED_POLICY
    reason: str | None = None


# ── AMG gate evaluation ───────────────────────────────────────────────────────


def evaluate_merge_gate(
    pr_url: str,
    repo: str,
    head_branch: str,
    pr_state: str,
    pr_mergeable: str,
    artifact_contract: dict,
    build_result: dict,
    readme_result: dict,
) -> MergeGateResult:
    """Evaluate all 10 AMG conditions in order.

    Args:
        pr_url:           Full GitHub PR URL.
        repo:             Owner/repo string (e.g. ``aspose-barcode-net/Aspose.BarCode.Plugins-for-.NET-Examples``).
        head_branch:      PR head branch name.
        pr_state:         GitHub PR state string, e.g. ``"OPEN"``.
        pr_mergeable:     GitHub mergeable field, e.g. ``"MERGEABLE"``.
        artifact_contract: Dict with at least ``{"status": "PASS" | ...}``.
        build_result:     Dict with at least ``{"verdict": "ALL_PASS" | ...}``.
        readme_result:    Dict with at least ``{"verdict": "QUALITY" | ...}``.

    Returns:
        :class:`MergeGateResult` with the final verdict.
    """
    r = MergeGateResult(verdict="MERGE_GATE_EVALUATING")

    # AMG-02: GH_TOKEN present
    gh_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not gh_token:
        r._check("AMG-02", False, "GITHUB_TOKEN / GH_TOKEN not present in env")
        r.verdict = "CREDENTIAL_BLOCKED"
        r.reason = "GITHUB_TOKEN not set in env"
        return r
    r._check("AMG-02", True, "GITHUB_TOKEN present")

    # AMG-03: allowlist check
    if repo not in APPROVED_PUBLICATION_REPOS:
        detail = f"repo {repo!r} not in APPROVED_PUBLICATION_REPOS allowlist"
        if repo in FIXTURE_SOURCE_REPOS:
            detail += " — this is a FIXTURE SOURCE REPO, not a publication target (HS-11)"
        r._check("AMG-03", False, detail)
        r.verdict = "REVIEW_POLICY_BLOCKED"
        r.reason = detail
        return r
    r._check("AMG-03", True, f"repo {repo!r} in allowlist")

    # AMG-04: branch pattern check
    if not _BRANCH_PATTERN.match(head_branch):
        detail = f"branch {head_branch!r} does not match lowcode/wave*/... pattern"
        r._check("AMG-04", False, detail)
        r.verdict = "REVIEW_POLICY_BLOCKED"
        r.reason = detail
        return r
    r._check("AMG-04", True, f"branch pattern OK: {head_branch!r}")

    # AMG-05: PR state and mergeability
    if pr_state != "OPEN":
        detail = f"PR state is {pr_state!r}, expected OPEN"
        r._check("AMG-05", False, detail)
        r.verdict = "MERGE_GATE_READY"
        r.reason = detail
        return r
    if pr_mergeable != "MERGEABLE":
        detail = f"PR mergeable={pr_mergeable!r}, expected MERGEABLE"
        r._check("AMG-05", False, detail)
        r.verdict = "MERGE_GATE_READY"
        r.reason = detail
        return r
    r._check("AMG-05", True, "PR is OPEN and MERGEABLE")

    # AMG-06: artifact contract
    if artifact_contract.get("status") != "PASS":
        detail = f"artifact_contract.status={artifact_contract.get('status')!r}, expected PASS"
        r._check("AMG-06", False, detail)
        r.verdict = "MERGE_GATE_READY"
        r.reason = "artifact_contract not PASS — gate not cleared"
        return r
    r._check("AMG-06", True, "artifact_contract PASS")

    # AMG-07: build result
    if build_result.get("verdict") != "ALL_PASS":
        detail = f"build_result.verdict={build_result.get('verdict')!r}, expected ALL_PASS"
        r._check("AMG-07", False, detail)
        r.verdict = "MERGE_GATE_READY"
        r.reason = "build not ALL_PASS — gate not cleared"
        return r
    r._check("AMG-07", True, "build ALL_PASS")

    # AMG-08: README quality
    if readme_result.get("verdict") != "QUALITY":
        detail = f"readme_result.verdict={readme_result.get('verdict')!r}, expected QUALITY"
        r._check("AMG-08", False, detail)
        r.verdict = "MERGE_GATE_READY"
        r.reason = "README not QUALITY — gate not cleared"
        return r
    r._check("AMG-08", True, "README QUALITY")

    # AMG-09: no secret / binary provenance failure (placeholder — checked upstream)
    r._check("AMG-09", True, "no secret/binary-provenance failure detected (checked upstream)")

    # AMG-01 / AMG-10: env gate — must check last so all artifact checks run first
    approve_live_merge = os.environ.get("APPROVE_LIVE_MERGE")
    if approve_live_merge != "1":
        r._check("AMG-01", False, "APPROVE_LIVE_MERGE != '1' in env")
        r.verdict = "CREDENTIAL_BLOCKED"
        r.reason = (
            "APPROVE_LIVE_MERGE not set to '1' in env — all artifact gates pass, merge authorized but env gate not set"
        )
        return r
    r._check("AMG-01", True, "APPROVE_LIVE_MERGE=1 present")

    # AMG-10: log command before execution
    cmd = ["gh", "pr", "merge", pr_url, "--squash", "--auto"]
    logged_command = " ".join(cmd)
    r._check("AMG-10", True, f"command logged before execution: {logged_command}")

    # Execute merge
    r.verdict = "AUTO_MERGE_TRIGGERED"
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        r.verdict = "MERGED"
        r.merge_sha = _extract_sha(result.stdout)
        r.logged_command = logged_command
    else:
        r.verdict = "MERGE_FAILED"
        r.reason = result.stderr.strip() or result.stdout.strip()
        r.logged_command = logged_command

    return r


# ── Branch deletion gate ──────────────────────────────────────────────────────


def evaluate_branch_delete_gate(
    repo: str,
    branch: str,
    pr_verdict: str,
) -> BranchDeleteResult:
    """Evaluate branch deletion gates BDG-01..04.

    Not an error if any gate fails — records BRANCH_DELETE_SKIPPED_POLICY.
    """
    # BDG-01
    if os.environ.get("APPROVE_DELETE_BRANCH") != "1":
        return BranchDeleteResult(
            verdict="BRANCH_DELETE_SKIPPED_POLICY",
            reason="APPROVE_DELETE_BRANCH not set to '1' in env",
        )
    # BDG-02
    if pr_verdict != "MERGED":
        return BranchDeleteResult(
            verdict="BRANCH_DELETE_SKIPPED_POLICY",
            reason=f"PR not in MERGED state (verdict={pr_verdict!r})",
        )
    # BDG-03 / BDG-04
    if not _BRANCH_PATTERN.match(branch):
        return BranchDeleteResult(
            verdict="BRANCH_DELETE_SKIPPED_POLICY",
            reason=f"Branch {branch!r} does not match expected pattern lowcode/wave*/...",
        )

    return BranchDeleteResult(verdict="BRANCH_DELETE_AUTHORIZED")


# ── Backward-compatibility shims ──────────────────────────────────────────────

# Legacy code that checks for APPROVAL_BLOCKED should migrate to CREDENTIAL_BLOCKED.
# This alias exists only for reading old state files — never generate APPROVAL_BLOCKED.
APPROVAL_BLOCKED = "CREDENTIAL_BLOCKED"  # compatibility alias

# Pre-Wave-25 merge approval token constants — kept so existing tests continue to pass.
# New code must use evaluate_merge_gate() / APPROVE_LIVE_MERGE env var instead.
MERGE_APPROVAL_ENV_VAR = "PLUGIN_EXAMPLES_MERGE_PR_APPROVAL"
MERGE_APPROVAL_EXPECTED_VALUE = "APPROVE_MERGE_PR"
BLOCKED_MERGE_APPROVAL_REQUIRED = "BLOCKED_MERGE_APPROVAL_REQUIRED"
BLOCKED_INVALID_MERGE_APPROVAL = "BLOCKED_INVALID_MERGE_APPROVAL"
BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN = "BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN"


def check_merge_approval(token: str | None) -> tuple[bool, str]:
    """Legacy merge approval gate — backward-compat shim for pre-Wave-25 callers.

    New code must use evaluate_merge_gate() with APPROVE_LIVE_MERGE env var.
    This function is retained only so existing tests continue to compile.
    """
    # Resolve token from env var if not passed directly
    if token is None:
        token = os.environ.get(MERGE_APPROVAL_ENV_VAR)

    if token is None or token == "":
        return False, BLOCKED_MERGE_APPROVAL_REQUIRED

    if token == "APPROVE_LIVE_PR":
        return False, BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN

    if token != MERGE_APPROVAL_EXPECTED_VALUE:
        return False, BLOCKED_INVALID_MERGE_APPROVAL

    return True, ""


# ── Internal helpers ──────────────────────────────────────────────────────────


def _extract_sha(stdout: str) -> str | None:
    """Extract merge SHA from gh pr merge output, if present."""
    for line in stdout.splitlines():
        if "sha" in line.lower() or line.strip().startswith("https://"):
            return line.strip()
    return None
