# Family Manual Analysis: page

## Date: 2026-06-04
## Evidence: GitHub repo aspose-page/Aspose.Page-for-.NET, code: ClippingXPS.cs, CropEPS.cs, ClippingPS.cs
## Prior sprint: Aspose.Page.Plugins namespace CONFIRMED present (PsConverter)

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? YES — Aspose.Page.Plugins is CONFIRMED present (unique finding from reflection).
## 3. Regular Product APIs? Yes. XpsDocument, PsDocument, EpsDocument.
## 4. Dedicated Plugin-Like Classes?
YES — actual Plugins namespace:
- `Aspose.Page.Plugins.PsConverter` — converts PS/EPS/XPS to PDF
- Regular API: `XpsDocument`, `PsDocument`, `EpsDocument`

## 5. Static Converter Classes? No (PsConverter uses Process() method).
## 6. Load/Save with Format Options? Yes. XpsDocument.SaveAsPdf(outPath).
## 7. Document Object Model Workflow? Yes. XPS documents have page/element hierarchy.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. PDF export from XPS/PS/EPS.

## 10. Fixtures Needed?
Yes. All plugins need input XPS, PS, or EPS files.

## 11. License-Sensitive?
Trial limitations.

## 12. Official Snippets?
- `ClippingXPS.cs` — XpsDocument creation + manipulation
- `CropEPS.cs` — EPS document processing (5.4KB, complex)
- `ClippingPS.cs` — PS document processing

## 13. Classes/Methods?
Via Plugins namespace (preferred):
- `PsConverter.Process(inputStream, outputStream, mergeOptions)` — PS/EPS to PDF

Via regular API:
- `XpsDocument doc = new XpsDocument(inputPath)`
- `doc.SaveAsPdf(outputPath, pdfOptions)`

## 14. Plugins Sharing API Pattern?
convert-eps-to-pdf, convert-ps-to-pdf: PsConverter.Process() via Plugins namespace.
convert-xps-to-pdf: XpsDocument.SaveAsPdf() via regular API.

## 15. Plugins Needing Unique Mapping?
All 3 plugins have distinct source formats (XPS vs PS vs EPS).

## 16. Plugins with No Code?
All 3 have fetched GitHub examples. Plugins namespace code not directly fetched.

## 17. Can Be Transformed Next Sprint?
- convert-xps-to-pdf: YES
- convert-ps-to-pdf: YES
- convert-eps-to-pdf: YES

## 18. Blockers?
Input fixture files needed (XPS, PS, EPS). Plugins namespace is available.

## 19. Registry Strategy?
All 3 READY_FOR_TRANSFORMATION. Priority: convert-xps-to-pdf (simplest).

## 20. First Transformation Candidates?
1. convert-xps-to-pdf
2. convert-eps-to-pdf (via PsConverter)

## Implementation Model
`DEDICATED_PLUGIN_CLASS` for PS/EPS via Aspose.Page.Plugins.PsConverter.
`LOAD_SAVE_OPTIONS` for XPS via XpsDocument.SaveAsPdf.
