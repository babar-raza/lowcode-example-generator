# Product Universe Reconciliation

**Run ID:** sysqual-20260528-001
**Sprint:** System Qualification Sprint — 26-Product Pilot Matrix
**Reconciliation Date:** 2026-05-28
**Reconciliation Status:** RECONCILED — UNIVERSE IS 25 PRODUCTS

---

## Expected vs Actual

| Item | Value |
|---|---|
| Sprint-specified expected count | 26 |
| Current repo authority count | **25** |
| Discrepancy | **1** |
| Reconciliation verdict | **EVIDENCED_UNIVERSE_IS_25** |

---

## Investigation

### What was searched

1. `pipeline/configs/families/*.yml` — primary authority (25 files, 1 template excluded)
2. `workspace/verification/latest/*-source-of-truth-proof.json` — 20 reflection-based proof files
3. `workspace/verification/latest/*-reflection-blocker.json` — 5 additional blocker proof files
4. `workspace/verification/latest/confirmed-no-lowcode-family-registry.json` — registry of 16 no-LowCode families
5. `pipeline/configs/denominators/` — 6 denominator files (one per active LowCode family)
6. `scripts/build_no_lowcode_registry.py` — hardcoded list of 13+2=15 no-LowCode families + OMR = 16 total
7. Historical workspace proofs and audit files

### Product count breakdown

| Category | Count | Products |
|---|---|---|
| LOWCODE_CONFIRMED (active) | 6 | cells, diagram, email, pdf, slides, words |
| NO_LOWCODE_CONFIRMED (disabled) | 16 | barcode, cad, drawing, finance, font, gis, html, imaging, note, omr, page, svg, tasks, tex, threed, zip |
| DISCOVERY_BLOCKED_EXTERNAL_PACKAGE | 2 | ocr, psd |
| DISCOVERY_BLOCKED_PACKAGE_NOT_FOUND | 1 | epub |
| **Total** | **25** | All 25 products evidenced in family configs |

### Why the sprint specified 26

The sprint prompt was authored with "26" as an expected count. After exhaustive search of all repo/config/package sources:
- No 26th Aspose .NET product was found in any family config, NuGet proof file, registry, or historical evidence
- The 25 products account for all investigated Aspose .NET products present in the pipeline repo
- The OMR family was confirmed no-LowCode via reflection (not in the original 13-family hardcoded list but added to registry; OMR has its own source-of-truth proof)
- The `epub` family is a documented discovery_blocked entry (NuGet package not found)
- No additional Aspose product was found that should be a 26th candidate

### Reconciliation Decision

**The evidenced universe is 25 products, not 26.**

The qualification run proceeds with all 25 products. No product is excluded without evidence. The "26" figure in the sprint prompt is unreconcilable against current repo authority and is superseded by this reconciliation.

---

## Product List (25)

| # | Product Key | Display Name | LowCode Status | E2E Requirement |
|---|---|---|---|---|
| 1 | barcode | Aspose.BarCode for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 2 | cad | Aspose.CAD for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 3 | cells | Aspose.Cells for .NET | LOWCODE_CONFIRMED | REQUIRED |
| 4 | diagram | Aspose.Diagram for .NET | LOWCODE_CONFIRMED | REQUIRED |
| 5 | drawing | Aspose.Drawing for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 6 | email | Aspose.Email for .NET | LOWCODE_CONFIRMED | REQUIRED |
| 7 | epub | Aspose.Epub for .NET | DISCOVERY_BLOCKED_EXTERNAL_PACKAGE | BLOCKED_PACKAGE_NOT_FOUND |
| 8 | finance | Aspose.Finance for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 9 | font | Aspose.Font for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 10 | gis | Aspose.GIS for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 11 | html | Aspose.HTML for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 12 | imaging | Aspose.Imaging for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 13 | note | Aspose.Note for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 14 | ocr | Aspose.OCR for .NET | DISCOVERY_BLOCKED_EXTERNAL_PACKAGE | BLOCKED_PENDING_PACKAGE_HEALING |
| 15 | omr | Aspose.OMR for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 16 | page | Aspose.Page for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 17 | pdf | Aspose.PDF for .NET | LOWCODE_CONFIRMED | REQUIRED |
| 18 | psd | Aspose.PSD for .NET | DISCOVERY_BLOCKED_EXTERNAL_PACKAGE | BLOCKED_PENDING_PACKAGE_HEALING |
| 19 | slides | Aspose.Slides for .NET | LOWCODE_CONFIRMED | REQUIRED |
| 20 | svg | Aspose.SVG for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 21 | tasks | Aspose.Tasks for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 22 | tex | Aspose.TeX for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 23 | threed | Aspose.3D for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |
| 24 | words | Aspose.Words for .NET | LOWCODE_CONFIRMED | REQUIRED |
| 25 | zip | Aspose.ZIP for .NET | NO_LOWCODE_CONFIRMED | NOT_REQUIRED |

---

## Sign-off

Reconciliation performed by: Supervisor Agent
Date: 2026-05-28
Evidence: `reports/system-qualification/product-universe/source-authority-map.json`
Final count: **25** (proceeding with qualification of all 25 products)
