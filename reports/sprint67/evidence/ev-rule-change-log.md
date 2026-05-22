# EV Rule Change Log — Sprint 67

Date: 2026-05-22
Sprint: sprint67

## Summary

| Metric | Before (Sprint 66) | After (Sprint 67) |
|--------|-------------------|--------------------|
| Total rules | 42 | 52 |
| validate_for_storage rules | 41 | 51 |
| New rules added | — | 10 |

## New Rules (43-52)

| Rule ID | Rule Method | Purpose |
|---------|-------------|---------|
| 43 | `cardinality_audit_json_present` | S66-D1: root-readme/cardinality-audit.json must exist |
| 44 | `root_readme_cardinality_annotated` | S66-D1: cells README must show xN markers for merger/splitter |
| 45 | `pdf_version_decision_record_present` | S66-D2: version/pdf-version-decision.md must exist |
| 46 | `version_truth_matrix_present` | S66-D2: version/version-truth-matrix.json must exist |
| 47 | `no_cross_sprint_path_leakage` | S66-D3: content-audit must have no stale sprint refs |
| 48 | `legacy_plans_reconciliation_present` | S66-D5: legacy-plan-reconciliation/reconciliation-index.md must exist |
| 49 | `content_audit_sprint_specific_present` | Sprint-specific content audit must be present |
| 50 | `handoff_index_per_family_complete` | All 6 family handoff-index.json files must exist |
| 51 | `readme_sync_state_present` | readme-sync/sync-state.json must exist |
| 52 | `remote_truth_refresh_present` | remote/remote-proof-summary.md must exist |

## ECC Contract Update

Sprint 67 ECC contract: 57 categories (EC01-EC57)
Sprint 66 ECC contract: 46 categories

## Test Coverage

84 unit tests in test_evidence_validator.py — all passing.
5 unit tests in test_pipeline_evidence_gate.py — all passing.
