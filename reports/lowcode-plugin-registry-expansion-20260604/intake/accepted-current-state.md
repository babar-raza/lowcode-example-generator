# Accepted Current State

## Sprint: lowcode-plugin-registry-expansion-20260604
## Date: 2026-06-04
## Preceding bundle: lowcode-plugin-code-registry-reconciliation-20260604.zip

---

## Confirmed Existing Registry

| Family | Plugins | Status | canonical_url |
|--------|---------|--------|---------------|
| barcode | 5 | 4×READY_FOR_TRANSFORMATION, 1×NEEDS_MANUAL_MAPPING | 4 entries |
| imaging | 8 | 8×READY_FOR_TRANSFORMATION | 8 entries |
| zip | 4 | 3×READY_FOR_TRANSFORMATION, 1×NEEDS_MANUAL_MAPPING | 4 entries |
| cad | 5 | 4×CODE_HARVESTED, 1×NEEDS_MANUAL_MAPPING | 0 |
| drawing | 2 | 2×CODE_HARVESTED | 0 |
| finance | 2 | 1×CODE_HARVESTED, 1×NEEDS_MANUAL_MAPPING | 0 |
| font | 2 | 1×CODE_HARVESTED, 1×NEEDS_MANUAL_MAPPING | 0 |
| gis | 2 | 1×CODE_HARVESTED, 1×NEEDS_MANUAL_MAPPING | 0 |
| html | 6 | 4×CODE_HARVESTED, 2×NEEDS_MANUAL_MAPPING | 0 |
| note | 3 | 3×CODE_HARVESTED | 0 |
| ocr | 3 | 2×CODE_HARVESTED, 1×NEEDS_MANUAL_MAPPING | 0 |
| omr | 2 | 2×NEEDS_MANUAL_MAPPING | 0 |
| page | 3 | 3×CODE_HARVESTED | 0 |
| psd | 4 | 4×CODE_HARVESTED | 0 |
| svg | 4 | 1×CODE_HARVESTED, 3×NEEDS_MANUAL_MAPPING | 0 |
| tasks | 5 | 3×CODE_HARVESTED, 2×NEEDS_MANUAL_MAPPING | 0 |
| tex | 3 | 3×CODE_HARVESTED | 0 |
| threed | 2 | 2×NEEDS_MANUAL_MAPPING | 0 |

**Total: 65 plugins, 18 families**
**READY_FOR_TRANSFORMATION: 15 (barcode:4, imaging:8, zip:3)**

---

## Confirmed Dry-Run Packages (Previous Sprint)

1. `barcode-generate-barcode` — dotnet run PASS, PNG 5,344 bytes
2. `imaging-convert-image` — dotnet run PASS, JPEG 1,111 bytes
3. `zip-compress-files` — dotnet run PASS, ZIP 868 bytes

---

## Confirmed Reconciliation Outputs

- Old URL pattern `/family/net/slug` → New canonical `/family/slug/` (no `/net/`)
- `reports/lowcode-plugin-code-registry-reconciliation-20260604/reconciliation/old-to-canonical-url-map.json`

---

## 13 New Canonical Pages Needing Registry Entries

| # | Family | Canonical Slug | Canonical URL |
|---|--------|---------------|---------------|
| 1 | imaging | animation-maker | https://products.aspose.net/imaging/animation-maker/ |
| 2 | imaging | photo-album-maker | https://products.aspose.net/imaging/photo-album-maker/ |
| 3 | imaging | image-deskew | https://products.aspose.net/imaging/image-deskew/ |
| 4 | zip | rar-extractor | https://products.aspose.net/zip/rar-extractor/ |
| 5 | ocr | image-text-finder | https://products.aspose.net/ocr/image-text-finder/ |
| 6 | ocr | invoice-to-text | https://products.aspose.net/ocr/invoice-to-text/ |
| 7 | ocr | photo-to-text | https://products.aspose.net/ocr/photo-to-text/ |
| 8 | ocr | table-to-text | https://products.aspose.net/ocr/table-to-text/ |
| 9 | psd | animation-maker | https://products.aspose.net/psd/animation-maker/ |
| 10 | psd | photo-processor | https://products.aspose.net/psd/photo-processor/ |
| 11 | svg | svg-to-pdf-converter | https://products.aspose.net/svg/svg-to-pdf-converter/ |
| 12 | svg | vectorizer | https://products.aspose.net/svg/vectorizer/ |
| 13 | tex | latex-math-renderer | https://products.aspose.net/tex/latex-math-renderer/ |

---

## 7 Previously Blocked Families

| Family | Blocker | Action This Sprint |
|--------|---------|-------------------|
| omr | HTTP 403 | Retry + classify |
| gis | HTTP 403 | Retry + classify |
| note | HTTP 403 | Retry + classify |
| drawing | HTTP 403 | Retry + classify |
| font | HTTP 403 | Retry + classify |
| finance | HTTP 403 | Retry + classify |
| threed | HTTP 403 | Retry + classify |

---

## Direction Confirmation

- Authority order: products.aspose.net → page prose → source links → manual analysis → registry → reflection/validation → transformation
- No reflection-first entries
- No pattern-only READY_FOR_TRANSFORMATION entries
