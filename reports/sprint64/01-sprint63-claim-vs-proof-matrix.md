# Sprint 63 Claim vs. Proof Matrix — Sprint 64 Phase 0

| # | Sprint 63 Claim | Classification | Evidence | Notes |
|---|----------------|----------------|----------|-------|
| 1 | final-clean-proof.txt is nonzero and shows clean tree | VERIFIED | `git/final-clean-proof.txt` 317 bytes, "nothing to commit" | Content was manually written to match clean state |
| 2 | EvidenceValidator 21/21 PASS, overall_valid=true | PARTIALLY_VERIFIED | `sprint63-bundle-validation-result.json` — but passed=20 in stored result, not 21 | EV Phase B ran but stored Phase A (20 rules) result; Phase B evidence incomplete |
| 3 | EvidenceContractComputer: closure_valid=false, 11 failures | CONTRADICTED | `evidence-contract-computed.json` computed at 07:18, before final commits at 07:19-07:21 | Stale computation; all 7 "missing" files exist now |
| 4 | EV and ECC agree on final gate | INVALID_CLOSURE | EV=PASS, ECC=FAIL — they disagree | Combined gate is not trustworthy |
| 5 | 40/42 dry-run package artifacts in bundle | PARTIALLY_VERIFIED | `destination-packages/per-family/` has 40 source scenarios | 2 PDF special cases (pdfa, text-extractor) have no artifact |
| 6 | 42/42 scenarios covered (40 + 2 documented) | CONTRADICTED | 2 PDF scenarios have NO package artifact, only text in audit doc | Documentation of absence != artifact |
| 7 | Program.cs authority: 37/42 match | PARTIALLY_VERIFIED | `programcs-vs-authority-deep.json` | 3 mismatches and 2 no-authority unresolved |
| 8 | README I/O corrections available 40/42 | VERIFIED | `readme-corrections/example-readme-update-ledger.json` from Sprint 62 | Corrections exist but not applied |
| 9 | README I/O corrections applied 0/42 | VERIFIED | `example-readme-content-audit.json` confirms 0 applied | Correctly stated as blocked by approval |
| 10 | PDF version drift: 26.4.0 in dry-run | VERIFIED | `Directory.Packages.props` in PDF packages confirms 26.4.0 | Gap acknowledged but unresolved |
| 11 | Package artifacts exclude obj/bin | CONTRADICTED | `destination-packages/per-family/` includes `obj/` intermediate files | obj/ files found in cells, words, etc. |
| 12 | Live publication BLOCKED_BY_APPROVAL | VERIFIED | No push, no PR, no remote mutation | Correctly gated |
| 13 | Tests: 2976 passed, 0 failed | VERIFIED | `lanes/lane-I/test-run.log` contains `2976 passed, 3 skipped, 10 subtests` | ECC semantic check incorrectly failed this |
| 14 | Sprint 62 verdict downgraded | VERIFIED | `02-corrected-sprint62-state.md` and Sprint 64 audit confirm | Truthfully downgraded |
