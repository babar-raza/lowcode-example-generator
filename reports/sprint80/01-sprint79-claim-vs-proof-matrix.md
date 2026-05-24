# Sprint 79 Claim vs Proof Matrix

**Date:** 2026-05-24

| Claim | Proof | Classification |
|-------|-------|---------------|
| ECC blocking_failures=0, closure_valid=true | evidence-contract-computed.json (genuine two-pass) | VERIFIED |
| 3083 tests passing, 3 skipped | test run log, pytest output | VERIFIED |
| 142 EV validator tests pass | validator-test-results.txt | VERIFIED |
| EV 110 rules, ECC 32 categories | validator source + test counts | VERIFIED |
| 5 Sprint 78 defects repaired | self-repair-actions.json | VERIFIED |
| ZIP bundle produced | bundles/sprint79-evidence-bundle-manifest.json with SHA256 | VERIFIED (ZIP gitignored) |
| final-clean-proof.txt has real SHA | commit b479ad9 | PARTIALLY_VERIFIED — committed file has SHA, but ZIP contains older placeholder version |
| sprint79-final-validation-result.json canonical | File has canonical_overall_valid=true but ALSO overall_valid=false | CONTRADICTED — S79-B1 |
| sprint79-bundle-validation-result.json Phase A | File has overall_valid=false with diagnostic label | PARTIALLY_VERIFIED — correct intent but canonical_overall_valid=false is contradictory |
| Publication matrix 42 examples | families dict has wrong per-family counts | CONTRADICTED — S79-B2 |
| Remote README I/O audit | Only family-level status, not per-example | INSUFFICIENT — S79-B3 |
| Test log completeness | One-line summary only | INSUFFICIENT — S79-B4 |
| Live publication blocked | PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=NOT_SET | VERIFIED — correctly blocked |
| 42/42 examples in remote repos | Confirmed by gh api query | VERIFIED |
| Words version drift REMOTE_DRIFT | remote=26.4.0, handoff=26.5.0 | VERIFIED — CARRIED_FORWARD |
| FormImporter BLOCKED_EXTERNAL | NullRef bug in Aspose.PDF>26.5.0 | VERIFIED — CARRIED_FORWARD |
