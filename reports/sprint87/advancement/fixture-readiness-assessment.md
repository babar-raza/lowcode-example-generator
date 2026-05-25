Sprint 87 — Fixture Readiness Assessment
==========================================
Date: 2026-05-25
Author: Lane 2

## Current Fixture State

### Existing Families (42 examples)
All fixture contracts are `api_verified` per `pipeline/format-authority/contracts/`:
- cells.json: 9 types verified
- words.json: 8 types verified
- pdf.json: 19 types verified
- diagram.json: 2 types verified
- email.json: 1 type verified
- slides.json: 3 types verified

### Denominator Configs
Denominators exist for all 6 active families in `pipeline/configs/denominators/`:
- cells.json, diagram.json, email.json, pdf.json, slides.json, words.json

### Fixture Registry
`src/plugin_examples/fixture_registry/registry.py` — stores provenance metadata
for fixtures sourced from Aspose example repos.

## Readiness for Next Families

### OCR Fixture Readiness
- **Format contract**: NOT YET CREATED (`pipeline/format-authority/contracts/ocr.json` absent)
- **Denominator**: NOT YET CREATED (`pipeline/configs/denominators/ocr.json` absent)
- **Prerequisite**: Must complete reflection/discovery sweep first to identify LowCode types
- **Status**: NOT_READY — blocked on discovery

### PSD Fixture Readiness
- **Format contract**: NOT YET CREATED (`pipeline/format-authority/contracts/psd.json` absent)
- **Denominator**: NOT YET CREATED (`pipeline/configs/denominators/psd.json` absent)
- **Prerequisite**: Must complete reflection/discovery sweep first to identify LowCode types
- **Status**: NOT_READY — blocked on discovery

## Fixture Integrity Checks
- Format authority store (`src/plugin_examples/format_authority/store.py`) is fail-closed
- `MissingFormatContractError` propagates for unknown types (Sprint 57 fix)
- `allow_legacy_format_inference=False` in production
- Stale-map guard tests in `tests/unit/test_format_authority_no_stale_maps.py`

## Summary
All current families have complete fixture readiness. Next families (OCR, PSD) require
discovery sweep completion before fixtures can be created.
