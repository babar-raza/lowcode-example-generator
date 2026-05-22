# Sprint 65 Phase 0 — Sprint 64 Claim vs Proof Matrix

| # | Sprint 64 Claim | Evidence In Bundle | Classification |
|---|----------------|-------------------|----------------|
| 1 | EV/ECC aligned, 22/22 rules pass | phase1/sprint64-final-validation-result.json, evidence/evidence-contract-computed.json | VERIFIED |
| 2 | 44/44 computed evidence categories PRESENT | evidence/evidence-contract-computed.json: closure_valid=true | VERIFIED |
| 3 | final-clean-proof.txt captured after commit | git/final-clean-proof.txt: non-empty, "nothing to commit" | VERIFIED |
| 4 | 42/42 clean package artifacts (0 obj/bin) | destination-packages/package-cleanliness-audit.md, package-artifact-index.json | VERIFIED |
| 5 | 42/42 README I/O sections in dry-run packages | phase5/example-readme-io-audit-after-application.json | PARTIALLY_VERIFIED — section presence confirmed, destination placement not proven |
| 6 | Root README audit reflects corrected state | phase5/root-readme-audit-after-application.json | CONTRADICTED — PDF shows 26.4.0 post version-policy at 26.5.0; no root README artifacts |
| 7 | Destination content audit 42/42 | destination/content-audit-deep.json | CONTRADICTED — dry_run_present=37 in JSON, 40 in summary; missing package_version, output_kind, readme_status, root_readme_status |
| 8 | PDF version drift resolved | phase6/pdf-version-drift-resolution.md | PARTIALLY_VERIFIED — policy-classified only; no build/run at 26.5.0; stale root README audit |
| 9 | Special-case packaging (pdf-pdfa, pdf-text-extractor) | destination-packages/special-cases/ | PARTIALLY_VERIFIED — artifacts present, destination path/placement NOT proven |
| 10 | All 42 examples published | final-verdict.md, sprint-state.json | INVALID_CLOSURE — no remote proof in bundle; workspace proof exists but not committed to bundle |
| 11 | Live publication status | publication/publication-readiness-result.json: live_publication_attempted=false | CONTRADICTED — claim says "published" but result says not attempted |
| 12 | Branch deletion | publication/branch-delete-result.json: NOT_APPLICABLE | VERIFIED — no branches created, no deletion required |

## Summary

| Classification | Count |
|----------------|-------|
| VERIFIED | 5 |
| PARTIALLY_VERIFIED | 3 |
| CONTRADICTED | 3 |
| INVALID_CLOSURE | 1 |
| REPAIRED_IN_SPRINT65 | 0 (will be after repair) |

## Sprint 65 Repair Plan

Each CONTRADICTED/INVALID_CLOSURE item has a Sprint 65 phase:
- S64-D1 (publication proof) → Phase 6
- S64-D2 (audit contradiction) → Phase 2
- S64-D3 (missing audit fields) → Phase 2
- S64-D4 (root README artifacts) → Phase 1
- S64-D5 (stale root README PDF) → Phase 1 + Phase 4
- S64-D6 (special case placement) → Phase 3
- S64-D7 (weak EV/ECC rules) → Phase 5
- S64-D8 (PDF deferred) → Phase 4
