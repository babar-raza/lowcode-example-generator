# PDF Root README Fix Proof — Sprint 68

Date: 2026-05-22
Sprint: sprint68
Defect closed: S67-D1

## Problem

Sprint 67 pdf-root-readme.md had only 3 rows in the examples table:
- doc-converter
- html
- xls-converter

The remaining 16 PDF example types were absent.

## Root Cause

Sprint 67's Phase 2 (root README cardinality repair) added cardinality annotations to existing
rows but did not expand the table to cover all 19 types. The cardinality-fix-proof.md
acknowledged this as a known issue ("PDF table 3/19 rows") but no EV rule was present
to detect it.

## Fix Applied

New `reports/sprint68/root-readme/per-family/pdf-root-readme.md` contains all 19 rows:

| Row | Example Dir | Input | Output | Operation |
|-----|------------|-------|--------|-----------|
| 1 | doc-converter | pdf | docx | converter |
| 2 | xls-converter | pdf | xlsx | converter |
| 3 | html | html | pdf | converter |
| 4 | jpeg | pdf | jpg (×N) | converter |
| 5 | png | pdf | png (×N) | converter |
| 6 | tiff | pdf | tiff | converter |
| 7 | text-extractor | pdf | string | extractor |
| 8 | merger | pdf (×N) | pdf | merger |
| 9 | splitter | pdf | pdf (×N) | splitter |
| 10 | optimizer | pdf | pdf | transform |
| 11 | pdfa-converter | pdf | pdf | transform |
| 12 | toc-generator | pdf | pdf | processor |
| 13 | table-generator | pdf | pdf | processor |
| 14 | image-extractor | pdf | png (×N) | extractor |
| 15 | security | pdf | pdf | transform |
| 16 | form-flattener | pdf | pdf | transform |
| 17 | form-editor | pdf | pdf | transform |
| 18 | form-exporter | pdf | json | exporter |
| 19 | signature | pdf | pdf | transform |

Row data source: `root-readme/pdf-readme-row-data.json`

## Verification

Row count: 19 (confirmed by counting `| ` delimited rows in ## Included Examples table)
Merger cardinality: Row 8 shows `pdf (×N)` input — N-to-1 merger
Splitter cardinality: Row 9 shows `pdf (×N)` output — 1-to-N splitter
TextExtractor output: Row 7 shows `string` — no fake file output

## EV Rule Added

New EV rule 53 (`pdf_root_readme_complete`) validates that the PDF root README contains
>=19 rows in the examples table. This closes the EV gap that allowed S67-D1 to pass validation.

## Other Family READMEs

The 5 non-PDF family root READMEs are carried forward unchanged from sprint67:
- cells-root-readme.md — 9/9 rows, cardinality markers present
- words-root-readme.md — 8/8 rows, cardinality markers present
- diagram-root-readme.md — 2/2 rows, present
- email-root-readme.md — 1/1 rows, present
- slides-root-readme.md — 3/3 rows, present
