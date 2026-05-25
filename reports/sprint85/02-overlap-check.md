Sprint 85 — Overlap Check
==========================
Date: 2026-05-24
Author: Coordinator Agent

## Purpose
Verify no two lanes write to the same path. Serial writes to shared authority files are
coordinated by the Coordinator. Confirm no lane violates another lane's owned paths.

## Lane Path Matrix

| Path Prefix | Owner Lane | Other Lanes Allowed |
|-------------|-----------|---------------------|
| reports/sprint85/publication/live-approval-check.md | A | none |
| reports/sprint85/publication/pr-creation-ledger.json | A | none |
| reports/sprint85/publication/pr-diff-verification.json | A | none |
| reports/sprint85/publication/per-family/ | A | none |
| reports/sprint85/publication/pr-batching-strategy.md | B | none |
| reports/sprint85/publication/pr-batching-plan.json | B | none |
| reports/sprint85/publication/pr-batching-risk-matrix.md | B | none |
| reports/sprint85/publication/publication-file-plan.json | B | none |
| reports/sprint85/publication/per-family-file-plan.md | B | none |
| reports/sprint85/conflicts/ | C | none |
| reports/sprint85/handoff/ | D | none |
| reports/sprint85/remote/ | D | none |
| reports/sprint85/merge-readiness/ | E | none |
| reports/sprint85/publication/merge-plan.md | E | none |
| reports/sprint85/publication/post-merge-verification-plan.md | E | none |
| reports/sprint85/publication/branch-delete-plan.md | E | none |
| reports/sprint85/publication/merge-result.json | E | none |
| reports/sprint85/publication/post-merge-verification.json | E | none |
| reports/sprint85/publication/branch-delete-result.json | E | none |
| reports/sprint85/product/ | F | none |
| reports/sprint85/version-drift/ | F | none |
| reports/sprint85/formimporter/ | F | none |
| reports/sprint85/post-merge-runtime/ | F | none |
| reports/sprint85/readiness/ | F | none |
| reports/sprint85/evidence/validator-*.* | G | none |
| reports/sprint85/evidence/pipeline-integration-proof.md | G | none |
| src/plugin_examples/evidence_validator.py | G | none |
| tests/unit/test_evidence_validator.py | G | none |
| reports/sprint85/evidence-consistency/ | H | none |
| reports/sprint85/git/ | H | Coordinator (final-clean-proof) |
| reports/sprint85/logs/ | H | none |
| reports/sprint84/bundle-manifest.json | H | none (hygiene repair) |
| reports/sprint84/review/final-consistency-check.json | H | none (hygiene repair) |
| reports/sprint84/tracking/taskcard-update-proof.md | H | none (hygiene repair) |
| reports/sprint84/tracking/scoreboard-update-proof.md | H | none (hygiene repair) |
| reports/sprint85/tracking/ | I | none |
| reports/sprint85/iv/ | J | none |
| reports/sprint85/review/iv-findings.md | J | none |
| reports/sprint85/final-verdict.md | Coord | none |
| reports/sprint85/sprint-state.json | Coord | none |
| reports/sprint85/bundle-manifest.json | Coord | none |
| reports/sprint85/evidence/sprint85-final-validation-result.json | Coord | none |
| reports/sprint85/evidence/evidence-contract-computed.json | Coord | none |
| reports/sprint85/publication/publication-truth-matrix-final.json | Coord | none |
| reports/sprint85/publication/publication-summary.md | Coord | none |
| reports/sprint85/review/adversarial-review.md | Coord | none |
| reports/sprint85/review/self-repair-actions.json | Coord | none |
| reports/sprint85/review/final-consistency-check.json | Coord | none |

## Conflict Analysis

Potential conflicts:
1. git/dirty-state-after.txt and git/final-clean-proof.txt: Owned by H, but Coordinator
   writes final-clean-proof.txt after bundle commit. RESOLUTION: H captures draft;
   Coordinator commits and writes final proof with real SHA.
2. publication-summary.md: Coordinator-owned, not Lane B. No conflict.
3. Sprint 84 hygiene files: H writes 4 Sprint 84 files. No Sprint 85 lane writes Sprint 84
   files. No conflict.

CONFLICT_COUNT: 0 unresolved

## Path Uniqueness Verdict
PASS — all paths are uniquely owned or explicitly coordinated.
