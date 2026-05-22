# Deep Audit Summary — Sprint 64

## content-audit-deep.json

**Sprint 63 defect S63-D7 fixed:** All 42 records now have `output_format`, `api_type`,
`full_type_name`, and `operation_kind` fields derived from format-authority contracts.

- Total records: 42/42
- output_format populated: 42/42
- api_type populated: 42/42
- dry_run_present: 40/42 (2 special cases without dry-run)

## programcs-vs-authority-deep.json

Uses corrected final ledger from Phase 4.
- 40/42 direct MATCH
- 2/42 KNOWN_SPECIAL_CASE (words-mail-merger, words-report-builder)
- 0/42 unexplained mismatch
- 0/42 authority_unknown

## readme-vs-authority-deep.json

Copied from Sprint 63. Phase 5 will apply README I/O corrections and update this.

## root-readme-vs-package-deep.json

Copied from Sprint 63. Shows:
- 5/6 families: version_match = true
- 1/6 (pdf): version_drift (26.4.0 dry-run vs 26.5.0 NuGet)

Phase 6 will resolve PDF version drift.
