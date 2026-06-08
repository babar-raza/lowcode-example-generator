# Canonical Page Registry Validator Rules
## Sprint: lowcode-plugin-registry-expansion-20260604 | Date: 2026-06-04

## Purpose
Prevent regression to pattern-only or reflection-first READY_FOR_TRANSFORMATION entries.
All rules operate on the `pipeline/plugin-code-registry/family/*.yaml` files.

---

## Rule Set

### R01: READY_FOR_TRANSFORMATION requires canonical_url
- **Condition**: `registry_status == READY_FOR_TRANSFORMATION`
- **Requirement**: `canonical_url` MUST be present and non-empty
- **Violation class**: REGISTRY_READINESS_DEFECT
- **Rationale**: Cannot be transformation-ready without a confirmed canonical product page URL

### R02: READY_FOR_TRANSFORMATION requires page_source_status
- **Condition**: `registry_status == READY_FOR_TRANSFORMATION`
- **Requirement**: `page_source_status` MUST be one of: `CANONICAL_URL_CONFIRMED`, `PAGE_CRAWLED_THIS_SPRINT`, `CANONICAL_URL_BEST_MATCH`
- **Note**: `CANONICAL_URL_BEST_MATCH` is accepted but generates a WARNING (not a blocking violation). It means a strong inference match without direct page fetch confirmation.
- **Violation class**: REGISTRY_READINESS_DEFECT (for missing/unknown values only)

### R03: READY_FOR_TRANSFORMATION requires implementation_model
- **Condition**: `registry_status == READY_FOR_TRANSFORMATION`
- **Requirement**: `implementation_model` MUST be set and not null
- **Violation class**: REGISTRY_READINESS_DEFECT

### R04: READY_FOR_TRANSFORMATION requires classes_used or methods_used
- **Condition**: `registry_status == READY_FOR_TRANSFORMATION`
- **Requirement**: At least one of `classes_used` or `methods_used` MUST be non-empty
- **Violation class**: REGISTRY_READINESS_DEFECT
- **Rationale**: Transformation requires knowing what classes/methods to use

### R05: No CODE_HARVESTED entry may have canonical_url without advancing
- **Condition**: `registry_status == CODE_HARVESTED` AND `canonical_url` is present
- **Requirement**: Must advance to `READY_FOR_TRANSFORMATION` or document a blocker
- **Violation class**: REGISTRY_STALENESS_WARNING
- **Severity**: WARNING (not blocking)

### R06: NEEDS_MANUAL_MAPPING must have a next_action
- **Condition**: `registry_status == NEEDS_MANUAL_MAPPING`
- **Requirement**: `next_action` MUST be non-empty
- **Violation class**: REGISTRY_COMPLETENESS_DEFECT

### R07: transformation_readiness_reason required for READY_FOR_TRANSFORMATION
- **Condition**: `registry_status == READY_FOR_TRANSFORMATION`
- **Requirement**: `transformation_readiness_reason` MUST be non-empty
- **Violation class**: REGISTRY_READINESS_DEFECT

### R08: Protected family registries are read-only
- **Condition**: Files in `pipeline/plugin-code-registry/family/` for families: `cells`, `words`, `pdf`, `slides`, `email`, `diagram`
- **Requirement**: These files MUST NOT be modified by this sprint
- **Violation class**: PROTECTED_REGISTRY_MUTATION — CRITICAL

### R09: No reflection-first discovery
- **Condition**: Any entry
- **Requirement**: `registry_status` MUST NOT be set to `READY_FOR_TRANSFORMATION` based solely on DllReflector output without page evidence
- **Enforcement**: Validated by presence of `canonical_url` (R01) and `page_source_status` (R02)
- **Violation class**: AUTHORITY_ORDER_VIOLATION — CRITICAL

### R10: Dry-run packages must have package-manifest.json
- **Condition**: Any directory under `reports/*/dryrun/examples/`
- **Requirement**: A `package-manifest.json` file MUST exist in the package directory
- **Violation class**: DRYRUN_COMPLETENESS_DEFECT

---

## Application to Current Sprint

All 10 rules applied to this sprint's output. See `registry-readiness-validator-results.json`.
