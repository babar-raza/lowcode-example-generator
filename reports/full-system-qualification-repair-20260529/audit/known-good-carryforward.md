# Known Good Carryforward

**Sprint ID:** full-system-qualification-repair-20260529
**Date:** 2026-05-29T00:00:00Z

## HEAL-001 PDF include_all_tfm_groups

**Description:** runner.py DependencyResolution now passes include_all_tfm_groups=True for PDF family. Fix verified by clean re-run in prior sprint.

**Test Status:** VERIFIED_BY_CLEAN_RERUN_IN_PRIOR_SPRINT

**Action in this sprint:** Used as-is; re-verified by running full validation stage for PDF.

**Files:** src/plugin_examples/family_config/models.py, src/plugin_examples/family_config/loader.py, src/plugin_examples/runner.py, pipeline/configs/families/pdf.yml, pipeline/schemas/family-config.schema.json

## HEAL-002 Words denominator canonical hash

**Description:** words.json denominator api_catalog_sha256 reverted to canonical value after stale-cache false positive.

**Test Status:** VERIFIED_BY_CLEAN_RERUN_IN_PRIOR_SPRINT

**Action in this sprint:** Used as-is; re-verified by running scenario_planning stage for Words.

**Files:** pipeline/configs/denominators/words.json

## 25-product universe classification

**Description:** 25 products classified across all categories. Universe reconciliation against expected 26 documented with evidence.

**Test Status:** ACCEPTED_IN_PRIOR_SPRINT

**Action in this sprint:** Fresh discovery re-run for all 25 products to update classification.

## External blocker evidence for epub/ocr/psd

**Description:** Three products blocked by external NuGet unavailability.

**Test Status:** ACCEPTED_IN_PRIOR_SPRINT

**Action in this sprint:** Rechecked fresh in Lane 7.

