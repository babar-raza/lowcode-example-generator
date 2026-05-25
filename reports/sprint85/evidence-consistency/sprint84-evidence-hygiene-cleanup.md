Sprint 85 — Sprint 84 Evidence Hygiene Cleanup
================================================
Date: 2026-05-24
Author: Lane H (Evidence Consistency Agent)

## Purpose
Sprint 84 was accepted with 5 evidence hygiene defects that do not affect correctness
or validity of the sprint, but violate strict evidence consistency rules.
Sprint 85 repairs these defects in-place and documents the repairs.

## Repairs Applied

### Defect 1: bundle-manifest.json source_sha = TBD_AFTER_COMMIT
- File: reports/sprint84/bundle-manifest.json
- Before: `"source_sha": "TBD_AFTER_COMMIT"`
- After: `"source_sha": "8bb4513"`
- Rationale: Sprint 84 final commit is 8bb4513. The TBD placeholder was never updated
  after the commit sequence completed. source_sha should reference the sprint's closing commit.

### Defect 2: final-consistency-check.json stale "will be captured" text
- File: reports/sprint84/review/final-consistency-check.json
- Before: `final_clean_proof_captured: false`, `dirty_after_captured_post_commit: false`,
  notes say "will be captured in commit 2"
- After: `final_clean_proof_captured: true`, `dirty_after_captured_post_commit: true`,
  notes updated to reflect actual capture state
- Rationale: Both files WERE captured (final-clean-proof.txt at commit 3, dirty-state-after.txt
  at commit 1). The consistency check was written before captures but never refreshed.

### Defect 3: taskcard-update-proof.md stale PENDING for Lane J
- File: reports/sprint84/tracking/taskcard-update-proof.md
- Before: `| J | IV | PENDING — runs after all lanes complete |`
- After: `| J | IV | COMPLETED — IV signed off, all lanes verified |`
- Rationale: Lane J (IV) completed and produced independent-verification-report.md,
  lane-output-checklist.json, and blocker-register.json. The taskcard was written by
  Lane I before Lane J finished but was never updated.

### Defect 4: scoreboard-update-proof.md TBD for EV applicable
- File: reports/sprint84/tracking/scoreboard-update-proof.md
- Before: `| EV applicable | 56 | TBD (post-EV run) | - |`
- After: `| EV applicable | 56 | 69 | +13 |`
- Rationale: EV Phase B ran and produced 69 applicable passes. The scoreboard was
  written before the EV run but never refreshed with actual values.

### Defect 5: dirty-state-after.txt SHA mismatch with final-clean-proof.txt
- File: reports/sprint84/git/dirty-state-after.txt
- Before: `Captured after: commit 1844c49`
- After: `Captured after: sprint84 final commit 8bb4513 (4 commits: 1844c49 → 71ff43f → 8fb3008 → 8bb4513)`
- Rationale: Sprint 84 had 4 commits (bundle + 3 proof commits). dirty-state-after
  referenced only commit 1. Updated to reference the final commit with full sequence
  for traceability. The actual dirty state (7 workspace/verification/latest/ files)
  was identical after all 4 commits.

## Validator Rules Added
Sprint 85 adds EV rules 120-124 to catch these defect classes automatically:
- Rule 120: bundle_manifest_source_sha_not_tbd
- Rule 121: no_stale_will_capture_text_in_final_consistency
- Rule 122: no_stale_pending_lane_label_in_tracking
- Rule 123: scoreboard_ev_applicable_not_tbd
- Rule 124: bundle_manifest_source_sha_in_final_clean_proof

## Impact
No Sprint 84 validity impact. All repairs are documentation-accuracy improvements.
Sprint 84 EV and ECC results remain valid. Sprint 85 commits these edits as part
of the sprint85 bundle.
