Sprint 85 — Coordinator Plan
=============================
Date: 2026-05-24
Author: Coordinator Agent

## Sprint Goal

Primary: Create 6 live README I/O PRs (1 per family) if live approval is present.
Secondary: Repair Sprint 84 evidence hygiene, strengthen validators, keep state synchronized.

## Approval Gate Status
- PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL: NOT_SET
- PLUGIN_EXAMPLES_MERGE_PR_APPROVAL: NOT_SET

Consequence: Lane A is APPROVAL_BLOCKED. All non-mutating lanes execute fully.

## Sprint Verdict (Anticipated)
LOWCODE_LIVE_PUBLICATION_BLOCKED_BY_APPROVAL

## Lane Ownership

| Lane | Owner | Topic | Approval Required |
|------|-------|-------|-------------------|
| A | Publication Agent | Live PR creation | YES — APPROVE_LIVE_PR |
| B | PR Strategy Agent | PR batching + file plan | NO |
| C | Conflict Strategy Agent | Root README PR state | NO |
| D | Handoff/Remote Agent | Handoff + remote truth | NO |
| E | Merge Readiness Agent | Merge/post-merge/delete plans | NO (plans only) |
| F | Product Agent | Words drift, FormImporter, next-family | NO |
| G | Validator Agent | EV rules 120-124, tests | NO |
| H | Evidence Agent | Sprint 84 hygiene repair, git proof | NO |
| I | State Sync Agent | Taskcard/scoreboard sync | NO |
| J | IV Agent | Independent verification | NO |
| Coord | Coordinator | Shared authority files | N/A |

## Shared Authority Files (Coordinator Only)
- reports/sprint85/final-verdict.md
- reports/sprint85/sprint-state.json
- reports/sprint85/publication/publication-truth-matrix-final.json
- reports/sprint85/publication/publication-summary.md
- reports/sprint85/evidence/evidence-contract-computed.json
- reports/sprint85/evidence/sprint85-final-validation-result.json
- reports/sprint85/review/final-consistency-check.json
- reports/sprint85/bundle-manifest.json

## New EV Rules This Sprint
Rule 120: bundle_manifest_source_sha_not_tbd
Rule 121: no_stale_will_capture_text_in_final_consistency
Rule 122: no_stale_pending_lane_label_in_tracking
Rule 123: scoreboard_ev_applicable_not_tbd
Rule 124: bundle_manifest_source_sha_in_final_clean_proof

Total EV rules after Sprint 85: 124

## New ECC Categories This Sprint
Sprint 85 adds 9 new categories (EC60-EC68) beyond Sprint 84's 59:
EC60: evidence-consistency/sprint84-evidence-hygiene-cleanup.md
EC61: remote/remote-conflict-check.md
EC62: evidence/pipeline-integration-proof.md
EC63: publication/per-family-file-plan.md
EC64: logs/test-run.log
EC65: version-drift/words-version-drift-current.json
EC66: formimporter/formimporter-repro-inventory.json
EC67: pdf-publication/pdf-pr-reconciliation.json
EC68: governance/sprint27-strict-contract-revalidation.md

Total ECC categories: 68

## Global Forbidden Actions
- no broad git add .
- no git reset --hard
- no git clean
- no direct push to main
- no PR creation without PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
- no merge without PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
- no branch deletion before post-merge verification
- no secret printing

## Execution Sequence
1. Phase 0: Coordinator preflight (this file) — COMPLETE
2. Lane H: Sprint 84 hygiene repair (precedes EV run)
3. Lane G: Validator hardening (precedes EV run)
4. Lanes B/C/D/E/F: Non-mutating evidence lanes (parallel)
5. Lane A: Approval gate check (approval-blocked proof)
6. Lane I: Taskcard/state sync
7. ECC two-pass protocol
8. EV Phase A (validate_for_storage)
9. EV Phase B (validate)
10. Lane J: Independent verification
11. Final integration: adversarial review, final files, commit, zip
