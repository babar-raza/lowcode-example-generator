# Family Manual Analysis: cad

## Date: 2026-06-04
## Evidence: GitHub repo aspose-cad/Aspose.CAD-for-.NET, code: ExportDGNToPdf.cs, ParticularDWGToImage.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. Aspose.CAD.Image static loader + format-specific options.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `Aspose.CAD.Image` (static .Load()) — universal entry point
- `CadImage`, `DgnImage`, `DxfImage`, `DwgImage` — specialized CAD image types
- `CadRasterizationOptions` — rasterization settings for CAD
- `PdfOptions`, `JpegOptions`, `BmpOptions` — output format options

## 5. Static Converter Classes? No (Image.Load is static loader, not converter).
## 6. Load/Save with Format Options? Yes. `Image.Load(cadPath)` + `image.Save(outputPath, pdfOptions)`.
## 7. Document Object Model Workflow? CAD files have entity hierarchy but export is direct.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. Rasterization + PDF/image export.

## 10. Fixtures Needed?
Yes. All plugins need input CAD files (DWG, DXF, DGN, etc.).
Prior probe used programmatically generated DXF binary content.

## 11. License-Sensitive?
Trial watermark. Prior probe confirmed working with synthetic DXF.

## 12. Official Snippets?
- `ExportDGNToPdf.cs` — DgnImage.Load() + CadRasterizationOptions + PdfOptions + Save()
- `ParticularDWGToImage.cs` — Image.Load(dwg) + CadRasterizationOptions + JpegOptions + Save()

## 13. Classes/Methods?
- `using (CadImage cadImage = (CadImage)Image.Load(inputPath))`
- `CadRasterizationOptions rasterOpts = new CadRasterizationOptions() { PageWidth=1600, PageHeight=1600 }`
- `PdfOptions pdfOptions = new PdfOptions { VectorRasterizationOptions = rasterOpts }`
- `cadImage.Save(outputPath, pdfOptions)`

## 14. Plugins Sharing API Pattern?
All 5 plugins use same: Image.Load(cadFile) + RasterizationOptions + FormatOptions + Save().

## 15. Plugins Needing Unique Mapping?
- convert-dwg-to-jpg: Specifically DWG input + JpegOptions

## 16. Plugins with No Code?
- convert-dwg-to-jpg: No direct match found.

## 17. Can Be Transformed Next Sprint?
- convert-cad-to-pdf: YES (confirmed by prior probe)
- convert-dwg-to-pdf: YES
- convert-dxf-to-pdf: YES
- convert-cad-to-image: YES
- convert-dwg-to-jpg: NEEDS_MANUAL_MAPPING (pattern same as image, just DWG input)

## 18. Blockers?
CAD file fixtures required. Prior probe generated synthetic DXF.

## 19. Registry Strategy?
4 plugins READY_FOR_TRANSFORMATION; 1 NEEDS_MANUAL_MAPPING.

## 20. First Transformation Candidates?
1. convert-cad-to-pdf (prior probe confirmed)
2. convert-dxf-to-pdf

## Implementation Model
`LOAD_SAVE_OPTIONS` with `RENDERING_API` for rasterization. Image.Load() → options → Save().
