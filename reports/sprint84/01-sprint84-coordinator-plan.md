Sprint 84 — Coordinator Plan
==============================
Date: 2026-05-24
Sprint Type: MULTI_MEGA_TRAIN
HEAD at start: 824173e

## Mission
Resolve Sprint 83 caveats (C1–C4), produce governed PR batching strategy (1 PR/family default),
formally decide per-family root README strategy, normalize stale labels, harden EV for PR
lifecycle governance. Publication remains approval-gated.

## Approval Gate Status
- PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL: NOT_SET → PRs BLOCKED
- PLUGIN_EXAMPLES_MERGE_PR_APPROVAL: NOT_SET → Merges BLOCKED
- Safe lanes run regardless.

## Evidence Contract
- Categories: 59 (EC01-EC59)
- Sprint 83 had 50. Sprint 84 adds 9 new: EC10 (root-readme-file-plan), EC22 (next-family-readiness),
  EC33-EC35 (PR batching), EC38 (merge-readiness-summary), EC39-EC41 (merge/post-merge plans).

## Lane Assignments

### Lane A — Publication Gate Check (SKIP/RECORD)
Approval gate = NOT_SET → record block, no PRs created.
Deliverables: live-approval-check.md, pr-creation-ledger.json, pr-diff-verification.json,
              publication-file-plan.json, publication-summary.md

### Lane B — PR Batching Strategy (DECISION)
Formally decide and document: 1 PR per family (6 total) as default.
Exceptions: only if root README conflict or large diff requires split.
Deliverables: pr-batching-strategy.md, pr-batching-plan.json, pr-batching-risk-matrix.md

### Lane C — Root README Conflict (DECISION + PLAN)
Per-family root README strategy with explicit rationale.
Open PRs: cells#5, words#7, diagram#2.
Deliverables: root-readme-pr-inventory.json, root-readme-pr-conflict-strategy.md,
              root-readme-action-plan.json, root-readme-file-plan.json

### Lane D — Handoff/Remote Truth (CARRY-FORWARD)
Verify 42 remote examples still accessible, refresh remote vs handoff delta.
Deliverables: remote-repo-state-before.json, remote-readme-io-audit-before.json,
              remote-vs-handoff-before.json, handoff-source-authority.md,
              handoff-prepublish-validation.json, handoff-source-map.json, handoff-diff-summary.md

### Lane E — Merge/Post-Merge Readiness (PLAN)
No PRs exist yet → merge-result/post-merge-verification/branch-delete-result record SKIPPED.
Plan documents what merge sequence will look like when approved.
Deliverables: merge-readiness-summary.md, merge-plan.md, post-merge-verification-plan.md,
              branch-delete-plan.md, merge-result.json (SKIPPED), post-merge-verification.json (SKIPPED),
              branch-delete-result.json (SKIPPED)

### Lane F — Product/System (CARRY-FORWARD + STATUS)
Words drift: carry forward (approval-blocked).
FormImporter: BLOCKED_EXTERNAL carry-forward.
Email/Slides runtime: REPAIRED carry-forward.
Next-family-readiness: identify which family would be Sprint 85 target.
Deliverables: product-advancement-summary.md, words-version-status.md, formimporter-status.md,
              email-slides-runtime-carry-forward.md, live-publication-operator-checklist.md,
              next-family-readiness.md

### Lane G — Validator Hardening (NEW RULES)
Add 4 new EV rules 116-119:
- 116: pr_batching_strategy_present_if_pr_creation_attempted
- 117: pr_batching_plan_present_if_pr_creation_attempted
- 118: root_readme_file_plan_present_before_pr_creation
- 119: no_bulk_42pr_plan_without_justification
Update test suite, run, capture results.
Deliverables: validator-gap-analysis.md, validator-source-proof.patch, validator-test-results.txt

### Lane H — Evidence Consistency/Git Proof (CLEANUP)
Normalize Sprint 83 stale labels, classify dirty files.
Run pytest to confirm clean baseline.
Deliverables: sprint83-stale-label-cleanup.md, dirty-file-classification.md,
              dirty-state-after.txt, logs/test-run.log

### Lane I — Taskcard Sync (NORMALIZE)
Update all taskcard entries to remove stale "pending validator tests" labels.
Deliverables: taskcard-update-proof.md, scoreboard-update-proof.md, next-gate-register.json

### Lane J — Independent Verification (IV)
Verify all 9 lane outputs, check ECC completeness, confirm no rule regressions.
Deliverables: independent-verification-report.md, lane-output-checklist.json,
              blocker-register.json, iv-findings.md

## EV Rule Count Target
- Sprint 83: 115 rules
- Sprint 84: 119 rules (4 new from Lane G)

## Test Count Target
- Sprint 83: 163 tests
- Sprint 84: 167 tests (4 new from Lane G)

## Expected Verdict
LOWCODE_LIVE_PUBLICATION_BLOCKED_BY_APPROVAL
(Same as Sprint 83 — gate not lifted)

## Stop Conditions
- If EV applicable rules drop below 56: HALT, diagnose
- If test count below 167 after Lane G: HALT, diagnose
- If ECC closure_valid=false: HALT, re-run two-pass protocol
- If final-consistency-check.json shows PASS_PENDING_COMMIT: FAIL (rule 114 violation)
