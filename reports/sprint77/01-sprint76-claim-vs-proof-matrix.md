# Sprint 76 Claim vs Proof Matrix — Sprint 77

**Date:** 2026-05-24
**Evaluator:** Sprint 77 independent review

| # | Sprint 76 Claim | Classification | Notes |
|---|-----------------|----------------|-------|
| 1 | Slides Compress runtime validated (input.pptx 34242→output.pptx 19807 bytes, 42.2%) | VERIFIED | Binary proof in post-merge-runtime/. Hash confirmed. |
| 2 | All 4 Email/Slides examples post_merge_validated=true, output_confirmed=true | VERIFIED | post-merge-validation-matrix.json consistent |
| 3 | S75-B1 repaired (overclaim corrected) | VERIFIED | output_confirmed now true. Matrix updated. |
| 4 | S75-B2 repaired (dirty-state contradiction) | VERIFIED | Root cause documented. dirty-state-before/after consistent. |
| 5 | 8 new EV rules (94-101) added | VERIFIED | tests/unit/test_evidence_validator.py updated |
| 6 | 3052/3052 tests pass | VERIFIED | test-run log confirms 3052 passed, 3 skipped |
| 7 | EV 101/101 applicable rules | PARTIALLY_VERIFIED | 17 sprint76-applicable rules pass; full 101-rule run had 61 non-applicable fails — ambiguous naming |
| 8 | ECC 31/31, closure_valid=true | VERIFIED | evidence-contract-computed.json confirms |
| 9 | dirty workspace: only 7 workspace/verification/latest/ files | CONTRADICTED | dirty-state-after.txt also shows `?? output.pptx` — omitted from final-verdict.md |
| 10 | final-clean-proof.txt: SHA 47c584d confirmed | PARTIALLY_VERIFIED | SHA present but proof is narrative-only, no raw git output |
| 11 | commands.log complete | INVALID_CLOSURE | commands.log has 2 `PENDING` entries (Phase 4 and Phase 6) |
| 12 | Validation result: overall_valid=true | AMBIGUOUS | two files with different answers; sprint76-bundle-validation-result.json says false |
| 13 | Publication: APPROVAL_BLOCKED, 0 PRs | VERIFIED | No unauthorized publication |
| 14 | Bundle type: REPAIR_SPRINT | VERIFIED | bundle-manifest.json has bundle_type: REPAIR_SPRINT |

**Classifications used:**
- **VERIFIED** — claim is supported by evidence, no gaps
- **PARTIALLY_VERIFIED** — claim is mostly true but has minor gaps
- **CONTRADICTED** — evidence directly contradicts the claim
- **INVALID_CLOSURE** — claim cannot stand as-is; repair required
- **AMBIGUOUS** — claim is unclear due to conflicting evidence files
- **REPAIRED_IN_SPRINT77** — will be repaired in this sprint
