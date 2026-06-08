# Manual Family Analysis: ocr
## Sprint: lowcode-plugin-registry-expansion-20260604 | Date: 2026-06-04
## Evidence: https://products.aspose.net/ocr/ (6 canonical pages) + RecognizeImageFromStream.cs

### Implementation Model: RECOGNITION_EXTRACTION_API
All 6 OCR plugins share a single API pattern: `AsposeOcr` engine + `OcrInput` + `api.Recognize()`.

### API Pattern (shared across all 6 plugins)
```csharp
AsposeOcr api = new AsposeOcr();
OcrInput input = new OcrInput(InputType.SingleImage);
input.Add(imageStream);
List<RecognitionResult> result = api.Recognize(input);
Console.WriteLine(result[0].RecognitionText);
```

### All 6 Canonical Pages
- image-text-finder — search/find text in images
- invoice-to-text — extract text from invoices
- photo-to-text — extract text from photos
- scanned-image-to-text — extract text from scanned images
- scanned-pdf-to-text — extract text from scanned PDFs
- table-to-text — extract table text

### Fixture Requirements
All require an image fixture (PNG/JPEG). A minimal programmatically-generated test image works.
For scanned-pdf-to-text: requires a PDF with scanned content.

### Transformation Priority: MEDIUM
- All 6 share same OcrInput + api.Recognize() code pattern
- Fixture: need a test image file; can generate one with System.Drawing or use a bundled test image
- License: trial limits recognition; metered licensing recommended for CI
