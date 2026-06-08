# Evidence Reconstruction Repair Plan

## Repair Assignments

| Contradiction | Type | Repair Train |
|--------------|------|-------------|
| CONTR-EV-001 | SOURCE_EVIDENCE_MISSING | MEGA-TRAIN-B: git diff + file snapshots |
| CONTR-EV-002 | TEST_EVIDENCE_MISSING | MEGA-TRAIN-C: run each test file; capture logs |
| CONTR-EV-003 | COMMAND_LEDGER_DEFECT | MEGA-TRAIN-D: real command ledger with stdout/stderr |
| CONTR-EV-004 | BUNDLE_HYGIENE_DEFECT | MEGA-TRAIN-F: exclude bin/obj/DLL from bundle |
| CONTR-EV-005 | EVIDENCE_BUNDLE_DEFECT | MEGA-TRAIN-B + MEGA-TRAIN-H: full manifest |
| CONTR-EV-006 | EVIDENCE_BUNDLE_DEFECT | MEGA-TRAIN-E: replay pilots from actual modules |
| CONTR-EV-007 | SOURCE_EVIDENCE_MISSING | MEGA-TRAIN-B: git diff output |

## Execution Order

1. MEGA-TRAIN-A: Document (done)
2. MEGA-TRAIN-B: Source snapshots (git diff; file copies)
3. MEGA-TRAIN-C: Raw test logs (run all 10 test files individually)
4. MEGA-TRAIN-D: Command ledger (real timestamps + stdout)
5. MEGA-TRAIN-E: Pilot replay (run Python modules directly)
6. MEGA-TRAIN-F: Bundle hygiene policy
7. MEGA-TRAIN-G: Self-healing QA
8. MEGA-TRAIN-H: Final clean bundle (no binaries)
