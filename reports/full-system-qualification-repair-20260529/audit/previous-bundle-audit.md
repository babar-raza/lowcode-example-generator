# Previous Bundle Audit

**Sprint ID:** full-system-qualification-repair-20260529
**Audited Bundle:** system-qualification-evidence-20260528.zip
**Previous Sprint ID:** sysqual-20260528-001
**Audit Date:** 2026-05-29T00:00:00Z

## Reclassification

Previous verdict was: `LOWCODE_SYSTEM_QUALIFICATION_ACCEPTED_WITH_EXTERNAL_BLOCKERS`

**Reclassified as:** `PARTIAL_MACHINERY_QUALIFICATION_ACCEPTED_FULL_SYSTEM_QUALIFICATION_NOT_ACCEPTED`

### Reasons

- **C-001 (SKIP_RUN_ENABLED):** All 6 LowCode E2E runs used --skip-run + --template-mode. Validation, reviewer, and publisher stages were explicitly skipped.
- **C-002 (BUILD_NOT_RUN):** Build logs say build NOT RUN for all 6 LowCode products in the prior sprint.
- **C-003 (VALIDATION_SKIPPED):** Validation stage (stage 15) was skipped in template-mode for all 6 products.
- **C-004 (REVIEWER_SKIPPED):** Reviewer stage was skipped in template-mode. No governed fallback was documented.
- **C-005 (PUBLISHER_SKIPPED):** Publisher/local package dry-run was not executed in the prior sprint.
- **C-006 (UNBUNDLED_PRODUCTION_EVIDENCE):** Prior sprint final verdict relied on workspace/verification/latest paths for production evidence, but those paths were not bundled in the evidence ZIP.
- **C-007 (VALIDATOR_TESTS_NOT_RUN):** pytest was not run in the prior sprint. Test suite status unknown.
- **C-008 (HTML_SVG_CONTRADICTION_PARTIAL):** HTML and SVG were classified NO_LOWCODE_CONFIRMED but had dependency blockers (missing transitive deps). Resolution was documented in workspace but not in the sprint evidence.
- **C-009 (PRODUCT_QUEUE_NOT_TRACKED):** Prior sprint did not maintain a formal product queue with PENDING/RUNNING/PASSED/BLOCKED states.

## Known Good Items (carried forward)

- **HEAL-001 PDF include_all_tfm_groups:** runner.py DependencyResolution now passes include_all_tfm_groups=True for PDF family. Fix verified by clean re-run in prior sprint.
- **HEAL-002 Words denominator canonical hash:** words.json denominator api_catalog_sha256 reverted to canonical value after stale-cache false positive.
- **25-product universe classification:** 25 products classified across all categories. Universe reconciliation against expected 26 documented with evidence.
- **External blocker evidence for epub/ocr/psd:** Three products blocked by external NuGet unavailability.
