# Family Manual Analysis: svg

## Date: 2026-06-04
## Evidence: GitHub repo aspose-svg/Aspose.SVG-for-.NET, code: ConvertSVGToPDF.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. SVGDocument + Converter static class.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `SVGDocument` — loads and represents SVG content
- `Converter` static class — ConvertSVG(document, options, outputPath)
- `PdfRenderingOptions`, `ImageRenderingOptions` — format options

## 5. Static Converter Classes?
Yes. `Aspose.Svg.Converters.Converter.ConvertSVG(doc, options, outputPath)`.

## 6. Load/Save with Format Options? Yes. Via Converter static methods.
## 7. Document Object Model Workflow? Yes. SVGDocument has DOM navigation.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. PDF, PNG, JPEG, BMP rendering.

## 10. Fixtures Needed?
Yes. All plugins need input SVG files.

## 11. License-Sensitive?
Trial limitations.

## 12. Official Snippets?
- `ConvertSVGToPDF.cs` — SVGDocument(svgPath) + PdfRenderingOptions + Converter.ConvertSVG()

## 13. Classes/Methods?
- `using (var document = new SVGDocument(svgPath))`
- `var options = new PdfRenderingOptions()`
- `Converter.ConvertSVG(document, options, outputPath)`
- `ImageRenderingOptions imgOpts = new ImageRenderingOptions(ImageFormat.Png)`

## 14. Plugins Sharing API Pattern?
convert-svg-to-pdf, convert-svg-to-png, convert-svg-to-jpg share same Converter.ConvertSVG pattern.
merge-svg: Different approach (SVGDocument combination or canvas).

## 15. Plugins Needing Unique Mapping?
- convert-svg-to-png: ImageRenderingOptions with Png format
- convert-svg-to-jpg: ImageRenderingOptions with Jpeg format
- merge-svg: NEEDS_MANUAL_MAPPING

## 16. Plugins with No Code?
- convert-svg-to-png: No direct match (only pdf matched in fetch)
- convert-svg-to-jpg: No direct match
- merge-svg: No direct match

## 17. Can Be Transformed Next Sprint?
- convert-svg-to-pdf: YES
- convert-svg-to-png: NEEDS_MANUAL_MAPPING (pattern clear from PDF variant)
- convert-svg-to-jpg: NEEDS_MANUAL_MAPPING
- merge-svg: NEEDS_MANUAL_MAPPING

## 18. Blockers?
SVG input fixture needed.

## 19. Registry Strategy?
1 READY_FOR_TRANSFORMATION; 3 NEEDS_MANUAL_MAPPING.

## 20. First Transformation Candidates?
1. convert-svg-to-pdf

## Implementation Model
`STATIC_CONVERTER_CLASS` — Converter.ConvertSVG() is primary pattern.
