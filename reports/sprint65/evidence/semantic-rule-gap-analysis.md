# Sprint 65 Phase 5 — Semantic Rule Gap Analysis

Generated: 2026-05-22
Sprint: sprint65-publication-truth-repair-root-readme-strict-audit-handoff

## Overview

Sprint 64 closed with EV/ECC aligned (22 rules, all PASS). However, independent
review found 8 blocking defects (S64-D1 through S64-D8) that the 22-rule EV did
not detect. This document analyzes each gap and documents the 10 new rules added
to close them.

---

## Sprint 64 Defects vs Rule Coverage

| Defect | Description | Was Rule Present? | Gap |
|--------|-------------|-------------------|-----|
| S64-D1 | Final verdict overclaims publication without remote proof | NO | No rule checked for remote-proof-index.json |
| S64-D2 | count contradiction (dry_run_present=37 vs 40/42 in text) | NO | No rule checked internal count consistency |
| S64-D3 | content-audit-deep.json missing 4 required fields | NO | `42 entries` semantic check only checked `readme_input/output_status` field names (wrong names) |
| S64-D4 | Family root README artifacts missing from bundle | NO | No rule verified root-readme/per-family/ artifacts |
| S64-D5 | Root README audit stale for PDF (26.4.0 vs 26.5.0 policy) | PARTIAL | No rule checked version_policy file contents |
| S64-D6 | Special cases lack destination placement proof | NO | No rule checked special-cases/special-case-publication-map.json |
| S64-D7 | EV/ECC semantic rules too weak (accepted contradictions) | SELF | This document itself is the closure |
| S64-D8 | PDF drift deferred without NOT_REGENERATED label in all files | NO | No rule checked version_policy.total_drift_unresolved |

---

## 10 New Rules Added (Sprint 65)

### Rule 23: `content_audit_final_has_required_fields`
**Closes:** S64-D3

**Gap:** The existing `_check_semantic` "42 entries" check looked for
`readme_input_status`, `readme_output_status`, and `readme_has_io` field names —
but the actual field in Sprint 64 content-audit-deep.json was `readme_status`.
The check always passed because the wrong field names were tested.

**New rule:** Checks `destination/content-audit-final.json` for the fields
`package_version`, `output_format`, `readme_status`, `root_readme_status` in every
record. Fails if any record is missing these fields.

**Validation on Sprint 64 bundle:** `content-audit-deep.json` → `package_version=42 missing, readme_status=42 missing` → FAIL ✓

---

### Rule 24: `content_audit_count_not_contradictory`
**Closes:** S64-D2

**Gap:** No rule compared `standard_package_artifacts` + `special_case_artifacts`
against `total_publication_artifacts` or against `len(records)`.

**New rule:** Checks that:
1. `len(records) == total_publication_artifacts`
2. `standard_package_artifacts + special_case_artifacts == total_publication_artifacts`

**Validation on Sprint 64 bundle:** Sprint 64 deep audit had `dry_run_present=37`
but `len(records)=42` with many `dry_run_present=false`. Contradiction detected → FAIL ✓

---

### Rule 25: `content_audit_all_records_ready`
**Closes:** S64-D2 (corollary)

**Gap:** No rule required all records to reach `READY` or `SPECIAL_CASE_READY`.

**New rule:** Checks `destination/content-audit-final.json` and requires all records
to have `final_readiness` ∈ {`READY`, `SPECIAL_CASE_READY`}.

---

### Rule 26: `root_readme_artifacts_present_for_all_families`
**Closes:** S64-D4

**Gap:** No rule checked for the existence of root README artifacts in the bundle.

**New rule:** Checks `root-readme/per-family/{family}-root-readme.md` for all 6
families: cells, diagram, email, pdf, slides, words.

**Validation on Sprint 64 bundle:** `root-readme/per-family/` not found → FAIL ✓

---

### Rule 27: `special_case_placement_proof_present`
**Closes:** S64-D6

**Gap:** No rule verified placement proof for the 2 PDF special cases.

**New rule:** Checks `special-cases/special-case-publication-map.json` with at
least 2 special cases documented (destination path, package artifact path, hashes).

**Validation on Sprint 64 bundle:** file absent → FAIL ✓

---

### Rule 28: `version_policy_no_unresolved_drift`
**Closes:** S64-D5, S64-D8

**Gap:** No rule checked the version policy file for unresolved drift families.

**New rule:** Reads `version/version-policy-final.json` (Sprint 65+) or
`phase6/version-policy.json` (Sprint 64). Requires `total_drift_unresolved=0`
or all drifting families to have a policy label (POLICY_CLASSIFIED_* or MATCH).

---

### Rule 29: `final_verdict_no_publication_overclaim`
**Closes:** S64-D1

**Gap:** No rule prevented the verdict from claiming `PUBLICATION_VERIFIED` or
`FULLY_PUBLISHED` without a remote proof artifact.

**New rule:** If `final-verdict.md` contains strong publication keywords
(`PUBLICATION_VERIFIED`, `FULLY_PUBLISHED`, etc.), checks that
`publication/remote-proof-index.json` exists.

---

### Rule 30: `remote_proof_index_present_if_published`
**Closes:** S64-D1 (broader check)

**Gap:** Same gap as rule 29 but for broader publication keywords.

**New rule:** If `final-verdict.md` contains any publication/PR keyword
(`PUBLISHED`, `HANDOFF`, `DRY_RUN`, `APPROVAL_BLOCKED`, etc.),
`publication/remote-proof-index.json` must exist.

**Validation on Sprint 64 bundle:** Verdict contains `APPROVAL_BLOCKED` and
`DRY_RUN` but no remote-proof-index.json → FAIL ✓

---

### Rule 31: `content_audit_readme_io_coverage`
**Closes:** S64-D3 (corollary)

**Gap:** No rule checked README I/O coverage percentage.

**New rule:** Requires at least `max(40, total-2)` records to have
`readme_status=IO_DOC`. Catches cases where README corrections weren't applied.

---

### Rule 32: `revalidation_shows_prior_sprint_invalid`
**Closes:** S64-D7

**Gap:** No rule verified that prior sprint revalidation actually failed.
A sprint could add rules that pass trivially on the prior sprint, defeating the
purpose of revalidation.

**New rule:** Reads `evidence/*revalidation*.json`. Requires `overall_valid=false`.
If the prior sprint passes under new rules, the rules are too weak.

---

## Summary

| Rule # | Rule ID | Severity | Closes |
|--------|---------|----------|--------|
| 23 | content_audit_final_has_required_fields | FAILURE | S64-D3 |
| 24 | content_audit_count_not_contradictory | FAILURE | S64-D2 |
| 25 | content_audit_all_records_ready | FAILURE | S64-D2 |
| 26 | root_readme_artifacts_present_for_all_families | FAILURE | S64-D4 |
| 27 | special_case_placement_proof_present | FAILURE | S64-D6 |
| 28 | version_policy_no_unresolved_drift | FAILURE/WARNING | S64-D5, S64-D8 |
| 29 | final_verdict_no_publication_overclaim | FAILURE | S64-D1 |
| 30 | remote_proof_index_present_if_published | FAILURE | S64-D1 |
| 31 | content_audit_readme_io_coverage | FAILURE | S64-D3 |
| 32 | revalidation_shows_prior_sprint_invalid | FAILURE/WARNING | S64-D7 |

Total EV rules: 32 (was 22 + 10 new)
Source proof: `semantic-rule-source-proof.patch` (564 lines, +539 insertions)
