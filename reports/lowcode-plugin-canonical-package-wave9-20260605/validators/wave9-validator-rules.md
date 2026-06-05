# Wave 9 Validator Rules

Sprint: lowcode-plugin-canonical-package-wave9-20260605
Lane: G (validators)
Date: 2026-06-05

## CCV-01..CCV-14: Closeout Consistency Validators

Module: `src/plugin_examples/fixture_factory/closeout_consistency_validators.py`

### Rules Table

| Rule   | Severity | Trigger Condition |
|--------|----------|-------------------|
| CCV-01 | ERROR    | Sprint verdict is COMPLETE but evidence_bundle is PENDING |
| CCV-02 | ERROR    | Sprint verdict is COMPLETE but lane-ledger lanes are PENDING/IN_PROGRESS |
| CCV-03 | ERROR    | Sprint verdict is COMPLETE but taskcards are PENDING/IN_PROGRESS |
| CCV-04 | ERROR    | Closeout claims test count but no test log file found in report dir |
| CCV-05 | WARNING  | Sprint is COMPLETE but no git-status.txt found |
| CCV-06 | WARNING  | Sprint is COMPLETE but no commit_sha recorded in closeout |
| CCV-07 | ERROR    | CANONICAL_IDENTITY_VERIFIED entry missing canonical_url |
| CCV-08 | WARNING  | CANONICAL_IDENTITY_VERIFIED entry missing display_plugin_name |
| CCV-09 | ERROR    | Publication-clean candidate missing canonical_url |
| CCV-10 | ERROR    | Package with verdict=PASS missing Program.cs (metadata-only PASS fraud) |
| CCV-11 | ERROR    | Package with verdict=PASS missing *.csproj |
| CCV-12 | WARNING  | Package with verdict=PASS missing log files |
| CCV-13 | ERROR    | Legacy alias slug appears as publication-clean candidate |
| CCV-14 | ERROR/WARNING | Publication matrix missing canonical_url column entirely (ERROR) or partially (WARNING) |

### Test Results

- Tests: `tests/unit/test_closeout_consistency_validators.py`
- Result: **45/45 PASS**

### CCV vs FPP Distinction

- **FPP** (Full Package Proof) validates individual package directories — files present, output present
- **CCV** (Closeout Consistency) validates sprint governance documents — closeout, lane-ledger, taskcards, registry, matrix

Both validators share the pattern: ERROR = blocks pass, WARNING = informational.
