# Sprint 78 Claim vs. Proof Matrix

**Date:** 2026-05-24
**Sprint:** 79 (Sprint 78 evidence authority repair)

| # | Claim | Proof File | Proof Status | Classification |
|---|-------|------------|-------------|----------------|
| 1 | canonical_overall_valid=true, 53 applicable rules pass | sprint78-final-validation-result.json | Partially verified — file exists, counts correct, but missing Phase 1 fields | REPAIRED_IN_SPRINT79 |
| 2 | Sprint 78 Phase A run has 55 non-applicable failures | sprint78-bundle-validation-result.json | File exists but lacks diagnostic_rules_are_non_blocking=true label | REPAIRED_IN_SPRINT79 |
| 3 | ECC closure_valid=true, 32/32 present | evidence-contract-computed.json | CONTRADICTION: closure_valid=true with blocking_failures=1 | REPAIRED_IN_SPRINT79 |
| 4 | EC27 self-reference is present | evidence-contract-computed.json EC27 | Bootstrap note says "File not found" — phantom PRESENT | REPAIRED_IN_SPRINT79 |
| 5 | 134 EV tests pass including Sprint 78 new rules | validator-test-results.txt | STALE: file is labeled Sprint 77, reports 123 tests | REPAIRED_IN_SPRINT79 |
| 6 | EvidenceValidator wired in pipeline | pipeline-integration-proof.md | INSUFFICIENT: one-line assertion only | REPAIRED_IN_SPRINT79 |
| 7 | Full evidence bundle provided | (none) | MISSING: no ZIP bundle | REPAIRED_IN_SPRINT79 |
| 8 | 42/42 examples published, all_merged=true | publication-truth-matrix-final.json | VERIFIED: consistent with release-status output | VERIFIED |
| 9 | README I/O approval-blocked | final-verdict.md, bundle-manifest.json | VERIFIED: PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=NOT_SET | VERIFIED |
| 10 | 6/6 remote repos accessible | remote-repo-state-before.json | VERIFIED: all 6 repos show can_push=true | VERIFIED |
| 11 | Handoff valid, 42/42 examples | handoff-prepublish-validation.json | VERIFIED: overall_handoff_valid=true | VERIFIED |
| 12 | Words version drift documented | version-drift/words-version-drift-current.json | VERIFIED: drift=REMOTE_DRIFT, status=NEEDS_REPAIR_APPROVAL_BLOCKED | CARRIED_FORWARD_WITH_TASKCARD |
| 13 | FormImporter STILL_BLOCKED | formimporter/formimporter-repro-inventory.json | VERIFIED: retest trigger = Aspose.PDF NuGet > 26.5.0 | CARRIED_FORWARD_WITH_TASKCARD |
| 14 | Sprint 27 governance classified | governance/sprint27-strict-contract-revalidation.md | VERIFIED: PRE_CONTRACT_ERA_BUNDLE classification present | CARRIED_FORWARD_WITH_TASKCARD |
| 15 | 3075 tests pass | logs/test-run.log | VERIFIED: 3075 passed, 3 skipped in Sprint 78 run | VERIFIED |
