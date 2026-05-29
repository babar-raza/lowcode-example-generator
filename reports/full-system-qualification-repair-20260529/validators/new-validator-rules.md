# New Validator Rules

**Sprint ID:** full-system-qualification-repair-20260529
**Added:** 2026-05-29T00:00:00Z

These rules prevent the classes of overclaiming found in prior sprints.

## R-NEW-001: skip_run_not_allowed_for_full_qualification

**Description:** Rejects final verdicts that claim full qualification when skip_run=True was used in any E2E run

**Severity:** FATAL

**Prevents:** C-001 SKIP_RUN_ENABLED overclaim

## R-NEW-002: build_not_run_not_allowed_for_full_qualification

**Description:** Rejects final verdicts that claim full qualification when any build.log contains BUILD_NOT_RUN

**Severity:** FATAL

**Prevents:** C-002 BUILD_NOT_RUN overclaim

## R-NEW-003: validation_skipped_not_allowed_for_full_qualification

**Description:** Rejects full qualification claims when validation stage was skipped in any family run

**Severity:** FATAL

**Prevents:** C-003 VALIDATION_SKIPPED overclaim

## R-NEW-004: reviewer_skipped_requires_governed_fallback

**Description:** Reviewer unavailability must have explicit governed fallback proof; reviewer=skipped without fallback is FATAL

**Severity:** FATAL

**Prevents:** C-004 REVIEWER_SKIPPED_NO_FALLBACK overclaim

## R-NEW-005: publisher_skipped_not_allowed_for_full_qualification

**Description:** Publisher dry-run must be executed; publisher=skipped is FATAL for full qualification

**Severity:** FATAL

**Prevents:** C-005 PUBLISHER_SKIPPED overclaim

## R-NEW-006: unbundled_production_evidence_not_allowed

**Description:** Final verdict may not reference external workspace paths as evidence if those paths are not in the evidence ZIP

**Severity:** FATAL

**Prevents:** C-006 UNBUNDLED_PRODUCTION_EVIDENCE overclaim

## R-NEW-007: pending_queue_items_not_allowed_for_full_qualification

**Description:** No product may remain in PENDING state when final verdict is issued

**Severity:** FATAL

**Prevents:** C-009 PRODUCT_QUEUE_NOT_TRACKED overclaim

