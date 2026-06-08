# Family Next-Action Ledger

**Sprint:** non-lowcode-fallback-implementation-20260604  
**Generated:** 2026-06-04

## Families with Classified Next Action

| family | package_id | bootstrap_status | next_action | blocker_type | confidence |
|--------|-----------|-----------------|------------|-------------|-----------|
| barcode | Aspose.BarCode | PROBE_CONFIRMED | READY_FOR_EXAMPLE_GENERATION | — | 0.95 |
| imaging | Aspose.Imaging | PROBE_CONFIRMED | READY_FOR_EXAMPLE_GENERATION | — | 0.80 |
| zip | Aspose.ZIP | PROBE_CONFIRMED | READY_FOR_EXAMPLE_GENERATION | — | 0.90 |
| html | Aspose.HTML | BOOTSTRAPPED_NO_PROBE | RUN_DLLREFLECTOR | — | — |
| tasks | Aspose.Tasks | BOOTSTRAPPED_NO_PROBE | RUN_DLLREFLECTOR | — | — |
| cad | Aspose.CAD | BOOTSTRAPPED_NO_PROBE | RUN_DLLREFLECTOR | — | — |
| ocr | Aspose.OCR | BOOTSTRAPPED_NO_PROBE | RUN_DLLREFLECTOR | — | — |

## Next-Action Definitions

| action | description |
|--------|-------------|
| READY_FOR_EXAMPLE_GENERATION | probe confirmed; dry-run example package can be built |
| RUN_DLLREFLECTOR | DllReflector has not yet run; namespace and type status unknown |
| PROBE_REQUIRED | type/method candidate found; probe not yet run |
| NEEDS_MANUAL_MAPPING | heuristic returned no candidates; manual seed required |
| BLOCKED_EXTERNAL | external blocker (license, NuGet, reflection) — no system action possible |

## Bootstrap Status Definitions

| status | description |
|--------|-------------|
| PROBE_CONFIRMED | Full e2e probe completed; output validated |
| BOOTSTRAPPED_NO_PROBE | Package known, NuGet available, but DllReflector not yet run |
| PROBE_IN_PROGRESS | Probe running or pending verification |
| BLOCKED | External blocker prevents progress |

## Sprint Actions Summary

- 3 families advanced to PROBE_CONFIRMED: barcode, imaging, zip
- 4 families remain at BOOTSTRAPPED_NO_PROBE pending DllReflector runs
- No families blocked (0 BLOCKED entries)
- Refresh policy: quarterly (90 days from last_validated)
