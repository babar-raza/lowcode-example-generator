# Live PR Approval Gate — Implementation Review

**Review date:** 2026-05-01
**Sprint reviewed:** Live PR Approval Gate and Safe Branch Probe Sprint
**Reviewer sprint:** Live PR Approval Gate Implementation Review and Agent-Operated PR Readiness Sprint
**Overall verdict:** PARTIALLY_COMPLETE

---

## Summary

All approval gate guards are correctly implemented and tested. The `probe-publish-permissions` command is read-only. 11 tests in `TestLivePRApprovalGate` pass.

**Critical weakness:** `publisher.py` line 185 contains `result.status = "published"` with no actual branch creation, commit, or PR operation. This is a stub — it returns success without doing anything.

**Additional weaknesses fixed this sprint:**
- `PR_SUMMARY.md` in Words package referenced outdated central target (fixed)
- `pr_builder.py` PR body used generic evidence text without file paths (fixed)
- No `publish-pr` simulation command existed (added)

---

## Claim Audit — 16 Items

| ID | Claim | Verdict | Risk | Fix Required |
|---|---|---|---|---|
| C01 | `approval_gate.py` created with correct constants | VERIFIED | NONE | No |
| C02 | `check_approval(None)` returns `blocked_live_pr_approval_required` | VERIFIED | NONE | No |
| C03 | `check_approval("wrong")` returns `blocked_invalid_live_pr_approval` | VERIFIED | NONE | No |
| C04 | GITHUB_TOKEN never read by `check_approval()` | VERIFIED | NONE | No |
| C05 | `publish_examples()` accepts all three new parameters | VERIFIED | NONE | No |
| C06 | CLI blocks `--dry-run + --publish` | VERIFIED | LOW | No |
| C07 | Publisher blocks `blocked_publish_to_main` | VERIFIED | NONE | No |
| C08 | Publisher blocks `blocked_repo_access_not_ready` | VERIFIED | NONE | No |
| C09 | Publisher blocks `blocked_pr_permission_not_ready` | VERIFIED | NONE | No |
| C10 | `probe-publish-permissions` is always read-only | VERIFIED | NONE | No |
| C11 | Probe output contains `probe_is_read_only=True`, `live_publish_authorized=False` | VERIFIED | NONE | No |
| C12 | 11 tests in `TestLivePRApprovalGate` pass | VERIFIED | NONE | No |
| C13 | `family-publish-readiness.json` shows correct `blocked_reason` | VERIFIED | NONE | No |
| C14 | `followup-live-pr-approval-gate` taskcard closed | VERIFIED | NONE | No |
| C15 | Approval token never stored in evidence or logs | VERIFIED | NONE | No |
| C16 | Publisher implements actual branch/commit/PR creation | **FAILED** | HIGH | **Yes** |

---

## Critical Finding: Publisher Stub (C16)

**File:** `src/plugin_examples/publisher/publisher.py`
**Line:** 185
**Code:** `result.status = "published"`

After all guards pass (approval gate, branch check, repo_access_ready, pr_permission_ready, family_config, central repo check, github_token), the code returns `status="published"` with no actual GitHub operations.

**Risk:** If this code path is reached (dry_run=False, valid token, valid approval), it claims success but creates nothing. The PR never exists.

**Resolution:** `publish-pr` command added with dry-run simulation mode. Real live PR creation (branch, commit, `gh pr create`) is deferred to `followup-agent-operated-live-pr-creation` sprint. The stub line itself is left in place as an intentional placeholder — it will be replaced when the agent-operated PR creation is implemented.

---

## Additional Weaknesses Found and Fixed

### W01: Words PR_SUMMARY.md — Wrong Target Repo

**File:** `workspace/pr-dry-run/words-controlled-pilot/PR_SUMMARY.md`
**Before:** `aspose/aspose-plugins-examples-dotnet (branch: main)`
**After:** `aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples (branch: main)`
**Fix status:** FIXED this sprint

### W02: pr_builder.py — Generic Evidence Text

**File:** `src/plugin_examples/publisher/pr_builder.py`
**Before:** Generic bullet list without file paths
**After:** Includes specific evidence file path references per family
**Fix status:** FIXED this sprint

### W03: No publish-pr Command

**File:** `src/plugin_examples/__main__.py`
**Before:** No `publish-pr` subparser
**After:** `publish-pr --family FAMILY --dry-run [--approval-token VALUE] [--promote-latest]` added
**Fix status:** FIXED this sprint

---

## Current Publish State After This Sprint

| Family | config_ready | repo_access_ready | pr_permission_ready | live_publish_ready | blocked_reason |
|---|---|---|---|---|---|
| cells | true | true | true | false | blocked_live_pr_approval_required |
| words | true | true | true | false | blocked_live_pr_approval_required |
| pdf | false | false | false | false | blocked_family_not_active |

---

## What Must Happen Before Live PR

1. Human provides explicit approval: set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`
2. Agent creates the live PRs using the approved, repeatable pipeline
3. `followup-agent-operated-live-pr-creation` taskcard is the gating item

---

## Evidence Files

- `workspace/verification/latest/live-pr-approval-implementation-review.json`
- `workspace/verification/latest/live-pr-approval-gate.json`
- `workspace/verification/latest/publish-permission-probe.json`
- `workspace/verification/latest/family-publish-readiness.json`
