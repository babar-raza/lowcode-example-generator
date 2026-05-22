# PDF Recovery Inventory Reconciliation — Sprint 46

## Result: PASS — All 14 pending examples mapped exactly once

## Sprint 45 Issues Resolved

### 1. Package Report Wrong Mapping
- **Issue:** Sprint 45 mapped `pr5` → DocConverter/Html/XlsConverter
- **Root cause:** The unnumbered `pdf-controlled-pilot/` directory (not `pr5`) contains doc-converter/html/xls-converter and maps to GitHub PR#5
- **Fix:** Canonical map now uses GitHub PR numbers as primary key

### 2. PR#10 Missing from Reports
- **Issue:** Sprint 45 JSON reports omitted PR#10/signature
- **Root cause:** Local dir `pdf-controlled-pilot-pr9/` maps to GitHub PR#10 (offset naming)
- **Fix:** All 6 PRs now represented in canonical map

### 3. Signature Location
- **Verified:** Signature is correctly in `pdf-controlled-pilot-pr9/` local dir, which maps to GitHub PR#10 on GitHub

## Verification Matrix
| GitHub PR | Examples (from `gh pr diff --name-only`) | Local Dir | Match |
|-----------|------------------------------------------|-----------|-------|
| #5 | doc-converter, html, xls-converter | pdf-controlled-pilot/ | PASS |
| #6 | jpeg, png, tiff | pdf-controlled-pilot-pr5/ | PASS |
| #7 | image-extractor, table-generator, toc-generator | pdf-controlled-pilot-pr6/ | PASS |
| #8 | form-flattener, security | pdf-controlled-pilot-pr7/ | PASS |
| #9 | form-editor, form-exporter | pdf-controlled-pilot-pr8/ | PASS |
| #10 | signature | pdf-controlled-pilot-pr9/ | PASS |
