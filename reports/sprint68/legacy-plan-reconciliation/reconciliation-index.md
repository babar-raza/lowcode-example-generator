# Legacy Plan Reconciliation Index — Sprint 67

Sprint: sprint67-final-pre-publication-repair-legacy-plan-reconciliation-readme-io-live-pr-readiness
Date: 2026-05-22

## Plans Reconciled

| Plan | Source Sprint | Items | Already Proven | Carried Forward | Superseded | Contradicted |
|------|-------------|-------|----------------|----------------|------------|-------------|
| Sprint 62 Format Capability Plan | Sprint 62 | 9 | 5 | 4 | 1 | 1 |
| Sprint 61 README Sync Architecture | Sprint 61 | 7 | 3 | 2 | 2 | 1 |
| **Total** | | **16** | **8** | **6** | **3** | **2** |

## Classification Summary

### Already Proven (closed, no Sprint 67 action)

1. S62-P1: Special-case I/O authority (9 cases) — closed Sprint 62
2. S62-P2: 42/42 README I/O correction text — closed Sprint 62
3. S62-P3: README gate hardening — closed Sprint 62
4. S62-P4: EV execution mandatory (SD61-05) — closed Sprint 62
5. S62-P5: Package authority api_verified — closed Sprint 62
6. S61-P1: readme_facts.py + readme_auditor.py active — closed Sprint 61
7. S61-P2: readme_audit_gate.py wired — closed Sprint 61
8. S61-P3: EvidenceValidator wired — closed Sprint 61

### Carried Forward (Sprint 67 must address)

1. CF-S62-2: Live README I/O publication — Phase 8
2. CF-S62-1: Words/Diagram version drift publication — Phase 3 + Phase 8
3. CF-S66-D1: Root README cardinality — Phase 2 (S66-D1)
4. CF-S66-D2: PDF version contradiction — Phase 3 (S66-D2)
5. CF-S66-D3: Sprint 64 path leakage — Phase 4 (S66-D3)
6. CF-S66-D4: No live PRs created — Phase 8 (S66-D4)

### Superseded (no action needed — newer artifacts replace)

1. SUP-S62-3: workspace/pr-dry-run/ packages → replaced by sprint66/handoff/per-family/
2. SUP-S61-4: readme-io-correction-plan.json → replaced by physical corrected packages
3. SUP-S61-5: Sprint 61 api_verified=False → replaced by Sprint 62 CONFIRMED_FROM_PROGRAMCS

### Contradicted (claims corrected by later evidence)

1. CON-S61-1: "38/42 IO_DOC_MATCH achievable" → corrected: 0/42 remote READMEs have I/O
2. CON-S62-1: "1 APPROVE_LIVE_PR away from publication" → corrected: root README cardinality defects must be repaired first

## Permanently Deferred Items (outside Sprint 67 scope)

| Item | Reason | Next Review |
|------|--------|-------------|
| FormImporter (pdf-form-importer) | Aspose.PDF library bug — blocked on 26.6.0+ | Monthly |
| OCR types | No Aspose LowCode OCR namespace confirmed | Monthly |
| PSD types | No Aspose LowCode PSD namespace confirmed | Monthly |
| api_verified=True via NuGet introspection | Requires external API tooling beyond current scope | Future sprint |

## Verdict

Sprint 62 Format Capability and Sprint 61 README Sync plans are now formally reconciled.
- 8 items proven closed
- 6 items carried forward with explicit Sprint 67 task cards (Phases 2, 3, 4, 8)
- 3 items superseded by newer artifacts
- 2 items contradicted with corrections on record
- 4 items permanently deferred (not Sprint 67 scope)

Legacy plan reconciliation: COMPLETE for Sprint 67.
