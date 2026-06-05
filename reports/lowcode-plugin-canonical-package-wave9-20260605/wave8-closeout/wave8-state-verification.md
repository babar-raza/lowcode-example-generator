# Wave 8 State Verification
Sprint: lowcode-plugin-canonical-package-wave9-20260605 (verifying Wave 8)
Date: 2026-06-05

## Summary

Wave 8 (`lowcode-plugin-canonical-primary-wave8-20260605`) is committed at `42f4de6`.
Sprint verdict was `SPRINT_COMPLETE`. This document records the honest state.

## What Was Actually Completed

### Registry Migrations
- barcode/generate-barcode → 1d-barcode-writer (CANONICAL_PRIMARY_MIGRATED)
- barcode/recognize-barcode → 1d-barcode-reader
- barcode/generate-qr-code → 2d-barcode-writer
- barcode/scan-barcode → 2d-barcode-reader
- ocr/photo-to-text: READY_FOR_TRANSFORMATION → TRANSFORMED_TO_EXAMPLE_DRYRUN
- ocr/table-to-text: same
- psd/animation-maker, psd/photo-processor: same + identity_status fixed
- imaging/convert-image → image-converter (Wave 8)
- imaging/resize-image → image-resizer (Wave 8)
- html/convert-html-to-pdf → html-to-pdf-converter (Wave 8)
- note/convert-one-to-pdf → convert-onenote-to-pdf (Wave 8)

### Source Code
- `src/plugin_examples/plugin_code_registry/models.py`: legacy_aliases, display_plugin_name, migration_status, migrated_from fields added
- `src/plugin_examples/plugin_code_registry/loader.py`: lookup_by_alias(), canonical_primary_entries() added
- `src/plugin_examples/fixture_factory/canonical_primary_validators.py`: CPV-01..CPV-12 (new file)
- `tests/unit/test_canonical_primary_validators.py`: 25 tests (new file)

### Test Results
- pytest: 3471 passed, 18 skipped (full suite — log not captured in bundle)
- CPV tests: 25/25 PASS (log: wave8-closeout/cpv-test-log.txt)
- IV: 80/80 PASS

## Known Gaps (Repaired in Wave 9)

1. **lane-ledger.json lanes**: showed IN_PROGRESS/PENDING — REPAIRED (now COMPLETE)
2. **taskcards.json**: showed IN_PROGRESS/PENDING — REPAIRED (now COMPLETE)
3. **sprint-closeout.json**: evidence_bundle said PENDING — REPAIRED (now COMPLETE with note)
4. **Raw pytest log**: not in Wave 8 evidence bundle — Wave 9 captures affected test logs
5. **Evidence bundle ZIP**: narrow patterns excluded .cs/.csproj/.log files — Wave 9 uses wider patterns
6. **package-manifest.json**: missing from imaging/image-converter, imaging/image-resizer, html/html-to-pdf-converter — REPAIRED in Lane C
7. **display_plugin_name**: missing from many CANONICAL_IDENTITY_VERIFIED registry entries — REPAIRED in Lane B

## Wave 8 Package Reality

The 4 Wave 8 packages ARE real dryrun packages (not metadata-only):
- All contain: Program.cs, .csproj, restore.log, build.log, run.log, output-validation.json, output files
- They are copies from prior sprint packages migrated to canonical paths with updated source-provenance
- The csproj names still use legacy slugs (naming issue, not functional gap)
- The `package` field in output-validation used old slug for image-converter (fixed in Lane C)

## Verdict
WAVE8_PARTIAL_IMPORTED — Sprint complete and committed; 7 known gaps documented and addressed in Wave 9.
