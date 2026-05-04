"""Live PR approval gate for the example publishing pipeline.

Live publishing requires explicit human approval via a token that matches
APPROVAL_EXPECTED_VALUE. This is NOT the GitHub PAT — it is a short phrase
the human types to confirm intent.

Usage:
    # Set env var before running with --publish:
    export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
    python -m plugin_examples run --family cells --publish

    # Or pass via CLI flag:
    python -m plugin_examples run --family cells --publish --approval-token APPROVE_LIVE_PR

Design:
    approval_required: true (always — cannot be disabled by config)
    approval_mode: manual_token
    The token value is a known phrase, not a secret. Its purpose is to
    ensure a human explicitly typed it — not that it is confidential.

Safety:
    - GITHUB_TOKEN must never be used as the approval token.
    - Approval token value is never stored in evidence files or logs.
    - No approval via default/empty config values.
    - Monthly runners cannot live publish without explicit token.
"""

from __future__ import annotations

import os

APPROVAL_ENV_VAR = "PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL"
APPROVAL_EXPECTED_VALUE = "APPROVE_LIVE_PR"
APPROVAL_REQUIRED = True
APPROVAL_MODE = "manual_token"

# Blocked reason constants for live publish guards.
# These are used in publisher.py and tests.
BLOCKED_LIVE_PR_APPROVAL_REQUIRED = "blocked_live_pr_approval_required"
BLOCKED_INVALID_LIVE_PR_APPROVAL = "blocked_invalid_live_pr_approval"
BLOCKED_PUBLISH_DRY_RUN_CONFLICT = "blocked_publish_dry_run_conflict"
BLOCKED_PUBLISH_TO_MAIN = "blocked_publish_to_main"
BLOCKED_REPO_ACCESS_NOT_READY = "blocked_repo_access_not_ready"
BLOCKED_PR_PERMISSION_NOT_READY = "blocked_pr_permission_not_ready"


def check_approval(approval_token: str | None) -> tuple[bool, str]:
    """Check whether a live publish approval token is valid.

    Reads PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL env var as fallback when
    approval_token is None or empty. GITHUB_TOKEN is never read here.

    Args:
        approval_token: Token value passed explicitly, or None/empty to read
            from the PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL env var.

    Returns:
        Tuple (approved: bool, blocked_reason: str).
        blocked_reason is empty string when approved=True.
    """
    token = approval_token or os.environ.get(APPROVAL_ENV_VAR, "")
    if not token:
        return False, BLOCKED_LIVE_PR_APPROVAL_REQUIRED
    if token != APPROVAL_EXPECTED_VALUE:
        return False, BLOCKED_INVALID_LIVE_PR_APPROVAL
    return True, ""
