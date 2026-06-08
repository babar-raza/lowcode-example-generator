# Internal QA Report

## Sprint: lowcode-plugin-code-registry-reconciliation-20260604
## Date: 2026-06-04

---

## QA Check Results

| Check | Description | Result |
|-------|-------------|--------|
| QA1 | TRAIN A: Root page crawled + family pages crawled | PASS — 11/18 families accessible; 7 blocked (403 external) |
| QA2 | TRAIN B: Canonical plugin pages fetched; source links extracted | PASS — 37 canonical plugins discovered; source on GitHub confirmed |
| QA3 | TRAIN C: Old-to-canonical URL map produced | PASS — reconciliation map written with HIGH confidence for core 3 families |
| QA4 | TRAIN C: Registry YAMLs updated with canonical_url + page_source_status | PASS — barcode, imaging, zip updated; 3-16 entries advanced to READY_FOR_TRANSFORMATION |
| QA5 | TRAIN D: ≥3 snippets built, run, output validated | PASS — 3/3 PASS (barcode, imaging, zip) |
| QA6 | TRAIN E: ≥3 transformation packages created (Program.cs + csproj + provenance) | PASS — 3 packages created |
| QA7 | TRAIN F: Canonical URL coverage validator written | PASS — coverage check JSON produced |
| QA8 | TRAIN F: Registry readiness validator written | PASS — readiness check JSON produced; 15/15 PASS |
| QA9 | Protected LowCode YAMLs unchanged (cells/words/pdf/slides/diagram/email) | PASS — 0 diff lines confirmed |
| QA10 | No PRs, no external repo mutations | PASS — confirmed; no gh CLI used |

---

## Remaining Classified Blockers

| Blocker | Code | Classification |
|---------|------|----------------|
| products.aspose.net 403 on 7 families | CRAWL_BLOCKED_403 | EXTERNAL — omr/gis/note/drawing/font/finance/threed |
| barcode/read-barcode canonical ambiguity | CANONICAL_SPLIT_AMBIGUOUS | DEFERRABLE — split in next sprint |
| 13 new canonical pages not yet in registry | NEW_CANONICAL_NOT_REGISTERED | DEFERRABLE — next sprint expansion |
| zip/extract-files no code hash | NEEDS_MANUAL_MAPPING | DEFERRABLE — fetch extraction example |

All remaining blockers are external or explicitly classified.

---

## Acceptance

INTERNAL_QA_PASS — 10/10 checks pass, 0 system defects, all external blockers classified.
