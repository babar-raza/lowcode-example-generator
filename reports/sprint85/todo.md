Sprint 85 — Todo
=================
Date: 2026-05-24

## Coordinator Phase 0
- [x] Read Sprint 84 acceptance baseline
- [x] Confirm approval gates (LIVE=NOT_SET, MERGE=NOT_SET)
- [x] Create 00-sprint84-acceptance-baseline.md
- [x] Create 01-sprint85-coordinator-plan.md
- [x] Create 02-overlap-check.md
- [x] Capture git dirty-state-before.txt
- [x] Create evidence-contract.json (68 categories)

## Lane H — Evidence Consistency (Sprint 84 repair)
- [x] Fix bundle-manifest.json source_sha TBD → 8bb4513
- [x] Fix final-consistency-check.json stale "will be captured" text
- [x] Fix taskcard-update-proof.md stale PENDING for Lane J
- [x] Fix scoreboard-update-proof.md TBD EV applicable → 69
- [x] Create sprint84-evidence-hygiene-cleanup.md (audit trail)
- [x] Capture git dirty-state-before.txt for sprint85

## Lane G — Validator Hardening
- [x] Add EV rules 120-124 to evidence_validator.py
- [x] Add 8 tests to test_evidence_validator.py
- [x] Update test count assertions (171 → 179)
- [x] Run validator tests (179 pass)
- [x] Run full suite (3120 pass)
- [x] Create validator-gap-analysis.md
- [x] Create validator-source-proof.patch
- [x] Create validator-test-results.txt
- [x] Create pipeline-integration-proof.md

## Lane B — PR Batching
- [x] Create pr-batching-strategy.md
- [x] Create pr-batching-plan.json (6 PRs, sprint85 branches, approval-blocked)
- [x] Create pr-batching-risk-matrix.md
- [x] Create publication-file-plan.json
- [x] Create per-family-file-plan.md

## Lane C — Root README
- [x] Create root-readme-pr-inventory.json (cells#5, words#7, diagram#2)
- [x] Create root-readme-pr-conflict-strategy.md
- [x] Create root-readme-action-plan.json
- [x] Create root-readme-file-plan.json

## Lane D — Handoff and Remote
- [x] Create handoff-source-authority.md
- [x] Create handoff-prepublish-validation.json
- [x] Create handoff-source-map.json
- [x] Create handoff-diff-summary.md
- [x] Create remote-repo-state-before.json
- [x] Create remote-readme-io-audit-before.json
- [x] Create remote-vs-handoff-before.json
- [x] Create remote-conflict-check.md

## Lane E — Merge Readiness
- [x] Create merge-readiness-summary.md
- [x] Create merge-plan.md
- [x] Create post-merge-verification-plan.md
- [x] Create branch-delete-plan.md
- [x] Create merge-result.json (SKIPPED_NO_PRS)
- [x] Create post-merge-verification.json (SKIPPED_NO_PRS)
- [x] Create branch-delete-result.json (SKIPPED_NO_PRS)

## Lane F — Product
- [x] Create product-advancement-summary.md
- [x] Create words-version-status.md
- [x] Create words-version-drift-current.json
- [x] Create formimporter-status.md
- [x] Create formimporter-repro-inventory.json
- [x] Create email-slides-runtime-carry-forward.md
- [x] Create live-publication-operator-checklist.md
- [x] Create next-family-readiness.md

## Lane A — Publication Gate
- [x] Create live-approval-check.md (APPROVAL_BLOCKED)
- [x] Create pr-creation-ledger.json (prs_created=0)
- [x] Create pr-diff-verification.json (approval-blocked)

## Lane I — State Sync
- [x] Create taskcard-update-proof.md
- [x] Create scoreboard-update-proof.md
- [x] Create next-gate-register.json

## Sprint 75 Carry-Forward Files
- [x] Create pdf-publication/pdf-pr-reconciliation.json
- [x] Create governance/sprint27-strict-contract-revalidation.md

## ECC + EV
- [x] Seed evidence-contract-computed.json (placeholder)
- [x] [All 68 ECC categories created]
- [x] Run ECC → 68/68 PRESENT, closure_valid=true
- [x] Update evidence-contract-computed.json
- [x] Create sprint85-bundle-validation-result.json
- [x] Run EV Phase A → applicable pass
- [x] Run EV Phase B → applicable pass
- [x] Update sprint85-final-validation-result.json

## Final Integration
- [x] Create publication-truth-matrix-final.json
- [x] Create publication-summary.md
- [x] Run adversarial review
- [x] Create adversarial-review.md
- [x] Create self-repair-actions.json
- [x] Create final-consistency-check.json
- [x] Create sprint-state.json
- [x] Create final-verdict.md
- [x] Create bundle-manifest.json

## Lane J — IV
- [x] Create independent-verification-report.md
- [x] Create lane-output-checklist.json
- [x] Create blocker-register.json
- [x] Create iv-findings.md

## Final Commit + ZIP
- [x] git add (exact paths) + git commit (bundle commit)
- [x] Update dirty-state-after.txt
- [x] Create final-clean-proof.txt
- [x] git commit (clean-proof commit)
- [x] Create ZIP bundle
