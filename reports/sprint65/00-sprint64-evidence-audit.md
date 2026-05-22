# Sprint 65 Phase 0 — Sprint 64 Evidence Audit

## Audit Date: 2026-05-22
## Auditor: Independent Sprint 65 review

Sprint 64 is NOT accepted as final closure. The evidence bundle shows strong progress
on dry-run packaging and EV/ECC alignment, but the final verdict overclaims publication
and destination-readiness in 8 distinct ways.

---

## Blocking Defect 1: Verdict Overclaims Publication (S64-D1)

**Classification:** CONTRADICTED

**Evidence:**
- `publication/publication-readiness-result.json` states:
  - `live_publication_attempted=false`
  - `remote_mutation=false`
  - `publication_status=BLOCKED_BY_APPROVAL`
- `sprint-state.json` states: `publication=BLOCKED_BY_APPROVAL_42_42_PUBLISHED_SPRINT62`
- `final-verdict.md` claims: "All 42 examples published in Sprint 62"

**Problem:**
- Sprint 64 bundle does NOT include remote repo proof (PR URLs, merge SHAs, post-merge
  content verification). Remote proof exists in `workspace/verification/latest/` (gitignored)
  but was never transferred to the evidence bundle.
- A closure verdict cannot cite "published in Sprint 62" without that sprint's remote proof
  being present or referenced from a canonically committed location.
- The distinction between dry-run readiness and live publication is blurred.

**Correct State:**
Remote proof (merge results, PR URLs) exists in workspace but is NOT in the evidence bundle.
Sprint 65 must extract and commit this proof before publication can be claimed.

---

## Blocking Defect 2: Destination Audit Contradiction (S64-D2)

**Classification:** CONTRADICTED

**Evidence:**
- `destination/content-audit-deep.json`: `dry_run_present=37/42`
- `destination/deep-audit-summary.md`: "dry_run_present: 40/42 (2 special cases without dry-run)"

**Problem:**
37 ≠ 40. Neither count is clearly labeled as standard vs. total.
The 5 scenarios NOT dry_run_present: diagram-diagram-converter, diagram-pdf-converter,
pdf-html-converter, pdf-pdfa-converter, pdf-text-extractor.
Of these, 2 are genuine special cases (pdf-pdfa-converter, pdf-text-extractor).
But 3 others (diagram-diagram-converter, diagram-pdf-converter, pdf-html-converter)
should be in the dry-run workspace but appear absent.

**Correct State:**
Must reconcile: standard_package_artifacts=40, special_case_artifacts=2, total=42.
The 3 diagram/pdf-html records need investigation.

---

## Blocking Defect 3: Destination Audit Missing Required Fields (S64-D3)

**Classification:** INVALID_CLOSURE

**Evidence:**
- `destination/content-audit-deep.json` record keys: scenario_id, family, dry_run_present,
  pkg_version, output_format, api_type, full_type_name, operation_kind, input_format,
  authority_match, gap_classification, readme_present, readme_has_io
- **Missing:** package_version, output_kind, readme_status, root_readme_status

**Problem:**
Sprint 65 specification requires all 4 fields for destination-readiness.
`pkg_version` exists but is not the canonical `package_version` field.
No `readme_status` field means README I/O claim is not traceable per-record.
No `root_readme_status` means root README inclusion is not tracked.

---

## Blocking Defect 4: Root README Artifacts Missing (S64-D4)

**Classification:** INVALID_CLOSURE

**Evidence:**
- Sprint 64 bundle contains `reports/sprint64/readme/` but only:
  - example-readme-content-audit.json
  - readme-gate-implementation.md
  - readme-gate-source-proof.patch
  - readme-gate-test-results.txt
- No root README artifacts (actual README.md content or diffs for the 6 destination repos)
- `phase5/root-readme-audit-after-application.json` has family entries but no actual artifacts

**Correct State:**
Family root README artifacts must be extracted from workspace/pr-dry-run/ and committed.

---

## Blocking Defect 5: Root README Audit Stale for PDF (S64-D5)

**Classification:** CONTRADICTED

**Evidence:**
- `phase5/root-readme-audit-after-application.json`: PDF `package_version=26.4.0`
- `phase6/version-policy.json`: PDF classified at 26.5.0

**Problem:**
Root README audit was not re-run after PDF version policy update.
The audit shows stale 26.4.0 while version policy says 26.5.0.

---

## Blocking Defect 6: Special Cases Lack Destination Placement Proof (S64-D6)

**Classification:** INVALID_CLOSURE

**Evidence:**
- `destination-packages/special-cases/` has: Program.cs, README.md, .csproj for each
- `special-cases-manifest.json` lists source paths and hashes
- **Missing:** canonical destination_repo, destination_path, root_readme_index_entry

**Correct State:**
Must specify exactly WHERE in the PDF destination repo each special case will be placed.

---

## Blocking Defect 7: EV/ECC Semantic Rules Too Weak (S64-D7)

**Classification:** PARTIALLY_VERIFIED

**Evidence:**
- EV/ECC now agree: 22/22 rules pass, 44/44 PRESENT
- But EV/ECC accepted:
  - destination audit with null fields
  - root README audit without artifacts
  - publication claim without remote proof
  - count contradictions (37 vs 40)

**Correct State:**
Sprint 65 must add 10 new semantic rules to prevent these classes of overclaim.

---

## Blocking Defect 8: PDF Version Drift Deferred (S64-D8)

**Classification:** PARTIALLY_VERIFIED

**Evidence:**
- `phase6/pdf-version-drift-resolution.md`: POLICY_CLASSIFIED_CALENDAR_VERSION_BUMP
- `phase6/version-policy.json`: PDF at 26.5.0 (policy-classified)
- **But:** No PDF build/run/audit at 26.5.0 was performed
- Root README audit still shows 26.4.0

**Correct State:**
Path B (policy-classified) is acceptable but must be explicitly labeled
`POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED` in all relevant files.

---

## Sprint 64 Items Accepted (Not Re-opened)

1. **EV/ECC alignment** — VERIFIED (22/22 rules pass post-commit)
2. **ECC timing fix** — VERIFIED (ECC run after final commit)
3. **42/42 clean package artifacts** — VERIFIED (0 obj/bin, 126 files)
4. **README I/O sections** — PARTIALLY_VERIFIED (42/42 have sections, but dst placement not proven)
5. **Program.cs authority 42/42** — VERIFIED (40 MATCH + 2 KNOWN_SPECIAL_CASE)
6. **2993 tests pass** — VERIFIED
7. **No unauthorized remote mutation** — VERIFIED
8. **ECC semantic bugs fixed (3)** — VERIFIED

---

## Corrected Sprint 64 Verdict

**OLD:** `LOWCODE_README_IO_DRY_RUN_PACKAGES_READY_42_OF_42_PUBLICATION_BLOCKED_BY_APPROVAL`
**CORRECTED:** `LOWCODE_DRY_RUN_PACKAGES_STRONG_PROGRESS_PUBLICATION_PROOF_MISSING`

Sprint 64 had strong dry-run progress but the final evidence bundle does not support
a publication-ready verdict due to 8 blocking defects.
