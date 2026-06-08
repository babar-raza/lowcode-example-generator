# Family Manual Analysis: html

## Date: 2026-06-04
## Evidence: GitHub repo aspose-html/Aspose.HTML-for-.NET, code: FlattenPDFExample.cs, HTMLtoDOCXExample.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. HTMLDocument + Converter static class.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `HTMLDocument` — loads HTML content (from file, URL, string)
- `Converter` — static conversion methods (ConvertHTML, ConvertMHTML, ConvertSVG, ConvertMarkdown)
- `PdfSaveOptions`, `DocSaveOptions`, `ImageSaveOptions`, `XpsSaveOptions` — format options

## 5. Static Converter Classes?
Yes. `Aspose.Html.Converters.Converter` has static `ConvertHTML(HTMLDocument, SaveOptions, string outputPath)`.

## 6. Load/Save with Format Options? Yes, via Converter static methods.
## 7. Document Object Model Workflow? Yes. HTMLDocument has DOM navigation but conversion is typically direct.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. Rendering to PDF, Word, XPS, Images.

## 10. Fixtures Needed?
Yes. All conversion plugins need input HTML/MHTML/Markdown files.

## 11. License-Sensitive?
Trial limitations. Full API needs license.

## 12. Official Snippets?
- `FlattenPDFExample.cs` — HTMLDocument + PdfSaveOptions pattern
- `HTMLtoDOCXExample.cs` — HTMLDocument + DocSaveOptions

## 13. Classes/Methods?
- `using (var document = new HTMLDocument(htmlPath)) { Converter.ConvertHTML(document, pdfOptions, outputPath); }`
- `PdfSaveOptions options = new PdfSaveOptions();`
- `DocSaveOptions docOptions = new DocSaveOptions();`
- `ImageSaveOptions imgOptions = new ImageSaveOptions(ImageFormat.Jpeg);`

## 14. Plugins Sharing API Pattern?
All conversion plugins (to-pdf, to-word, to-image, to-xps) share the same `Converter.ConvertHTML(doc, options, path)` pattern.
Markdown conversion may use different API.

## 15. Plugins Needing Unique Mapping?
- convert-html-to-markdown: Uses Converter.ConvertMarkdown or different approach
- merge-html: May use HTMLDocument DOM manipulation to merge content

## 16. Plugins with No Code?
- convert-html-to-markdown: No match fetched
- merge-html: No match fetched

## 17. Can Be Transformed Next Sprint?
- convert-html-to-pdf: YES
- convert-html-to-word: YES
- convert-html-to-image: YES
- convert-html-to-xps: YES
- convert-html-to-markdown: NEEDS_MANUAL_MAPPING
- merge-html: NEEDS_MANUAL_MAPPING

## 18. Blockers?
None for first 4 plugins.

## 19. Registry Strategy?
4 plugins READY_FOR_TRANSFORMATION; 2 NEEDS_MANUAL_MAPPING.

## 20. First Transformation Candidates?
1. convert-html-to-pdf
2. convert-html-to-word

## Implementation Model
`STATIC_CONVERTER_CLASS` — Converter.ConvertHTML() is the primary pattern.
