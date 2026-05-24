# Weekly Review Taskcard Updates — Sprint 76

**Date:** 2026-05-24

## Taskcard Updates from Sprint 76 Repairs

### Item 4 — Slides Compress (UPGRADED)

Previous status: RUNTIME_VALIDATED_NO_INPUT_FIXTURE
Updated status: **RUNTIME_VALIDATED**
Evidence: post-merge-runtime/slides-compress-output-proof.json (output_confirmed=true)
Trigger removed: No longer needs "fixture deferred" note

All 4 runtime validation items are now RUNTIME_VALIDATED:
- email-converter ✓
- slides-compress ✓ (upgraded)
- slides-convert ✓
- slides-merger ✓

### Item 5 — Dirty Tree (CLARIFIED)

Previous label: VERIFIED_HISTORICAL_BUT_SUPERSEDED
Updated label: WORKSPACE_LATEST_DIRTY_GOVERNANCE_EXCEPTION
Reason: sprint75 claimed source/test were not dirty (incorrect); sprint76 documents
that source/test are clean (committed), but workspace/verification/latest/ remain
dirty under established governance exception.

### Item 6 — Sprint 27 (LABEL UPGRADE)

Previous label: GOVERNANCE_EXCEPTION_REQUIRED
Updated label: GOVERNANCE_EXCEPTION_APPLIED
Reason: The policy was applied in sprint75. The exception is active, not pending.

---

## No Change Items

| Item | Status | Reason |
|------|--------|--------|
| 1. PDF publication | VERIFIED_HISTORICAL_BUT_SUPERSEDED | Evidence confirmed |
| 2. FormImporter | BLOCKED_EXTERNAL | Bug still present at 26.5.0 |
| 3. Words drift | NEEDS_REPAIR_APPROVAL_BLOCKED | No new approval or PR |

---

## Active Triggers (carried forward)

| Trigger | Condition | Owner |
|---------|-----------|-------|
| TRG-01 | Aspose.PDF NuGet > 26.5.0 → retest FormImporter | sprint76 |
| TRG-02 | PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL set → create PRs | sprint76+ |
| TRG-03 | PLUGIN_EXAMPLES_MERGE_PR_APPROVAL set → merge PRs | sprint76+ |
| TRG-04 | Remote Words version advances → re-check drift | sprint76+ |
