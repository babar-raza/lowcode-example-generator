# Family Manual Analysis: note

## Date: 2026-06-04
## Evidence: GitHub repo aspose-note/Aspose.Note-for-.NET, code: PdfConversion.cs, PasswordProtectedDoc.cs, ExtractImages.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. Document class with Save method.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `Document` — loads and represents OneNote documents (.one files)
- `PdfSaveOptions`, `DocSaveOptions`, `ImageSaveOptions` — format options
- `SaveFormat` enum — for format selection

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Yes. `document.Save(outputPath, saveOptions)`.
## 7. Document Object Model Workflow? Yes. Document has Pages/Outlines/Rich Text hierarchy.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. PDF, Word, image export.

## 10. Fixtures Needed?
Yes. All plugins need input .ONE (OneNote) files.

## 11. License-Sensitive?
Trial watermark on output. Full API needs license.

## 12. Official Snippets?
- `PdfConversion.cs` — `new Document(oneFile)` + `document.Save(pdfPath)`
- `PasswordProtectedDoc.cs` — Document with password + Save to Word
- `ExtractImages.cs` — Document.GetChildNodes<Image>() for image extraction

## 13. Classes/Methods?
- `var document = new Document(inputPath);`
- `document.Save(outputPath, new PdfSaveOptions());`
- `document.Save(outputPath, SaveFormat.Doc);`
- `document.GetChildNodes<Image>()` — extract images

## 14. Plugins Sharing API Pattern?
All 3 conversion plugins use Document.Load() + Save() pattern.

## 15. Plugins Needing Unique Mapping?
- convert-one-to-image: May use GetChildNodes or page-level rendering

## 16. Plugins with No Code?
None — all 3 matched.

## 17. Can Be Transformed Next Sprint?
All 3 YES. Need .ONE fixture file.

## 18. Blockers?
OneNote fixture file needed.

## 19. Registry Strategy?
All 3 READY_FOR_TRANSFORMATION.

## 20. First Transformation Candidates?
1. convert-one-to-pdf

## Implementation Model
`LOAD_SAVE_OPTIONS` — Document.Load() + Save(options).
