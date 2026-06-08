# Family Manual Analysis: barcode

## Date: 2026-06-04
## Evidence: GitHub repo aspose-barcode/Aspose.BarCode-for-.NET

---

## 1. LowCode Namespace?
No. Aspose.BarCode does not have a LowCode namespace.

## 2. Plugins Namespace?
No. Aspose.BarCode does not have a dedicated Plugins namespace.

## 3. Regular Product APIs?
Yes. The standard workflow uses `Aspose.BarCode.Generation` and `Aspose.BarCode.BarCodeRecognition`.

## 4. Dedicated Plugin-Like Classes?
Yes:
- `BarcodeGenerator` — generates barcodes (write path)
- `BarCodeReader` — reads/recognizes barcodes (read path)

## 5. Static Converter Classes?
No.

## 6. Load/Save with Format Options?
Yes. `BarcodeGenerator.Save(path, BarCodeImageFormat)` for generation.
`BarCodeReader.ReadBarCodes()` returns recognized results.

## 7. Document Object Model Workflow?
Partial. BarcodeGenerator has a `Parameters` object for configuration.

## 8. Recognition/Extraction APIs?
Yes. BarCodeReader performs recognition. RecognitionResult objects hold results.

## 9. Rendering/Export APIs?
Yes. BarcodeGenerator renders to image formats (PNG, JPEG, SVG, EMF, BMP, GIF, TIFF).

## 10. Fixtures Needed?
- Generation: No input fixture needed (generates from code text + EncodeType)
- Recognition: Input image with barcode required

## 11. License-Sensitive?
Trial watermark on generated barcodes. Full API needs license.

## 12. Official Snippets?
- `StoreBarcodeOutputAsFile.cs` — BarcodeGenerator(EncodeTypes.Code128, "12345678") → gen.Save()
- `ReadSimpleExample.cs` — BarCodeReader(imagePath, DecodeType) → reader.ReadBarCodes()

## 13. Classes/Methods in Official Snippets?
- `BarcodeGenerator(EncodeTypes.*, codeText)`
- `gen.Save(path, BarCodeImageFormat.Png)`
- `BarCodeReader(imagePath, DecodeType.*)`
- `reader.ReadBarCodes()` → `BarCodeResult[]`

## 14. Plugins Sharing API Pattern?
- generate-barcode, generate-qr-code: Same BarcodeGenerator pattern, different EncodeTypes
- recognize-barcode, read-barcode, scan-barcode: Same BarCodeReader pattern

## 15. Plugins Needing Unique Mapping?
- generate-qr-code: EncodeTypes.QR or EncodeTypes.MaxiCode

## 16. Plugins with No Code?
None — all 5 have official GitHub examples.

## 17. Can Be Transformed Next Sprint?
- generate-barcode: YES (no fixture, code confirmed)
- generate-qr-code: YES (no fixture, same pattern)
- recognize-barcode: YES (needs input barcode image fixture)
- read-barcode: YES (same as recognize)
- scan-barcode: YES (same pattern)

## 18. Blockers?
Trial watermark on output. Documenting as ENVIRONMENT_DEPENDENT.

## 19. Registry Strategy?
All 5 plugins: READY_FOR_TRANSFORMATION after symbol confirmation.
Generation plugins: No input fixture. Recognition plugins: Need image fixture.

## 20. First Transformation Candidates?
1. generate-barcode (highest priority — no fixture needed)
2. generate-qr-code (same pattern, different EncodeType)
3. recognize-barcode (needs barcode image fixture)

## Implementation Model
`STATIC_CONVERTER_CLASS` — BarcodeGenerator is a direct instantiation with Save output.
Recognition plugins use `RECOGNITION_EXTRACTION_API`.
