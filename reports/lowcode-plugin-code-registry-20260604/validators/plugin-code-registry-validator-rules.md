# Plugin-Code Registry Validator Rules

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Purpose

These validators prevent the system from drifting back to:
- KNOWN_PATTERN-only synthetic catalog
- Reflection-first mapping
- Family-level probe counted as plugin coverage

---

## Rule Set

### Rule 1: REGISTRY_STATUS_REQUIRES_PRODUCT_PAGE
**Condition**: Plugin entry claims any status above PAGE_DISCOVERED
**Check**: `plugin_url` must point to a real `products.aspose.net` URL
**Fail if**: `plugin_url` is null, empty, or not products.aspose.net domain
**Code**: `REGISTRY_STATUS_NO_PRODUCT_PAGE`

### Rule 2: CODE_HARVESTED_REQUIRES_CODE_HASH
**Condition**: `registry_status == CODE_HARVESTED`
**Check**: `code_hashes` list must not be empty
**Fail if**: `code_hashes` is empty or null
**Code**: `CODE_HARVESTED_NO_CODE_HASH`

### Rule 3: SOURCE_URL_MUST_BE_FETCHED_OR_BLOCKED
**Condition**: Any `github_links` or `source_links` entries exist
**Check**: Either `code_hashes` is non-empty OR `registry_status == CODE_FETCH_FAILED`
**Fail if**: Source link exists but no code hash and no CODE_FETCH_FAILED status
**Code**: `SOURCE_LINK_UNFETCHED`

### Rule 4: GIST_MUST_BE_STORED_OR_BLOCKED
**Condition**: `gist_links` entries exist
**Check**: Either code text cached in .local/code-cache/ OR `registry_status == GIST_FETCH_BLOCKED`
**Fail if**: Gist link present but not fetched and not blocked
**Code**: `GIST_UNFETCHED`

### Rule 5: NO_HEURISTIC_ONLY_WHEN_OFFICIAL_CODE_EXISTS
**Condition**: Official GitHub repo exists for family (18/18 do)
**Check**: If `registry_status == NEEDS_MANUAL_MAPPING`, it must NOT be because reflection was the only source
**Fail if**: Entry's only evidence is reflection data (no code hash, no GitHub URL)
**Code**: `HEURISTIC_ONLY_WHEN_CODE_EXISTS`

### Rule 6: FAMILY_MANUAL_ANALYSIS_REQUIRED
**Condition**: Any registry entry exists for a family
**Check**: `reports/.../manual-analysis/family/{family}.md` must exist
**Fail if**: Family has registry entries but no manual analysis file
**Code**: `FAMILY_MANUAL_ANALYSIS_MISSING`

### Rule 7: IMPLEMENTATION_MODEL_REQUIRED
**Condition**: Any registry entry exists
**Check**: `implementation_model` must be non-null and a valid enum value
**Fail if**: Field is null, empty, or UNKNOWN_NEEDS_MANUAL_REVIEW
**Code**: `IMPLEMENTATION_MODEL_MISSING`

### Rule 8: HISTORY_REQUIRED
**Condition**: Any registry entry exists
**Check**: `history` list must have at least 1 record with `date`, `status`, `analyst_notes`
**Fail if**: `history` is empty or missing
**Code**: `HISTORY_RECORD_MISSING`

### Rule 9: TRANSFORMATION_PLAN_REQUIRES_PROVENANCE
**Condition**: Transformation plan exists for entry
**Check**: `evidence_paths` must reference a product page URL or source code URL
**Fail if**: Transformation plan has no provenance link
**Code**: `TRANSFORMATION_PLAN_NO_PROVENANCE`

### Rule 10: REGISTRY_STATUS_REQUIRED
**Condition**: Every entry
**Check**: `registry_status` must be non-null valid enum
**Fail if**: Field missing or null
**Code**: `REGISTRY_STATUS_MISSING`

### Rule 11: NEXT_ACTION_REQUIRED
**Condition**: Every entry
**Check**: `next_action` must be non-empty, actionable string
**Fail if**: Field is null, empty, or "TBD"
**Code**: `NEXT_ACTION_MISSING`

### Rule 12: EVIDENCE_PATHS_REQUIRED
**Condition**: Every entry
**Check**: `evidence_paths` must have at least 1 entry
**Fail if**: Empty or missing
**Code**: `EVIDENCE_PATHS_MISSING`

### Rule 13: WEBSITE_PATTERN_UNVERIFIED_NOT_READY
**Condition**: `registry_status == WEBSITE_PATTERN_UNVERIFIED`
**Check**: Status must NOT be READY_FOR_TRANSFORMATION
**Fail if**: WEBSITE_PATTERN_UNVERIFIED entry also has READY_FOR_TRANSFORMATION
**Code**: `UNVERIFIED_MARKED_READY`

### Rule 14: FAMILY_PROBE_NOT_PLUGIN_COVERAGE
**Condition**: Entry history or notes reference a "family probe"
**Check**: Family probe run result must NOT be cited as proof that this specific plugin works
**Fail if**: Single family probe used to claim N different plugins as PROBE_CONFIRMED
**Code**: `FAMILY_PROBE_AS_PLUGIN_COVERAGE`
