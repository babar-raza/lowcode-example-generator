# Family Manual Analysis: ocr

## Date: 2026-06-04
## Evidence: GitHub repo aspose-ocr/Aspose.OCR-for-.NET, code: GetChoicesForRecognizedCharacters.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. AsposeOcr + OcrInput + Recognize workflow.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `AsposeOcr` — main OCR engine
- `OcrInput` — input container (supports SingleImage, MultipleImages, PDF etc.)
- `RecognitionResult` — results container

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? No. Recognition returns result objects.
## 7. Document Object Model Workflow? No.
## 8. Recognition/Extraction APIs? Yes. `api.Recognize(input, settings)` is primary.
## 9. Rendering/Export APIs? No (OCR outputs text/JSON/CSV).

## 10. Fixtures Needed?
Yes. All plugins need input image or PDF with text content.

## 11. License-Sensitive?
Trial limits on recognized characters. Full API needs license.

## 12. Official Snippets?
- `GetChoicesForRecognizedCharacters.cs` — AsposeOcr + OcrInput + Recognize

## 13. Classes/Methods?
- `AsposeOcr api = new AsposeOcr();`
- `OcrInput input = new OcrInput(InputType.SingleImage);`
- `input.Add("image.png");`
- `List<RecognitionResult> results = api.Recognize(input, new RecognitionSettings { DetectAreasMode = DetectAreasMode.PHOTO });`
- `results[0].RecognitionText` — extracted text

## 14. Plugins Sharing API Pattern?
All 3 plugins use AsposeOcr + OcrInput + Recognize pattern.

## 15. Plugins Needing Unique Mapping?
- recognize-text: Basic recognition with RecognitionSettings
- extract-text: Same but focused on clean text output
- scan-document: Multi-page document recognition

## 16. Plugins with No Code?
- extract-text: No direct match. Pattern derivable from recognize-text.

## 17. Can Be Transformed Next Sprint?
- recognize-text: YES (needs input image fixture)
- extract-text: NEEDS_MANUAL_MAPPING
- scan-document: YES (multi-page variant)

## 18. Blockers?
Trial limits on recognition. OCR engine may refuse unlicensed recognition.

## 19. Registry Strategy?
1 READY_FOR_TRANSFORMATION; 1 NEEDS_MANUAL_MAPPING; 1 READY with fixture planning.

## 20. First Transformation Candidates?
1. recognize-text

## Implementation Model
`RECOGNITION_EXTRACTION_API`
