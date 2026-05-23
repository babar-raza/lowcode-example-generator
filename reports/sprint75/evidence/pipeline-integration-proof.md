# Pipeline Integration Proof — Sprint 75

Date: 2026-05-23

## EvidenceValidator Integration

EvidenceValidator is called from `release-status --validate-bundle` command.

Source: `src/plugin_examples/publisher/release_status.py`

The `release-status` command calls `EvidenceValidator(bundle_dir).validate()` and writes
the result JSON to `evidence/{sprint_id}-bundle-validation-result.json`.

## README Gate Integration

The README audit gate (`readme_audit_gate.py`) is called from `publish-pr --publish`.
Gate blocks publication if README audit is missing, shallow, or failed.
Override requires `PLUGIN_EXAMPLES_README_AUDIT_APPROVAL=APPROVE_README_AUDIT_OVERRIDE`.

Source: `src/plugin_examples/publisher/readme_audit_gate.py`

## Sprint 75 Status

Sprint 75 adds 8 new EV rules (rules 86-93) covering weekly review integration:
- weekly_review_claim_matrix_present (rule 86)
- pdf_publication_truth_reconciled (rule 87)
- formimporter_taskcard_durable (rule 88)
- words_version_drift_documented (rule 89)
- email_slides_runtime_validated (rule 90)
- dirty_tree_classified (rule 91)
- sprint27_governance_classified (rule 92)
- weekly_review_verdict_not_complete_while_unclassified (rule 93)

Also adds 3 new allowed verdicts to `_rule_final_verdict_is_precise`:
- LOWCODE_WEEKLY_REVIEW_ITEMS_CLASSIFIED_PUBLICATION_APPROVAL_BLOCKED
- LOWCODE_WEEKLY_REVIEW_REPAIRED_AND_README_IO_PRS_CREATED
- LOWCODE_PUBLICATION_AND_REVIEW_ITEMS_PARTIAL_WITH_EXPLICIT_BLOCKERS

Total EV rules: 93. No other pipeline code changes required in this sprint.
