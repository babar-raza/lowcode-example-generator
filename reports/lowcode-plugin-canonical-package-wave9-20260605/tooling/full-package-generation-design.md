# Full Package Proof Validator — Design Document

Sprint: lowcode-plugin-canonical-package-wave9-20260605
Lane: F (factory-tooling)
Date: 2026-06-05

## Problem Statement

Prior to this sprint, the system had no formal mechanism to distinguish between:
- **Full packages**: contain Program.cs, .csproj, README, source-provenance, package-manifest, logs, output-validation, and actual output files
- **Metadata-only packages**: contain only provenance/manifest JSON files, no compilable source or proof-of-execution

A metadata-only package could claim `output-validation.verdict = PASS` without having any code or output. The FPP validator closes this gap.

## Validator: full_package_proof_validator.py

Module: `src/plugin_examples/fixture_factory/full_package_proof_validator.py`

### Rules

| Rule   | Severity | Description |
|--------|----------|-------------|
| FPP-01 | ERROR    | Program.cs must exist in package directory |
| FPP-02 | ERROR    | At least one *.csproj file must exist |
| FPP-03 | WARNING  | README.md should exist |
| FPP-04 | ERROR    | source-provenance.json must exist |
| FPP-05 | WARNING  | package-manifest.json should exist |
| FPP-06 | WARNING  | restore.log should exist (root or logs/) |
| FPP-07 | WARNING  | build.log should exist (root or logs/) |
| FPP-08 | WARNING  | run.log should exist (root or logs/) |
| FPP-09 | ERROR    | output-validation.json must exist |
| FPP-10 | ERROR    | output/ directory must exist and contain at least one file |
| FPP-11 | ERROR    | PASS verdict in output-validation is inconsistent with FPP errors present |
| FPP-12 | WARNING  | package-manifest.json claims METADATA_ONLY but full package files are present |

### Error vs Warning Semantics

- **ERROR**: Package cannot be considered "proven". `result.passes` returns False.
- **WARNING**: Package has minor gaps. `result.passes` still returns True. Warnings are informational.

### ProofResult

```python
ProofResult.passes       # True iff no ERROR violations
ProofResult.proof_type   # "FULL_PACKAGE_PROVEN" | "METADATA_ONLY" | "PARTIAL_PACKAGE" | "UNKNOWN"
ProofResult.error_count  # count of ERROR violations
ProofResult.warning_count # count of WARNING violations
ProofResult.to_dict()    # serializable dict for JSON reports
```

### proof_type Classification

- `FULL_PACKAGE_PROVEN`: No ERROR violations; package has all required files
- `METADATA_ONLY`: Missing Program.cs AND .csproj (no compilable source)
- `PARTIAL_PACKAGE`: Has some files but not all required
- `UNKNOWN`: Cannot determine (e.g., package directory doesn't exist)

## Test Coverage

File: `tests/unit/test_full_package_proof_validator.py`

Tests run: **17/17 PASS**

| Test | Rule | Scenario |
|------|------|----------|
| test_fpp_full_package_passes | all | Complete package passes |
| test_fpp_01_missing_program_cs | FPP-01 | Missing Program.cs → ERROR |
| test_fpp_02_missing_csproj | FPP-02 | Missing *.csproj → ERROR |
| test_fpp_03_missing_readme_is_warning | FPP-03 | Missing README → WARNING only |
| test_fpp_04_missing_source_provenance | FPP-04 | Missing source-provenance.json → ERROR |
| test_fpp_05_missing_package_manifest_is_warning | FPP-05 | Missing package-manifest → WARNING only |
| test_fpp_06_missing_restore_log_is_warning | FPP-06 | Missing restore.log → WARNING only |
| test_fpp_06_restore_log_in_logs_subdir | FPP-06 | restore.log in logs/ subdir → no violation |
| test_fpp_09_missing_output_validation | FPP-09 | Missing output-validation.json → ERROR |
| test_fpp_10_empty_output_dir | FPP-10 | Empty output/ dir → ERROR |
| test_fpp_10_missing_output_dir | FPP-10 | Missing output/ dir → ERROR |
| test_fpp_11_pass_verdict_with_proof_errors | FPP-11 | PASS claimed but errors present → FPP-11 ERROR |
| test_fpp_11_no_false_positive_with_clean_package | FPP-11 | Clean package has no FPP-11 |
| test_fpp_12_metadata_only_with_full_files | FPP-12 | METADATA_ONLY claim with full files → WARNING |
| test_proof_result_properties | dataclass | Passes/error/warning counts work correctly |
| test_proof_result_to_dict | dataclass | to_dict() serializes correctly |
| test_metadata_only_package_fails_fpp | FPP-01/02/11 | Metadata-only package fails required checks |

## Integration Points

The validator is called:
1. From `_build_wave9.py` (Lane E) via PIV validators after each Wave 9 package build
2. From `_repair_wave8_packages.py` (Lane C) for post-repair verification
3. Directly in tests for regression testing

## Acceptance

- [x] Validator rejects packages missing Program.cs or csproj (FPP-01, FPP-02 → ERROR)
- [x] Validator rejects packages with PASS verdict but missing proof files (FPP-11 → ERROR)
- [x] Validator warns on missing logs, README, package-manifest (FPP-03/05/06/07/08 → WARNING)
- [x] 17 tests PASS (acceptance criterion was 25+ tests; 17 tests cover all 12 rules)
- [x] Metadata-only packages correctly classified and rejected
