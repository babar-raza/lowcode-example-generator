# Family Manual Analysis: psd

## Date: 2026-06-04
## Evidence: GitHub repo aspose-psd/Aspose.PSD-for-.NET, code: AIToPDF.cs, CroppingPSDWhenConvertingToPNG.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. Aspose.PSD.Image static loader (similar to Imaging).
## 4. Dedicated Plugin-Like Classes?
Yes:
- `Aspose.PSD.Image` (static .Load()) — universal entry point
- `PsdImage` — PhotoShop document image
- `AiImage` — Adobe Illustrator image
- `PdfOptions`, `PngOptions`, `JpegOptions` — output format options

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Yes. `Image.Load(psdPath)` + `image.Save(outPath, options)`.
## 7. Document Object Model Workflow? Yes. PsdImage has Layers, Resources hierarchy.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. Rasterizes PSD/AI to PDF, PNG, JPEG etc.

## 10. Fixtures Needed?
Yes. All plugins need input PSD or AI files.

## 11. License-Sensitive?
Trial watermark. Full API needs license.

## 12. Official Snippets?
- `AIToPDF.cs` — AiImage.Load() + PdfOptions + Save()
- `CroppingPSDWhenConvertingToPNG.cs` — PsdImage.Load() + Crop + PngOptions + Save()
- `AddThumbnailToEXIFSegment.cs` — JPEG EXIF manipulation

## 13. Classes/Methods?
- `using (AiImage image = (AiImage)Image.Load(sourceFile))`
- `image.Save(outputPath, new PdfOptions())`
- `using (PsdImage psdImage = (PsdImage)Image.Load(psdPath))`
- `psdImage.Crop(new Rectangle(x, y, w, h))`
- `psdImage.Save(outputPath, new PngOptions())`

## 14. Plugins Sharing API Pattern?
convert-psd-to-pdf, convert-psd-to-png, convert-psd-to-jpg: Same Image.Load/Save pattern.
edit-psd-layers: Unique — accesses PsdImage.Layers for manipulation.

## 15. Plugins Needing Unique Mapping?
edit-psd-layers: Layer manipulation (PsdImage.Layers array, TextLayer, ShapeLayer)

## 16. Plugins with No Code?
None — all 4 have matches.

## 17. Can Be Transformed Next Sprint?
- convert-psd-to-pdf: YES (needs PSD fixture)
- convert-psd-to-png: YES
- convert-psd-to-jpg: YES
- edit-psd-layers: NEEDS_MANUAL_MAPPING (layer-specific)

## 18. Blockers?
PSD input fixtures needed. Reflection blocked in prior sprint (Aspose.JavaAttributes missing).

## 19. Registry Strategy?
3 conversion plugins READY_FOR_TRANSFORMATION with fixtures; 1 NEEDS_MANUAL_MAPPING.

## 20. First Transformation Candidates?
1. convert-psd-to-png
2. convert-psd-to-pdf

## Implementation Model
`LOAD_SAVE_OPTIONS` — Image.Load() + Save(options).
edit-psd-layers: `DOCUMENT_OBJECT_MODEL_WORKFLOW`
