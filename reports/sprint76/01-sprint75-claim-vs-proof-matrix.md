# Sprint 75 Claim vs Proof — Sprint 76 Classification Matrix

**Date:** 2026-05-24
**Purpose:** Classify every Sprint 75 claim using Sprint 76 independent review.

Labels:
- VERIFIED — claim is fully supported by evidence
- PARTIALLY_VERIFIED — claim is supported for some items but not all
- CONTRADICTED — claim is directly contradicted by evidence
- INVALID_CLOSURE — claim enabled closure but was not valid
- REPAIRED_IN_SPRINT76 — defect found and repaired during sprint76
- CARRIED_FORWARD_WITH_TASKCARD — acknowledged defect, tracked for future

---

## Sprint 75 Claims

| # | Claim | Classification | Notes |
|---|-------|---------------|-------|
| 1 | PDF publication truth reconciliation — all 19 examples remotely present, "14 blocked" claim historical | VERIFIED | pdf-scenario-publication-map.json, pr-reconciliation.json confirmed. Remote presence cross-checked against sprint74 handoff. |
| 2 | FormImporter upstream bug tracking — BLOCKED_EXTERNAL at Aspose.PDF 26.5.0 | VERIFIED | formimporter-repro-inventory.json present, TRG-01 registered, retest-trigger-register.json present. |
| 3 | Words version drift classification — Remote=26.4.0, handoff=26.5.0, NEEDS_REPAIR approval-blocked | VERIFIED | words-version-drift-current.json has both `drift` and `drift_type` fields. Repair correctly approval-blocked. |
| 4 | Email Converter runtime validation — Build PASS, run PASS, output confirmed | VERIFIED | email-runtime-validation.txt: exit 0, input.html created. output_confirmed=true in matrix. |
| 5 | Slides Convert runtime validation — Build PASS, run PASS, 64837 bytes PDF | VERIFIED | slides-runtime-validation.txt: confirmed 64837 bytes output. output_confirmed=true in matrix. |
| 6 | Slides Merger runtime validation — Build PASS, run PASS, 42020 bytes PPTX | VERIFIED | slides-runtime-validation.txt: confirmed 42020 bytes output. output_confirmed=true in matrix. |
| 7 | Slides Compress runtime validation — post_merge_validated=true | INVALID_CLOSURE → REPAIRED_IN_SPRINT76 | `output_confirmed: false`, `runtime_result: RUNTIME_VALIDATED_NO_INPUT_FIXTURE`. No compression performed. Repaired in Sprint 76 Phase 2. |
| 8 | Weekly Review Item 4 fully "REPAIRED" (including Slides Compress) | CONTRADICTED → REPAIRED_IN_SPRINT76 | Overclaimed. Slides Compress was RUNTIME_PARTIAL_NO_INPUT_FIXTURE. Item 4 should have been PARTIALLY_REPAIRED. Sprint 76 completes the repair. |
| 9 | Dirty tree classified — no source/test files dirty at close | CONTRADICTED | dirty-state-after.txt shows evidence_validator.py and test files modified. dirty-file-classification.md says no source/test dirty. These are internally inconsistent. (Source/test were in fact committed in b2a2748 — final-clean-proof.txt is accurate — but the classification document contradicts the captured dirty state.) |
| 10 | Sprint 27 historical governance exception | VERIFIED | governance/historical-evidence-exception-policy.md, sprint27-strict-contract-revalidation.md present. 17 missing categories grandfathered as PRE_CONTRACT_ERA_BUNDLE. |
| 11 | EV 93/93 PASS | PARTIALLY_VERIFIED | Rules pass but rules 90/91 do not catch Slides Compress partial validation or dirty-state internal contradiction. New rules required. |
| 12 | ECC 46/46 PRESENT | VERIFIED | evidence-contract-computed.json: 46/46 PRESENT, closure_valid=true. |
| 13 | Tests 3041/3041 PASS | VERIFIED | logs/test-run.log: 3041 passed, 3 skipped. |
| 14 | Publication approval blocked | VERIFIED | live-approval-check.md confirms PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL not set. PRs=0. |

---

## Summary

- VERIFIED: 10 items
- PARTIALLY_VERIFIED: 1 item (EV rule completeness)
- CONTRADICTED / REPAIRED_IN_SPRINT76: 2 items (Slides Compress, dirty-state)
- INVALID_CLOSURE → REPAIRED_IN_SPRINT76: 1 item (Slides Compress claim)
- VERIFIED: Sprint 27 governance, FormImporter, Words drift, PDF truth, Email, Slides Convert/Merger

Sprint 76 must repair items 7, 8, 9 and harden EV to prevent recurrence.
