Sprint 87 — Next-Family Discovery Report
==========================================
Date: 2026-05-25
Author: Lane 2

## Discovery Method
Scanned `pipeline/configs/families/*.yml` for enabled status and LowCode namespace
confirmation. This is REAL discovery from repo configs, not a re-listing of current families.

## Current Active Families (6 families, 42 examples)

| Family | Examples | Status |
|--------|----------|--------|
| cells | 9 | ACTIVE — 9/9 remote, 0/9 README I/O |
| words | 8 | ACTIVE — version drift (26.4.0→26.5.0) |
| pdf | 19 | ACTIVE — FormImporter BLOCKED_EXTERNAL |
| diagram | 2 | ACTIVE — 2/2 remote |
| email | 1 | ACTIVE — 1/1 remote |
| slides | 3 | ACTIVE — 3/3 remote |

## Candidate Next Families (enabled=true, not yet published)

### OCR (Aspose.OCR)
- **Config**: `pipeline/configs/families/ocr.yml` — enabled=true
- **LowCode status**: UNKNOWN (reflection not completed successfully)
- **Next step**: Run discovery_sweep with OCR family to check for LowCode namespace
- **Risk**: Medium — OCR may not have LowCode APIs
- **Priority**: HIGH — already enabled in config

### PSD (Aspose.PSD)
- **Config**: `pipeline/configs/families/psd.yml` — enabled=true
- **LowCode status**: UNKNOWN (reflection not completed successfully)
- **Next step**: Run discovery_sweep with PSD family to check for LowCode namespace
- **Risk**: Medium — PSD may not have LowCode APIs
- **Priority**: HIGH — already enabled in config

## Investigation-Required Families (status unknown)

### HTML (Aspose.HTML)
- **Config**: `pipeline/configs/families/html.yml` — enabled=false
- **LowCode status**: UNKNOWN — not investigated
- **Next step**: Run reflection to check for LowCode namespace
- **Priority**: MEDIUM

### SVG (Aspose.SVG)
- **Config**: `pipeline/configs/families/svg.yml` — enabled=false
- **LowCode status**: UNKNOWN — not investigated
- **Next step**: Run reflection to check for LowCode namespace
- **Priority**: MEDIUM

### Epub
- **Config**: `pipeline/configs/families/epub.yml` — enabled=false
- **LowCode status**: No explicit CONFIRMED_NO_LOWCODE tag
- **Next step**: Verify LowCode namespace status
- **Priority**: LOW

## Confirmed No-LowCode Families (14 families — no action needed)
barcode, cad, drawing, finance, font, gis, imaging, note, omr, page, tasks, tex, threed, zip

All confirmed via all-family discovery run 2026-05-09. No LowCode namespace found.
OMR required Newtonsoft.Json extra_package for reflection to succeed.

## Summary
- **2 high-priority candidates**: OCR, PSD (enabled but reflection incomplete)
- **3 investigation candidates**: HTML, SVG, Epub (status unknown)
- **14 confirmed non-LowCode**: No further action
- **Denominator impact**: If OCR or PSD have LowCode APIs, total example count will increase beyond 42
