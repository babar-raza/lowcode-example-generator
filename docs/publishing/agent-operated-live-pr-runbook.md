# Agent-Operated Live PR Creation Runbook

**Version:** 1.0
**Date:** 2026-05-01
**Sprint:** Live PR Approval Gate Implementation Review and Agent-Operated PR Readiness Sprint
**Status:** READY — pending human approval

---

## Overview

Live PRs are **not created by humans manually**. After human provides explicit approval, the **agent creates the PRs** using the approved, repeatable pipeline. This runbook defines the exact sequence.

**Human role:** Provide explicit approval token. Review and merge PRs after agent creates them.
**Agent role:** Validate prerequisites, run simulation, execute live PR creation, record evidence.

---

## Prerequisites (All Must Be True)

| Prerequisite | Check Command | Expected Result |
|---|---|---|
| Cells package assembled | `ls workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/` | 9 directories |
| Words package assembled | `ls workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/` | 4 directories |
| Gate verdict OK | `cat workspace/verification/latest/gate-results.json \| jq .verdict` | `PR_DRY_RUN_READY` |
| Repo access ready | `python -m plugin_examples validate-publish-targets --families cells words` | 2/2 ready |
| Permission probe | `python -m plugin_examples probe-publish-permissions --families cells words --promote-latest` | 2/2 PUSH_READY |
| Simulation passes | `python -m plugin_examples publish-pr --family cells --dry-run --promote-latest` | SIMULATION_PASSED |
| Simulation passes | `python -m plugin_examples publish-pr --family words --dry-run --promote-latest` | SIMULATION_PASSED |
| GITHUB_TOKEN set | `echo $GITHUB_TOKEN \| head -c 4` | Non-empty (never print full token) |
| Human approval set | `echo $PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | `APPROVE_LIVE_PR` |

---

## Step 1 — Run Pre-PR Audit (Agent Executes)

```bash
PYTHONPATH=src python -m plugin_examples validate-publish-targets \
    --families cells words pdf --promote-latest

PYTHONPATH=src python -m plugin_examples probe-publish-permissions \
    --families cells words --promote-latest
```

Verify output:
- `validate-publish-targets`: 2/2 ready (cells=READY, words=READY)
- `probe-publish-permissions`: 2/2 PUSH_READY, `live_publish_authorized: false`

---

## Step 2 — Run Simulation (Agent Executes)

```bash
PYTHONPATH=src python -m plugin_examples publish-pr \
    --family words --dry-run --promote-latest

PYTHONPATH=src python -m plugin_examples publish-pr \
    --family cells --dry-run --promote-latest
```

Both must output `SIMULATION_PASSED`. Review:
- `workspace/verification/latest/words-live-pr-simulation.json`
- `workspace/verification/latest/cells-live-pr-simulation.json`

---

## Step 3 — Human Approval

**Human action required.** No automation can substitute for this step.

1. Review the simulation outputs (Step 2)
2. Review the dry-run packages:
   - `workspace/pr-dry-run/words-controlled-pilot/`
   - `workspace/pr-dry-run/cells-controlled-pilot/`
3. Confirm the PR titles match expected:
   - `feat(words): add 4 plugin examples (v26.4.0)`
   - `feat(cells): add 9 plugin examples (v26.4.0)`
4. Set the approval environment variable:
   ```bash
   export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
   export GITHUB_TOKEN=<your_token>
   ```
5. Document sign-off (record date, reviewer, decision in `workspace/verification/latest/live-pr-sign-off.json`)

**Safety rules:**
- `GITHUB_TOKEN` is **never** the approval token
- The approval value `APPROVE_LIVE_PR` is a known phrase, not a secret
- Never automate this step

---

## Step 4 — Live PR Creation (Agent Executes, Human Authorized)

```bash
# Words — 4 examples to aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples
PYTHONPATH=src python -m plugin_examples publish-pr \
    --family words \
    --publish \
    --approval-token APPROVE_LIVE_PR \
    --promote-latest

# Cells — 9 examples to aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples
PYTHONPATH=src python -m plugin_examples publish-pr \
    --family cells \
    --publish \
    --approval-token APPROVE_LIVE_PR \
    --promote-latest
```

**Token requirement:** `GITHUB_TOKEN` must be a classic PAT with `repo` scope, or a fine-grained PAT
with "Contents: Read and Write" permission for the target repo. The pipeline reads only `GITHUB_TOKEN`.
A fine-grained PAT without Contents write permission fails at blob creation (HTTP 403). The operator
must ensure the correct token type is set before running with `--publish`.

Expected outputs:
- `workspace/verification/latest/words-live-pr-simulation.json` — updated with `live_pr_created=true`, `pr_url`
- `workspace/verification/latest/cells-live-pr-simulation.json` — updated with `live_pr_created=true`, `pr_url`

---

## Step 5 — Verify and Close

After PRs are created:

1. Confirm PR URLs are accessible and correct
2. Record PR URLs in evidence
3. Close `followup-agent-operated-live-pr-creation` taskcard with PR URLs as evidence
4. Human reviews and merges PRs on GitHub

---

## Blocked Reasons (Abort if Any Fire)

| Code | Meaning | Action |
|---|---|---|
| `blocked_live_pr_approval_required` | No approval token set | Set env var or pass --approval-token |
| `blocked_invalid_live_pr_approval` | Wrong token value | Token must be exactly `APPROVE_LIVE_PR` |
| `blocked_publish_dry_run_conflict` | Both --dry-run and --publish set | Remove one flag |
| `blocked_publish_to_main` | Branch would be `main` | Check run_id format |
| `blocked_repo_access_not_ready` | repo_access_ready=False | Run resolve-repo-access and check GITHUB_TOKEN |
| `blocked_pr_permission_not_ready` | pr_permission_ready=False | Verify GITHUB_TOKEN permissions |
| `blocked_missing_validation_evidence` | Gate verdict not publishable | Rerun pipeline, check gate-results.json |

---

## Package Targets

| Family | Target Repo | Branch | Examples | NuGet Version |
|---|---|---|---|---|
| cells | `aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples` | main | 9 | 26.4.0 |
| words | `aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples` | main | 4 | 26.4.0 |

---

## Evidence Files Written

| File | Content |
|---|---|
| `workspace/verification/latest/words-live-pr-simulation.json` | Words simulation result |
| `workspace/verification/latest/cells-live-pr-simulation.json` | Cells simulation result |
| `workspace/verification/latest/publish-permission-probe.json` | Permission probe |
| `workspace/verification/latest/family-publish-readiness.json` | 4-tier readiness |
| `workspace/verification/latest/live-pr-sign-off.json` | Human sign-off record |

---

## Implementation Notes

The `publish-pr` command supports two modes:
- `--dry-run` (default): simulation only, no remote writes, validates all prerequisites
- `--publish`: live mode, creates branch + commit + PR via GitHub REST API

Live publish (`--publish`) requires:
1. Approval token (`--approval-token APPROVE_LIVE_PR` or `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` env var)
2. `GITHUB_TOKEN` — classic PAT with `repo` scope, or fine-grained PAT with Contents write permission
3. Assembled package at the expected `workspace/pr-dry-run/{family}-controlled-pilot/` path

Words PR #1 was successfully created on 2026-05-02 using this implementation.
