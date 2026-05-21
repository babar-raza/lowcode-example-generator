# Sprint 59 Claim-vs-Proof Matrix — Sprint 60 Phase 0

**Date:** 2026-05-21
**Sprint 59 Claims Source:** `reports/sprint59/final-verdict.md`, `reports/sprint59/sprint-state.json`

Legend:
- **VERIFIED** — claim is backed by matching evidence
- **PARTIALLY_VERIFIED** — claim is partially backed; notable gaps exist
- **CONTRADICTED** — claim is contradicted by included evidence
- **INVALID_CLOSURE** — claim cannot be assessed because required proof is absent/deferred
- **REPAIRED_IN_SPRINT60** — claim was false in Sprint 59; Sprint 60 provides the repair

---

## Claim Matrix (26 Claims)

| # | Claim | Evidence File | Classification | Notes |
|---|-------|---------------|----------------|-------|
| C01 | "Dirty files at close: 0 (clean after final commit)" | `git/dirty-state-after.txt`, `lanes/lane-I/git-status.txt` | CONTRADICTED | dirty-state-after.txt captured before final commit; git-status.txt shows 7 modified + untracked sprint59/ |
| C02 | "Final git state: clean" | `lanes/lane-I/git-status.txt` | CONTRADICTED | Shows 7 modified workspace files and untracked sprint59/ |
| C03 | "42/42 destination Program.cs content verified" | `destination/content-audit.json` | CONTRADICTED | content_match_rate=39/42; 1 PARTIAL + 3 PRESENT_NO_AUTHORITY |
| C04 | "42/42 README.md fetched and audited" | `destination/readme-vs-authority.json` | CONTRADICTED | Files fetched and size-checked, not content-audited against I/O authority |
| C05 | "6/6 root READMEs audited" | `destination/root-readme-audit.json` | PARTIALLY_VERIFIED | Audited for presence/size/family-name; Words+Diagram version gaps unclassified |
| C06 | "README gate documented; auto-gate wiring deferred Sprint 60" | `lanes/lane-G/readme-gate-proof.md` | INVALID_CLOSURE | Gate deferred cannot be counted as implemented |
| C07 | "Branch auto-delete at cf0919a; 7 dry-run tests pass" | `lanes/lane-G/branch-auto-delete-source-proof.md` | VERIFIED | Source diff, 7 tests, merge-flow integration all documented |
| C08 | "42/42 input formats resolved, zero unknown" | `io-authority/input-format-authority-matrix.json` | VERIFIED | 42/42 entries from format_contract, confidence high |
| C09 | "Authority source: format_contract" | `io-authority/input-format-authority-matrix.json` | PARTIALLY_VERIFIED | format_contract authority is valid; not full package-level reflection |
| C10 | "42/42 regeneration (35 clean + 7 repaired)" | `regeneration/full-regeneration-ledger-repaired.json` | VERIFIED | Per-example records present; counts add up |
| C11 | "42 per-example records with 30+ fields" | `regeneration/per-example/` | VERIFIED | 42 JSON files with full field sets |
| C12 | "2826 passed, 0 failed, 3 skipped" | `lanes/lane-I/test-run.log` | VERIFIED | Test log present and matches |
| C13 | "Evidence bundle 81 files" | `bundle-manifest.json` | VERIFIED | 79 evidence files covered + 2 (bundle-manifest + final-verdict) = 81 |
| C14 | "26/26 EC categories PRESENT" | `evidence-contract.json` | CONTRADICTED | EC23+EC24 set PRESENT but underlying evidence (git-status.txt) shows dirty state |
| C15 | "12 bundle validation rules passed" | `bundle-manifest.json` | INVALID_CLOSURE | validation_rules_passed is a hardcoded list; no validator was actually run |
| C16 | "Source diff present (370 lines)" | `source/source-diff.patch` | VERIFIED | Patch file present, 370 lines |
| C17 | "Source hashes in bundle" | `source/source-hashes.json` | VERIFIED | SHA256 per file post-commit present |
| C18 | "All Sprint 58 defects SD01–SD08 resolved" | `sprint-state.json`, per-defect evidence | PARTIALLY_VERIFIED | SD05+SD08 verified; SD07 only presence-checked; SD06 is 39/42 not 42/42; SD01 git proof missing |
| C19 | "PRESENT_NO_AUTHORITY: 3 cases — name mapping gap" | `destination/content-audit.json` | CONTRADICTED | Claimed as known gap; verdict still says DESTINATION_CONTENT_VERIFIED |
| C20 | "PARTIAL: 1 case — minor mismatch" | `destination/content-audit.json` | CONTRADICTED | pdf-image-extractor has output_format_in_programcs=false — not minor |
| C21 | "Destination correction plan" | `destination/correction-plan.md` | INVALID_CLOSURE | Plan exists but no actual correction was executed |
| C22 | "TODO: Phase 0 complete" | `todo.md` | VERIFIED | Phase 0 items all checked |
| C23 | "TODO: phases 1-8 complete" | `todo.md` | CONTRADICTED | Phases 1-8 have zero checked items despite work being done |
| C24 | "SD02 resolved: 35 clean + 7 repaired = 42" | `regeneration/full-regeneration-ledger-repaired.json` | VERIFIED | Counts verified against per-example records |
| C25 | "SD04 resolved: zero unknown input formats" | `io-authority/input-format-authority-matrix.json` | VERIFIED | 0 unknown confirmed |
| C26 | "Sprint 59 verdict IO_AUTHORITY_COMPLETE_DESTINATION_CONTENT_VERIFIED" | all evidence | INVALID_CLOSURE | 5 of 26 claims CONTRADICTED; 2 INVALID_CLOSURE; verdict overclaims |

---

## Summary

| Classification | Count |
|----------------|-------|
| VERIFIED | 11 |
| PARTIALLY_VERIFIED | 3 |
| CONTRADICTED | 7 |
| INVALID_CLOSURE | 5 |
| **Total** | **26** |

**Acceptance verdict for Sprint 59:** `EVIDENCE_REPAIR_REQUIRED_NOT_CLOSED`

7 CONTRADICTED + 5 INVALID_CLOSURE = 12 claims that do not support the Sprint 59 closure verdict.
