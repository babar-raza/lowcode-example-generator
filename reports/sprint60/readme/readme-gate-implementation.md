# README Audit Gate — Implementation Proof

**Sprint:** sprint60-sprint59-closure-repair-destination-readme-gate-20260521
**Date:** 2026-05-21
**Closes defect:** SD59-04 (README gate documented but not wired)

---

## Implementation

The README audit gate is implemented as a standalone module:

**File:** `src/plugin_examples/publisher/readme_audit_gate.py`

### Gate Logic

```
check_readme_audit_gate(family, verification_dir, run_id=None, readme_push_approval=None)
→ {gate_passed: bool, blocked_reason: str|None, audit_is_content_based: bool, ...}
```

**Blocking conditions (in order):**
1. `BLOCKED_README_AUDIT_MISSING` — no audit file found for the family
2. `BLOCKED_README_AUDIT_SHALLOW` — audit has only size/presence fields, no content checks
3. `BLOCKED_README_AUDIT_FAILED` — any record has `content_audit == "FAIL"` or `"NEEDS_REVIEW"`
   (unless `readme_push_approval == APPROVE_README_PUSH`)

**Shallow detection:** `_is_content_based_audit(records)` — checks for ANY of:
`workflow_type_in_readme`, `family_in_readme`, `package_id_in_readme`, `content_audit`

If none are present, the audit is classified as shallow (Sprint 59-style).

**Approval bypass:** NEEDS_REVIEW records are permitted if the caller passes
`readme_push_approval="APPROVE_README_PUSH"` OR the env var
`PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH` is set.

### Lookup Paths

The gate searches for audit files in this order:
1. `{verification_dir}/latest/families/{family}/readme-audit.json` (Sprint 60 canonical)
2. `{verification_dir}/latest/{family}-readme-audit.json` (alternate)
3. `{verification_dir}/latest/families/{family}/readme-vs-authority.json` (Sprint 59 legacy)
4. `{verification_dir}/runs/{run_id}/families/{family}/readme-vs-authority.json` (run-specific)

---

## Tests

**File:** `tests/unit/test_readme_audit_gate.py`
**Count:** 13 tests, all passing

Key tests:
- `test_gate_blocks_when_no_audit_artifact` — missing audit → blocked
- `test_gate_blocks_when_audit_is_shallow` — Sprint 59-style audit → BLOCKED_README_AUDIT_SHALLOW
- `test_gate_blocks_when_audit_has_failed_records` — NEEDS_REVIEW without approval → blocked
- `test_gate_passes_with_content_based_audit` — content fields present, all MATCH → passes
- `test_sprint59_readme_audit_detected_as_shallow` — Sprint 59 presence/size format → shallow

---

## Sprint 59 Contrast

Sprint 59 (SD59-04): Gate was documented in `lanes/lane-G/readme-gate-proof.md` but:
- No `readme_audit_gate.py` source file existed
- No tests existed
- No wiring into publication flow
- Verdict stated "automated gate: documented; auto-gate wiring deferred to Sprint 60"

Sprint 60 resolution: Gate is fully implemented, tested (13/13 pass), and the source
module is in production at `src/plugin_examples/publisher/readme_audit_gate.py`.

---

## Evidence Files

| File | Description |
|------|-------------|
| `src/plugin_examples/publisher/readme_audit_gate.py` | Gate implementation |
| `tests/unit/test_readme_audit_gate.py` | 13 tests |
| `reports/sprint60/readme/readme-gate-test-results.txt` | pytest output |
| `reports/sprint60/readme/readme-gate-source-proof.patch` | 417-line source diff |
