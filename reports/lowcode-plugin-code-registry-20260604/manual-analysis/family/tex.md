# Family Manual Analysis: tex

## Date: 2026-06-04
## Evidence: GitHub repo aspose-tex/Aspose.TeX-for-.NET, code: LaTeXPdfConversionAlternative.cs, LaTeXSvgConversionSimplest.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. TeXOptions + LaTeX.Process().
## 4. Dedicated Plugin-Like Classes?
Yes:
- `TeXOptions` — configuration for TeX/LaTeX compilation
- `LaTeX` static class with `.Process()` method

## 5. Static Converter Classes? Yes. `LaTeX.Process(inputPath, options)`.
## 6. Load/Save with Format Options? Yes via TeXOptions configuration.
## 7. Document Object Model Workflow? No.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. PDF, SVG, XPS, image output.

## 10. Fixtures Needed?
Yes. All plugins need input TeX or LaTeX source files.

## 11. License-Sensitive?
Trial limitations on output.

## 12. Official Snippets?
- `LaTeXPdfConversionAlternative.cs` — TeXOptions + PdfSaveOptions + Process()
- `LaTeXSvgConversionSimplest.cs` — TeXOptions + SvgSaveOptions + Process()

## 13. Classes/Methods?
- `TeXOptions options = TeXOptions.ConsoleAppOptions(TeXConfig.ObjectLaTeX)`
- `options.OutputWorkingDirectory = new OutputFileSystemDirectory(outDir)`
- `options.SaveOptions = new PdfSaveOptions()`
- `new TeXJob(inputTexFile, new PdfDevice(), options).Run()`

## 14. Plugins Sharing API Pattern?
All 3 plugins use TeXOptions + TeXJob pattern, different SaveOptions.

## 15. Plugins Needing Unique Mapping?
- convert-tex-to-svg: SvgDevice instead of PdfDevice

## 16. Plugins with No Code?
All 3 have fetched GitHub examples.

## 17. Can Be Transformed Next Sprint?
All 3 YES.

## 18. Blockers?
LaTeX source fixture file needed.

## 19. Registry Strategy?
All 3 READY_FOR_TRANSFORMATION.

## 20. First Transformation Candidates?
1. convert-tex-to-pdf

## Implementation Model
`STATIC_CONVERTER_CLASS` — TeXJob/LaTeX.Process() is the primary compilation pattern.
