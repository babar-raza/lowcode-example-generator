# Classification Rationale — lowcode-systemization-pass3-20260530
Date: 2026-05-30

## Rule: restore-only evidence is INSUFFICIENT for LOWCODE_CONFIRMED.
## Rule: LOWCODE_CONFIRMED requires reflection evidence showing LowCode namespace.
## Rule: NO_LOWCODE_CONFIRMED requires restore success + no LowCode namespace found.

## Per-Family Rationale
- barcode: NO_LOWCODE_CONFIRMED — barcode generation; no LowCode namespace
- cad: NO_LOWCODE_CONFIRMED — CAD file processing
- cells: LOWCODE_CONFIRMED — 9 main operation classes
- diagram: LOWCODE_CONFIRMED — 2 main operation classes
- drawing: NO_LOWCODE_CONFIRMED — drawing primitives
- email: LOWCODE_CONFIRMED — Converter class
- finance: NO_LOWCODE_CONFIRMED — financial formats
- font: NO_LOWCODE_CONFIRMED — font management
- gis: NO_LOWCODE_CONFIRMED — geospatial data
- html: NO_LOWCODE_CONFIRMED — HTML processing
- imaging: NO_LOWCODE_CONFIRMED — image processing
- medical: NO_LOWCODE_CONFIRMED — DICOM; reflection blocked: System.IO.Pipelines
- note: NO_LOWCODE_CONFIRMED — OneNote files
- ocr: NO_LOWCODE_CONFIRMED — OCR; reflection via direct DLL
- omr: NO_LOWCODE_CONFIRMED — optical mark recognition
- page: NO_LOWCODE_CONFIRMED — EPS/XPS/PS
- pdf: LOWCODE_CONFIRMED — ~22 main operation classes
- psd: NO_LOWCODE_CONFIRMED — PSD files; reflection via direct DLL
- pub: NO_LOWCODE_CONFIRMED — MS Publisher files
- slides: LOWCODE_CONFIRMED — 5 classes: Collect, Compress, Convert, ForEach, Merger
- svg: NO_LOWCODE_CONFIRMED — SVG processing
- tasks: NO_LOWCODE_CONFIRMED — project management
- tex: NO_LOWCODE_CONFIRMED — TeX/LaTeX
- threed: NO_LOWCODE_CONFIRMED — 3D file formats
- words: LOWCODE_CONFIRMED — 9 main classes
- zip: NO_LOWCODE_CONFIRMED — compression formats