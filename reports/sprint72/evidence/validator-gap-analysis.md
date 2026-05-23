# Validator Gap Analysis — Sprint 72

**Sprint:** sprint72
**Date:** 2026-05-23
**Defect Closed:** S71-D1

## Gap Identified

Sprint 71 had EV rules 73–78 that checked stale sprint paths in content-audit-final.json,
publication-truth-matrix-final.json, handoff-index.json, and remote-vs-handoff-final.json.

However, there was **no rule** that checked for contradictions between:
1. `remote/remote-proof-summary.md` — states the README I/O section count
2. `remote/remote-readme-io-audit-final.json` — contains the actual io_doc_count

This gap allowed the Sprint 68 artifact (claiming "42/42 examples have README I/O sections")
to be carried forward through Sprints 69, 70, and 71 without being detected by EV.

## Root Cause

The Sprint 68 `remote-proof-summary.md` conflated two facts:
- **True:** 42/42 examples are published in remote repos
- **False:** 42/42 remote READMEs have I/O sections (actual: 0/42)

No EV rule cross-checked the summary against the audit.

## Rules Added (Sprint 72)

Seven new EV rules added in `src/plugin_examples/evidence_validator.py`:

| Rule ID | Rule Name | What It Catches |
|---------|-----------|-----------------|
| 79 | `remote_proof_consistency_audit_present` | Missing remote-proof-consistency-audit.json |
| 80 | `remote_proof_consistency_audit_consistent` | consistent=false in consistency audit |
| 81 | `remote_proof_summary_states_zero_io` | summary claiming non-zero when audit says 0 |
| 82 | `remote_proof_summary_not_contradicted` | summary io_count contradicts audit io_doc_count |
| 83 | `remote_proof_summary_superseded_archived` | Missing superseded document in history/ |
| 84 | `remote_readme_io_audit_count_consistent` | Internal inconsistency in io_doc_count vs records |
| 85 | `remote_vs_handoff_uses_current_sprint` | Stale sprint paths in remote-vs-handoff-final.json |

## Sprint 71 Revalidation

Sprint 71 bundle (`reports/sprint71/`) fails rules 81 and 82 under Sprint 72 EV rules:
- Rule 81 fails: `remote-proof-summary.md` claims "42/42 examples have README I/O sections"
- Rule 82 fails: summary contradicts audit (io_doc_count=0)

This is the expected behavior — Sprint 71 has the defect Sprint 72 repairs.

## Conclusion

Sprint 72 hardens the validator to catch remote proof contradictions.
The gap is now closed: if any future sprint carries forward an incorrect remote proof
summary, EV rules 79–85 will detect it immediately.
