# Sprint 65 — Final Verdict

Sprint: sprint65-publication-truth-repair-root-readme-strict-audit-handoff
Date: 2026-05-22

## Verdict

`LOWCODE_DRY_RUN_PUBLICATION_HANDOFF_READY_42_OF_42_APPROVAL_BLOCKED`

## Summary

Sprint 65 repairs all 8 blocking defects from Sprint 64 (S64-D1 through S64-D8).

| Defect | Description | Status |
|--------|-------------|--------|
| S64-D1 | Final verdict overclaims publication without remote proof | CLOSED |
| S64-D2 | Count contradiction (dry_run_present=37 vs 40/42 in summary) | CLOSED |
| S64-D3 | content-audit-deep.json missing required fields | CLOSED |
| S64-D4 | Family root README artifacts missing | CLOSED |
| S64-D5 | Root README audit stale for PDF | CLOSED |
| S64-D6 | Special cases lack placement proof | CLOSED |
| S64-D7 | EV/ECC semantic rules too weak | CLOSED |
| S64-D8 | PDF drift not labeled in all files | CLOSED |

## Evidence Highlights

- **42/42 examples** with complete content audit (all fields present)
- **Remote proof bundled**: all 6 destination repos have merged PRs (merge SHAs captured)
- **Root READMEs**: 6 family artifacts with corrected version strings
- **Special cases**: 2 PDF scenarios with placement proof (20/20 tests PASS)
- **PDF version**: POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED (all 19 scenarios)
- **EV rules**: 32 total (was 22), Sprint 64 fails under new rules (overall_valid=false)
- **Tests**: 2993 passed, 3 skipped, 0 failed

## DRY_RUN Status

Publication is BLOCKED_BY_APPROVAL. All 42 examples are already published (Sprint 62).
No new live publication was performed in Sprint 65.

Approval gate: `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`

## Prior Sprint Corrections

| Sprint | Original Verdict | Corrected Status |
|--------|-----------------|-----------------|
| Sprint 64 | LOWCODE_DRY_RUN_42_42_CLEAN_PACKAGES_PUBLICATION_READINESS | LOWCODE_DRY_RUN_PACKAGES_STRONG_PROGRESS_PUBLICATION_PROOF_MISSING |
| Sprint 63 | EVIDENCE_GATE_REPAIR_REQUIRED_NOT_CLOSED | (Sprint 64 closure) |

## Sprint 65 State

`SPRINT65_CLOSED`
