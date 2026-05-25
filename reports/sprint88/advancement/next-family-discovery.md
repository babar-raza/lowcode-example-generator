Sprint 88 — Next-Family Discovery
====================================
Date: 2026-05-25

## Discovery Method
Scanned `pipeline/configs/families/` for all YAML configs. Cross-referenced with NuGet API v3
to verify package availability and identify transitive dependency blockers.

## Enabled Families in Config (8 total)
- cells, diagram, email, pdf, slides, words (active, 42 examples)
- ocr, psd (enabled in config but LowCode reflection incomplete)

## Candidate Investigation

### OCR (Aspose.OCR 26.5.0)
- NuGet package exists: YES
- LowCode namespace: UNKNOWN (reflection blocked)
- Blocker: Aspose.AI.LLM transitive dependency not found on NuGet (HTTP 404)
- Classification: DISCOVERY_BLOCKED_MISSING_PACKAGE

### PSD (Aspose.PSD 26.5.0)
- NuGet package exists: YES
- LowCode namespace: UNKNOWN (reflection blocked)
- Blocker: Aspose.JavaAttributes transitive dependency not found on NuGet (HTTP 404)
- Classification: DISCOVERY_BLOCKED_MISSING_PACKAGE

### HTML (Aspose.HTML 26.4.0)
- NuGet package exists: YES
- LowCode namespace: UNKNOWN (reflection blocked)
- Blocker: DllReflector assembly resolution failure
- Classification: REFLECTION_BLOCKED_ASSEMBLY_RESOLUTION

### SVG (Aspose.SVG 26.4.0)
- NuGet package exists: YES
- LowCode namespace: UNKNOWN (reflection blocked)
- Blocker: DllReflector assembly resolution failure
- Classification: REFLECTION_BLOCKED_ASSEMBLY_RESOLUTION

## Confirmed No LowCode (14 families)
barcode, cad, drawing, finance, font, gis, imaging, note, omr, page, tasks, tex, threed, zip

## Confirmed No NuGet Package
epub
