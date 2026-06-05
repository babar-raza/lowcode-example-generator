# Sprint Summary — Wave 6

**Sprint:** lowcode-plugin-example-factory-wave6-20260605
**Date:** 2026-06-05
**Verdict:** SPRINT_COMPLETE

---

## Headline Results

| Metric | Value |
|--------|-------|
| Packages built this wave | 14 |
| Packages PASS | 14/14 (100%) |
| Registry advances | 14 |
| Cumulative TRANSFORMED | 44/72 (61%) |
| New fixture generators | 4 |
| AOC validator rules | 16 |
| Test suite | 3433 passed, 18 skipped (+44 vs Wave 5) |
| IV verdict | IV_PASS |

---

## Packages Built (Wave 6)

| Package | Output | Size |
|---------|--------|------|
| html/convert-html-to-image | output.jpg | 223,704 B |
| html/convert-html-to-word | output.docx | 4,466 B |
| note/convert-one-to-image | output.png | 6,334 B |
| note/convert-one-to-word | output.html | 920 B |
| ocr/image-text-finder | found-text.txt | 110 B |
| ocr/invoice-to-text | invoice-data.txt | 112 B |
| page/convert-eps-to-pdf | output.pdf | 7,002 B |
| psd/convert-psd-to-pdf | output.pdf | 2,215 B |
| psd/psd-image-converter | output.jpg | 7,180 B |
| svg/vectorizer | output.svg | 438 B |
| tasks/convert-mpp-to-excel | project.xlsx | 5,250 B |
| tasks/convert-mpp-to-html | 6x project_N.html | ~3.5 MB each |
| tasks/convert-mpp-to-image | 3x project_N.png | ~30 KB each |
| tex/convert-latex-to-pdf | job.xps | 684,314 B |

---

## API Discoveries

1. **Aspose.PSD 24.12.0** requires `Aspose.Drawing 24.12.0` as explicit NuGet dep (nuspec bug lists 23.7.0)
2. **Aspose.Note 24.12.0** `SaveFormat` has no Word/Docx — supported: Bmp, Gif, Html, Jpeg, One, Pdf, Png, Tiff
3. **Aspose.Tasks** `SaveFileFormat.Png` (PascalCase, not `PNG`)
4. **Aspose.TeX 24.12.0** `PdfDevice` throws `XpsSaveOptions→PdfSaveOptions` cast — use `XpsDevice`
5. **EPS C# strings** must use `string[] + string.Join` to avoid `CS1010 Newline in constant`
6. **Aspose.SVG** `ImageVectorizerConfiguration.LineWidth` must be `1.0f` (float literal)

---

## New Capabilities

### Fixture Generators (Lane D)
- `generate_eps_fixture()` — EPS 200x200 with text
- `generate_psd_fixture()` — Binary PSD from spec (8BPS header)
- `generate_rich_geojson_fixture()` — 5-feature GeoJSON with mixed geometry
- `generate_latex_fixture()` — Minimal LaTeX document

### Anti-Overclaiming Validators (Lane F)
- 16 rules: AOC-01..AOC-16
- Covers: output integrity, provenance, log presence, registry consistency
- 23 unit tests all pass

---

## Registry State (Post-Wave 6)

| Status | Count |
|--------|-------|
| TRANSFORMED_TO_EXAMPLE_DRYRUN | 44 |
| READY_FOR_TRANSFORMATION | 4 |
| CODE_HARVESTED | 8 |
| NEEDS_MANUAL_MAPPING | 16 |
| TOTAL | 72 |

---

## Wave 7 Outlook

11 candidates identified across: imaging (4), barcode (2), zip (1), gis (2), drawing (1), finance (1).
Target: 55+ packages TRANSFORMED after Wave 7.
