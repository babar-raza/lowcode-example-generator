# Pipeline Integration Proof — Sprint 67

Date: 2026-05-22

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

## Sprint 67 Status

Both gates carried forward from Sprint 66. No code changes were required.
Sprint 67 adds 10 new EV rules (rules 43-52) and 57-category ECC contract.
