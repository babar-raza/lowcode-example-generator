# PDF PR/Package Map — Sprint 46

## Canonical Mapping: GitHub PR to Local Package

| GitHub PR | Local Package Dir | Branch | Examples | Count |
|-----------|------------------|--------|----------|-------|
| #5 | pdf-controlled-pilot/ (unnumbered) | .../20260518-150226 | doc-converter, html, xls-converter | 3 |
| #6 | pdf-controlled-pilot-pr5/ | .../20260518-150254 | jpeg, png, tiff | 3 |
| #7 | pdf-controlled-pilot-pr6/ | .../20260518-150331 | image-extractor, table-generator, toc-generator | 3 |
| #8 | pdf-controlled-pilot-pr7/ | .../20260518-150408 | form-flattener, security | 2 |
| #9 | pdf-controlled-pilot-pr8/ | .../20260518-150429 | form-editor, form-exporter | 2 |
| #10 | pdf-controlled-pilot-pr9/ | .../20260518-150454 | signature | 1 |

**Total pending: 14 examples across 6 PRs**

## Directory Naming Offset
Local directory names are offset by 1 from GitHub PR numbers:
- `pdf-controlled-pilot/` (unnumbered) corresponds to GitHub PR#5
- `pdf-controlled-pilot-pr5/` corresponds to GitHub PR#6
- `pdf-controlled-pilot-pr9/` corresponds to GitHub PR#10

## Already Published (5 examples on target main)
- merger (wave1)
- splitter (wave1)
- optimizer (wave2)
- pdfa-converter
- text-extractor

## Verification
- All 14 pending examples mapped exactly once: PASS
- No published examples in recovery packages: PASS
- pdf-splitter excluded (already MERGED): PASS
- All 6 PRs are OPEN and CONFLICTING on README.md
- All 6 local packages exist with correct content
