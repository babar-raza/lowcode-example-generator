# Family Manual Analysis: tasks

## Date: 2026-06-04
## Evidence: GitHub repo aspose-tasks/Aspose.Tasks-for-.NET, code: ExXlsxOptions.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. Project class with Save method.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `Project` — main class, loads MPP/MPX/XML project files
- `SaveFileFormat` — enum for output format (Pdf, Xlsx, Html, Png, Jpg etc.)

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Yes. `project.Save(outputPath, SaveFileFormat.Pdf)`.
## 7. Document Object Model Workflow? Yes. Project has tasks, resources, calendars hierarchy.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. Pdf, image, HTML export.

## 10. Fixtures Needed?
Yes. All conversion plugins need input MPP/MPX files.
Probe confirmed with new empty Project(). For conversion, existing file is better.

## 11. License-Sensitive?
Trial watermark on output. Prior probe confirmed with empty project.

## 12. Official Snippets?
- `ExXlsxOptions.cs` — `new Project(mppPath)` + `project.Save(outPath, SaveFileFormat.Xlsx)`

## 13. Classes/Methods?
- `var project = new Project(inputPath);`
- `project.Save(outputPath, SaveFileFormat.Pdf);`
- `XlsxOptions` — Excel output options
- `HtmlSaveOptions` — HTML output options
- `ImageSaveOptions` — image output options

## 14. Plugins Sharing API Pattern?
All conversion plugins share `Project.Save(path, format)` pattern.

## 15. Plugins Needing Unique Mapping?
- read-project-data: Uses Project.RootTask, Project.Tasks to enumerate tasks

## 16. Plugins with No Code?
read-project-data: No direct match, but API is simple.

## 17. Can Be Transformed Next Sprint?
- convert-mpp-to-pdf: YES
- convert-mpp-to-excel: YES
- convert-mpp-to-html: YES
- convert-mpp-to-image: YES
- read-project-data: NEEDS_MANUAL_MAPPING

## 18. Blockers?
None for conversion plugins. Need MPP input fixture.

## 19. Registry Strategy?
4 conversion plugins READY_FOR_TRANSFORMATION; 1 NEEDS_MANUAL_MAPPING.

## 20. First Transformation Candidates?
1. convert-mpp-to-pdf (prior probe confirmed)
2. convert-mpp-to-excel

## Implementation Model
`LOAD_SAVE_OPTIONS` — Project.Load(path) + project.Save(path, format).
