# Family Blocker Ledger

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Blocked Families/Plugins

| Family | Plugin | Blocker Code | Reason |
|--------|--------|-------------|--------|
| omr | recognize-omr | BLOCKED_LICENSE | Trial restricts all OMR operations; template required |
| omr | generate-omr-template | BLOCKED_LICENSE | Trial restricts template generation |
| font | convert-font | ENVIRONMENT_DEPENDENT | Trial requires allowlisted fonts (Montserrat, Noto Sans JP, etc.) |
| font | render-text-with-font | ENVIRONMENT_DEPENDENT | Same trial font restriction |
| threed | compress-3d-scene | ENVIRONMENT_DEPENDENT | License watermark; fixture needed |
| threed | convert-3d-model | ENVIRONMENT_DEPENDENT | License watermark; 3D fixture needed |

---

## Needs Manual Mapping (code gap, not license blocker)

| Family | Plugin | Reason |
|--------|--------|--------|
| barcode | read-barcode | Fetched general base class, not read-specific |
| cad | convert-dwg-to-jpg | No specific file fetched; pattern clear from other CAD plugins |
| finance | parse-xbrl | No match; DOM navigation pattern needed |
| gis | convert-gis-data | Fetched wrong file (App.xaml.cs); VectorLayer.Convert pattern known |
| html | convert-html-to-markdown | No match; markdown API different from converter static |
| html | merge-html | No match; DOM combination approach needed |
| ocr | extract-text | No match; same pattern as recognize-text |
| omr | recognize-omr | No code AND blocked by license |
| omr | generate-omr-template | No code AND blocked by license |
| svg | convert-svg-to-png | No match; pattern derivable from convert-svg-to-pdf |
| svg | convert-svg-to-jpg | No match; same derivable pattern |
| svg | merge-svg | No match; different approach needed |
| tasks | read-project-data | No match; DOM navigation of Project.Tasks |
| zip | extract-files | No match; Archive(path).ExtractAll() pattern |

---

## Summary

| Code | Count | Resolution |
|------|-------|-----------|
| BLOCKED_LICENSE | 2 | External blocker; need licensed environment |
| ENVIRONMENT_DEPENDENT | 4 | Use trial-compatible setup or licensed env |
| NEEDS_MANUAL_MAPPING | 12 | Code patterns known; write example manually |
