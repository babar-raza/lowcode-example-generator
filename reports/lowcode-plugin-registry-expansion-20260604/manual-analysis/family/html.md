# Manual Family Analysis: html
## Sprint: lowcode-plugin-registry-expansion-20260604 | Date: 2026-06-04
## Evidence: https://products.aspose.net/html/html-to-pdf-converter/ + HTMLtoPDFExample.cs

### Implementation Model: STATIC_CONVERTER_CLASS
Canonical product page confirms `Converter.ConvertHTML()` as the primary static conversion method.

### API Pattern
```csharp
using HTMLDocument document = new HTMLDocument(htmlPath);
PdfSaveOptions options = new PdfSaveOptions();
Converter.ConvertHTML(document, options, outputPdfPath);
// OR single-line:
Converter.ConvertHTML("<h1>text</h1>", ".", new PdfSaveOptions(), outputPath);
```

### Answers to Analysis Questions
1. Regular product APIs: YES — uses Aspose.HTML's standard Converter class
2. Dedicated plugin classes: NO — uses Converter static class
3. Static converter: YES — `Converter.ConvertHTML()` is the pattern
4. Load/save options: YES — `PdfSaveOptions`, `DocSaveOptions`, `XpsSaveOptions`
5. DOM workflow: YES — `HTMLDocument` represents the document object model
6. Recognition/extraction: NO
7. Rendering/export: YES — renders HTML to PDF/images
8. Fixtures needed: YES — needs an HTML input file or inline HTML string (can be inline for no-fixture probe)
9. License-sensitive: YES — trial may watermark output; metered licensing supported
10. Official snippets: HTMLtoPDFExample.cs confirms full pattern
11. Classes: `HTMLDocument`, `PdfSaveOptions`, `DocSaveOptions`, `XpsSaveOptions`, `Converter`, `MemoryStreamProvider`
12. Shared pattern: all HTML conversion plugins share Converter.ConvertHTML() with format-specific SaveOptions
13. Unique mapping: none; all follow same pattern
14. Next candidates: convert-html-to-pdf (READY), convert-html-to-word (CODE_HARVESTED)
15. Blocked: none confirmed

### Canonical URL
Only 1 canonical page found: `/html/html-to-pdf-converter/`
Other old slugs (convert-html-to-word, convert-html-to-image, etc.) have no confirmed canonical pages.

### Transformation Priority: HIGH
- No fixture needed if using inline HTML string
- Single-line call: `Converter.ConvertHTML("<h1>Hi</h1>", ".", new PdfSaveOptions(), path)`
