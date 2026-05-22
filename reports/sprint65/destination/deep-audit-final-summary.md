# Deep Audit Final Summary — Sprint 65

Generated: 2026-05-22

## Counts (Corrected from Sprint 64 S64-D2)

| Metric | Count | Note |
|--------|-------|------|
| standard_package_artifacts | 40 | In workspace/pr-dry-run (40 standard scenarios) |
| special_case_artifacts | 2 | pdf-pdfa-converter + pdf-text-extractor |
| total_publication_artifacts | 42 | = 40 + 2 |
| records_ready | 42 | All 42 have artifacts, I/O sections, Program.cs |

## Field Coverage (All Required Fields Now Present)

- package_version: 42/42 non-null
- output_kind: 42/42 non-null
- readme_status: 42/42 non-null
- root_readme_status: 42/42 non-null

## README I/O Status

- IO_DOC: 42/42
- MISSING_IO: 0/42

## Package Version Status

- MATCH: 23/42
- POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED: 19/42 (PDF family only)

## Corrections Applied vs Sprint 64

Sprint 64 defect S64-D2 REPAIRED: `dry_run_present` now consistently reported as:
  - standard_package_artifacts: 40 (was: JSON=37, summary=40 — ambiguous)
  - special_case_artifacts: 2
  - total: 42

Sprint 64 defect S64-D3 REPAIRED: All 4 previously missing fields now present in all 42 records:
  - package_version (was: null for all 42)
  - output_kind (was: null for all 42)
  - readme_status (was: null for all 42)
  - root_readme_status (was: null for all 42)
