# Sprint 91 — Final Approval Packet

**Author:** Publication Agent (Lane 4)
**Date:** 2026-05-27

## For Operator: What You Need to Know

This packet summarizes what is ready and what is waiting for your approval.

## Local State: READY

- Evidence: `reports/sprint91/evidence/sprint91-final-validation-result.json`
  - `canonical_overall_valid: true`
  - `applicable_rules_failed: 0`
- ECC: `reports/sprint91/evidence/evidence-contract-computed.json`
  - `closure_valid: true`
  - `blocking_failures: 0`
- Git state: Clean after Sprint 91 commit
- Test baseline: 3189 (Sprint 89 committed); pytest ENV_BLOCKER in Sprint 91 session

## What Happens on Approval

If you set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`:

1. Publication agent will create 6 README I/O PRs (Cells, PDF, Slides, Email, Diagram, Words)
2. Each PR will contain the family's README.md updates
3. Each PR will be verified for correct diff

If you additionally set `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR`:

4. Agent will merge the PRs after verification
5. Agent will fetch remote main and verify remote README I/O
6. Agent will delete safe branches after verified merge

## To Approve

```bash
export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
export PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR  # optional: for merge
# Then rerun the sprint
```

## Current Verdict Without Approval

`LOWCODE_FINAL_LOCAL_CLOSEOUT_ACCEPTED_PUBLICATION_APPROVAL_BLOCKED`

This is the preferred verdict when local authority is clean and publication approval is absent.
