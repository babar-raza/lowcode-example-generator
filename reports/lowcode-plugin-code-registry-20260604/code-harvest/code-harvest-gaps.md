# Code Harvest Gaps

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Harvest Summary

- Total plugins: 65
- Code fetched: 53 (81%)
- No match: 12 (19%)

---

## No-Match Plugins

| Family | Plugin | Reason | Blocker |
|--------|--------|--------|---------|
| barcode | read-barcode | Matched recognition base class only | SOURCE_FETCH_BLOCKED |
| cad | convert-dwg-to-jpg | No specific Dwg-to-Jpg file found | SOURCE_FETCH_BLOCKED |
| finance | parse-xbrl | No parse-specific files in repo | SOURCE_FETCH_BLOCKED |
| html | merge-html | No merge-specific file found | SOURCE_FETCH_BLOCKED |
| html | convert-html-to-markdown | No markdown conversion file found | SOURCE_FETCH_BLOCKED |
| imaging | - | All 8 matched | NONE |
| omr | recognize-omr | OMR repo has different file naming | SOURCE_FETCH_BLOCKED |
| omr | generate-omr-template | OMR repo has different file naming | SOURCE_FETCH_BLOCKED |
| ocr | extract-text | No extract-text specific file | SOURCE_FETCH_BLOCKED |
| svg | convert-svg-to-png | SVG repo has very few files | SOURCE_FETCH_BLOCKED |
| svg | convert-svg-to-jpg | SVG repo has very few files | SOURCE_FETCH_BLOCKED |
| svg | merge-svg | SVG repo has very few files | SOURCE_FETCH_BLOCKED |
| zip | extract-files | No extract-specific file matched | SOURCE_FETCH_BLOCKED |

---

## Code Quality Caveats

Some fetched files are not ideal matches:
1. **gis/convert-gis-data** -> `App.xaml.cs` — Wrong file (XAML startup); manual analysis required
2. **font/convert-font** -> `RunExamples.cs` — Program entry point; manual analysis required
3. **barcode/scan-barcode** -> same file as recognize-barcode (AustraliaPost); deduplication needed
4. **threed/compress-3d-scene** -> same file as convert-3d-model; separate example needed
5. **tasks/convert-mpp-to-pdf** -> `ExPdfDigitalSignatureDetails.cs` — specific PDF signing, not general save

These caveats are documented in the registry entries as NEEDS_MANUAL_MAPPING until better matches are confirmed.

---

## Mitigation

For 12 no-match plugins and 5 caveated matches, manual family analysis (Lane D) will:
1. Determine the correct API pattern from docs/reflection
2. Assign NEEDS_MANUAL_MAPPING status
3. Document what code would be needed
