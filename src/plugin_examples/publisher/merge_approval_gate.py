"""Merge approval gate for the example publishing pipeline.

Merging a live PR requires a SEPARATE approval from PR creation.

Design:
    - PR creation uses APPROVE_LIVE_PR (PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL)
    - PR merge uses APPROVE_MERGE_PR (PLUGIN_EXAMPLES_MERGE_PR_APPROVAL)
    - These are intentionally different tokens and different env vars.
    - Reusing APPROVE_LIVE_PR for merge is explicitly rejected.

Merge preconditions (all required):
    1. Explicit family and PR number provided
    2. Approval token = APPROVE_MERGE_PR
    3. Clean-checkout validation evidence exists
    4. PR state = open (verified via GitHub API or evidence)
    5. PR not already merged
    6. Target repo matches family config
    7. No unexpected files in PR
    8. No failing CI checks (if CI is configured)
    9. No multi-PR merge unless each is explicitly listed

Safety:
    - Token value is never stored in evidence files or logs.
    - GITHUB_TOKEN is never used as the approval token.
    - Approval token is read only from CLI arg or env var; never from config files.
"""

from __future__ import annotations

import os

MERGE_APPROVAL_ENV_VAR = "PLUGIN_EXAMPLES_MERGE_PR_APPROVAL"
MERGE_APPROVAL_EXPECTED_VALUE = "APPROVE_MERGE_PR"
MERGE_APPROVAL_REQUIRED = True
MERGE_APPROVAL_MODE = "manual_token"

# Blocked reason constants for merge guards.
BLOCKED_MERGE_APPROVAL_REQUIRED = "blocked_merge_approval_required"
BLOCKED_INVALID_MERGE_APPROVAL = "blocked_invalid_merge_approval"
BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN = "blocked_merge_reused_live_publish_token"
BLOCKED_MERGE_MISSING_FAMILY = "blocked_merge_missing_family"
BLOCKED_MERGE_MISSING_PR_NUMBER = "blocked_merge_missing_pr_number"
BLOCKED_MERGE_WRONG_TARGET_REPO = "blocked_merge_wrong_target_repo"
BLOCKED_MERGE_UNEXPECTED_FILES = "blocked_merge_unexpected_files"
BLOCKED_MERGE_NO_CLEAN_CHECKOUT_EVIDENCE = "blocked_merge_no_clean_checkout_evidence"
BLOCKED_MERGE_PR_NOT_OPEN = "blocked_merge_pr_not_open"
BLOCKED_MERGE_PR_ALREADY_MERGED = "blocked_merge_pr_already_merged"
BLOCKED_MERGE_CI_FAILING = "blocked_merge_ci_failing"

# The live PR approval token — explicitly rejected for merge
_LIVE_PUBLISH_TOKEN = "APPROVE_LIVE_PR"


def check_merge_approval(approval_token: str | None) -> tuple[bool, str]:
    """Check whether a PR merge approval token is valid.

    Reads PLUGIN_EXAMPLES_MERGE_PR_APPROVAL env var as fallback when
    approval_token is None or empty.

    APPROVE_LIVE_PR is explicitly rejected — merge requires a separate
    approval phrase. This prevents accidental reuse of the PR creation token.

    Args:
        approval_token: Token value passed explicitly, or None/empty to read
            from the PLUGIN_EXAMPLES_MERGE_PR_APPROVAL env var.

    Returns:
        Tuple (approved: bool, blocked_reason: str).
        blocked_reason is empty string when approved=True.
    """
    token = approval_token or os.environ.get(MERGE_APPROVAL_ENV_VAR, "")
    if not token:
        return False, BLOCKED_MERGE_APPROVAL_REQUIRED
    # Explicitly reject the live publish token — must use a separate phrase
    if token == _LIVE_PUBLISH_TOKEN:
        return False, BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN
    if token != MERGE_APPROVAL_EXPECTED_VALUE:
        return False, BLOCKED_INVALID_MERGE_APPROVAL
    return True, ""
