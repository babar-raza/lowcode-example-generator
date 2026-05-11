# Live PR Approval Gate Preflight Review

**Review date:** 2026-05-01
**Sprint:** Live PR Approval Gate and Safe Branch Probe Sprint
**Purpose:** Confirm prior work state, identify gaps, define approval gate implementation plan

---

## Prior Work Confirmed

| Item | State |
|---|---|
| Cells `repo_access_ready` | `true` |
| Cells `pr_permission_ready` | `true` |
| Cells `live_publish_ready` | `false` |
| Words `repo_access_ready` | `true` |
| Words `pr_permission_ready` | `true` |
| Words `live_publish_ready` | `false` |
| No example content pushed | CONFIRMED |
| No live PR created | CONFIRMED |
| `dry_run=True` enforced in publisher | CONFIRMED |

Evidence source: `workspace/verification/latest/family-repo-access-resolution.json`

---

## Gap Found: No Approval Token Guard

`publisher.py` currently has no approval token check. The live publish path in `publish_examples()` will reach `status = "published"` if:
- `dry_run=False`
- `github_token` is present
- `family_config` is not None
- Target is not a central repo (or `central_repo_allowed=True`)

**Risk:** Any future call with `dry_run=False` and a valid token (e.g., CI misconfiguration, automation bug) would push examples without human sign-off.

**Fix:** Add `approval_gate.py` module with `APPROVAL_EXPECTED_VALUE = "APPROVE_LIVE_PR"` token check. `publish_examples()` must require this token before any live publish proceeds.

---

## `followup-family-repo-initialization` Reassessment

**Original intent:** Initialize repos before PR creation (ensure repos exist and are accessible).

**Current state:** Both repos exist (`isEmpty=false`), accessible, public, `main` branch has `README.md`. The infrastructure prerequisite is already met — the repos do not need initialization.

**Revised intent:** Taskcard should now represent "create live PRs after approval gate closes" rather than "initialize repos." The repos are ready; only the human approval workflow is missing.

**Decision:** Revise taskcard description, keep open until `followup-live-pr-approval-gate` is closed and live PRs are created.

---

## Approval Gate Design

### Token model

| Field | Value |
|---|---|
| `approval_required` | `true` |
| `approval_mode` | `manual_token` |
| Expected value | `APPROVE_LIVE_PR` |
| Env var | `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` |
| CLI flag | `--approval-token <value>` |

### Rules

1. `GITHUB_TOKEN` is **never** the approval token
2. Approval token value is never stored in evidence or logs
3. Approval through default config is not allowed
4. Monthly runner cannot live publish without explicit approval token

### Blocked reasons

| Code | Condition |
|---|---|
| `blocked_live_pr_approval_required` | No approval token provided |
| `blocked_invalid_live_pr_approval` | Wrong approval token value |
| `blocked_publish_dry_run_conflict` | `--dry-run` and `--publish` both set |
| `blocked_publish_to_main` | Branch name would be `main` |
| `blocked_missing_validation_evidence` | Evidence files missing or gate verdict not publishable |
| `blocked_repo_access_not_ready` | `repo_access_ready=False` at time of live publish |
| `blocked_pr_permission_not_ready` | `pr_permission_ready=False` at time of live publish |

---

## Safe Branch/Permission Probe

`probe-publish-permissions` command: read-only GitHub API probe only. Uses `check_repo_access()` (GET requests only). Never creates branches, files, commits, or PRs.

Output: `workspace/verification/latest/publish-permission-probe.json`

---

## Evidence Files

- `workspace/verification/latest/live-pr-approval-preflight-review.json`
- `workspace/verification/latest/live-pr-approval-gate.json` (written after implementation)
- `workspace/verification/latest/publish-permission-probe.json` (written by probe command)
