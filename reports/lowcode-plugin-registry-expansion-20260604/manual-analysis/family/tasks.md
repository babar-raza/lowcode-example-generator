# Manual Family Analysis: tasks
## Sprint: lowcode-plugin-registry-expansion-20260604 | Date: 2026-06-04
## Evidence: https://products.aspose.net/tasks/project-to-pdf-converter/ + AsposeTasksConversion.cs

### Implementation Model: LOAD_SAVE_OPTIONS
Product page confirms `Project.Save(path, PdfSaveOptions)` as the primary pattern.

### API Pattern
```csharp
Project project = new Project(inFilePath);
PdfSaveOptions pdfSaveOptions = new PdfSaveOptions();
project.Save(outPath, (SaveOptions)pdfSaveOptions);
```

### Answers to Analysis Questions
1. Regular product APIs: YES — uses Aspose.Tasks' Project class
2. Dedicated plugin classes: NO
3. Static converter: NO
4. Load/save options: YES — `PdfSaveOptions`, `XlsxOptions`, `HtmlSaveOptions`
5. DOM workflow: YES — `Project` is the document object model
6. Recognition/extraction: NO
7. Rendering/export: YES — exports project data to PDF/images
8. Fixtures needed: YES — requires .mpp file. Workaround: use programmatic project creation
9. License-sensitive: YES — trial may limit project size or features
10. Official snippets: AsposeTasksConversion.cs confirms pattern
11. Classes: `Project`, `PdfSaveOptions`, `XlsxOptions`, `HtmlSaveOptions`
12. Shared pattern: all export plugins use `project.Save(path, formatOptions)`
13. Unique mapping: none
14. Next candidates: convert-mpp-to-pdf (READY_FOR_TRANSFORMATION)
15. Blocked: convert-mpp-to-pdf needs .mpp fixture OR programmatic project creation

### Canonical URL
Only 1 canonical page found: `/tasks/project-to-pdf-converter/`

### Transformation Priority: MEDIUM
- Requires fixture (.mpp file) — but programmatic project creation is possible:
  `Project project = new Project(); project.Save(outPath, SaveFileFormat.Pdf);`
