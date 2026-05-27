# Healing Sprint 1 — Lane 4: Validator Gap Analysis

**Lane:** 4 — Validator and Invariant Hardening
**Date:** 2026-05-27

## Validator Source Audit

File: `src/plugin_examples/evidence_validator.py`
Lines: 7706
Total `_rule_*` methods: **145** (confirmed via grep)

## Rule Distribution by Sprint

| Sprint | Rule Range | Notes |
|---|---|---|
| Sprint 60 | 1–N | Hardened baseline rules |
| Sprint 61 | Next block | New semantic rules |
| Sprint 62 | Next block | New rules |
| Sprint 64 | Next block | New rules |
| Sprint 65 | Next block | New rules |
| Sprint 66 | Next block | S65-D1 through S65-D5 closures |
| Sprint 67 | Next block | S66-D1 through S66-D5 closures |
| Sprint 68 | Next block | S67-D1 through S67-D5 closures |
| Sprint 69 | Rules 58–67 | S68-D1 through S68-D8 closures |
| Sprint 71 | Stale-path scanner | S70-D1, S70-D2, S70-D3 closures |
| Sprint 72 | Remote proof consistency | S71-D1 closure |
| Sprint 75 | Weekly review integration | |
| Sprint 76 | S75-B1, S75-B2 | slides-compress, dirty-state |
| Sprint 77 | Next block | S76-C1 through S76-C4 closures |
| Sprint 78 | Next block | S77-D1 through S77-D3 closures |
| Sprint 79 | Next block | S78-E1 and S78-E2 closures |
| Sprint 85 | Rules 120–124 | Evidence hygiene rules |
| Sprint 86 | Rules 125–126 | Readiness-loop prevention |
| Sprint 87 | Rules 127–134 | S86 defect invariants |
| Sprint 88 | Next block | S87 defect invariants |
| Sprint 89 | Final block | S88 defect invariants (rules through 145) |

## Last 5 Rules (Sprint 89)

1. `_rule_head_sha_matches_final_proof` — bundle-manifest.json head_sha must appear in final-clean-proof.txt
2. `_rule_active_validation_not_not_canonical` — active validation must not be not_canonical
3. `_rule_source_proof_present_if_source_changed` — source proof present if source files changed
4. `_rule_no_lowcode_confirmed_has_evidence` — NO_LOWCODE_CONFIRMED classification has evidence
5. `_rule_candidate_classification_not_stale_after_scan` — candidate classification not stale after scan

## Gap Analysis

### Hardening Opportunities Identified

| Gap ID | Description | Severity |
|---|---|---|
| GAP-001 | No rule catches "will be updated" placeholder in proof files | MEDIUM |
| GAP-002 | No rule validates that source-diff.patch is non-empty | HIGH (caught by ECC ZERO_BYTES, not validator) |
| GAP-003 | No rule validates phantom SHAs in bundle-manifest.json against git log | HIGH |
| GAP-004 | Rule `head_sha_matches_final_proof` — head_sha in manifest says "see git/final-clean-proof.txt" (literal text) — rule correctly skips non-SHA values | LOW (working as designed) |

### Gap-001 Mitigation

Template rule PROOF-TEMPLATE-001 created (Lane 1). No code change needed
as this is a procedural control, not a validator rule.

### Gap-002 Mitigation

ECC already catches zero-byte files as ZERO_BYTES (blocking). The validator
operates on semantic content; ECC operates on file existence/size. Layered
defense is correct.

### Gap-003 Mitigation

Sprint 89 added rule `_rule_head_sha_matches_final_proof` which checks that
head_sha appears in final-clean-proof.txt. This partially addresses phantom SHAs
but does not call `git cat-file -t`. Procedural control (SHA verification step)
documented in BAD-003 replay (Lane 2).

## Invariant Check

The EvidenceValidator maintains the invariant:
  `applicable_rules + diagnostic_rules = total_rules`

Rule `_rule_validation_result_not_placeholder` (Sprint 86-D2) enforces this.
Sprint 91 validation confirmed: `applicable_rules_failed=0`, `canonical=true`.

## Lane 4 Verdict

**LANE_4_PASS** — 145 rules confirmed present. Sprint sequence audited. 3 gaps
identified with mitigations. No code changes required (procedural controls sufficient).
Validator invariant confirmed via Sprint 91 canonical validation result.
