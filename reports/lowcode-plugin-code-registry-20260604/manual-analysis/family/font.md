# Family Manual Analysis: font

## Date: 2026-06-04
## Evidence: GitHub repo aspose-font/Aspose.Font-for-.NET, code: RunExamples.cs, RenderingText.cs
## Prior sprint: PROBE_CONFIRMED (trial-restricted to allowlisted fonts)

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. Font.Open() + font.Save() or rendering.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `Font` — abstract base, opened via FontDefinition
- `FontDefinition` — specifies font type + file path
- `TtfFont`, `Type1Font`, `CffFont` — specific font types
- `FontRenderer` — renders text using font (GlyphId to bitmap)

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Yes. `Font.Open(definition)` + `font.Save(outputPath)`.
## 7. Document Object Model Workflow? No.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. Text rendering to image/glyph output.

## 10. Fixtures Needed?
Yes. Needs input font files (TTF, OTF, Type1, CFF).
Trial mode restriction: only allowlisted fonts work (Montserrat, Noto Sans JP, Merriweather, Lora, Source Code Pro).

## 11. License-Sensitive?
YES — STRONGLY. Trial restricts font loading to allowlisted fonts only.
Prior probe confirmed with Montserrat.ttf (free font).

## 12. Official Snippets?
- `RenderingText.cs` — FontDefinition + Font.Open() + GlyphId rendering
- `RunExamples.cs` — program entry, lists available examples

## 13. Classes/Methods?
Convert font:
- `FontDefinition fd = new FontDefinition(FontType.TTF, new FontFileDefinition(new FileSystemStreamSource(fontPath)))`
- `TtfFont font = (TtfFont)Font.Open(fd)`
- `font.Save(outputPath)` — converts to same or different format

Render text:
- `FontRenderer renderer = new FontRenderer(font)`
- `renderer.RenderText(text, size, outImage)`

## 14. Plugins Sharing API Pattern?
convert-font: Font.Open + Save (different font type)
render-text-with-font: Font.Open + FontRenderer + render to image

## 15. Plugins Needing Unique Mapping?
render-text-with-font: Unique rendering path.

## 16. Plugins with No Code?
None — both have code.

## 17. Can Be Transformed Next Sprint?
- convert-font: YES with allowlisted font (ENVIRONMENT_DEPENDENT)
- render-text-with-font: YES with allowlisted font (ENVIRONMENT_DEPENDENT)

## 18. Blockers?
Trial font restriction. Documented as ENVIRONMENT_DEPENDENT_PASS.

## 19. Registry Strategy?
Both READY_FOR_TRANSFORMATION with ENVIRONMENT_DEPENDENT note.

## 20. First Transformation Candidates?
1. convert-font

## Implementation Model
`LOAD_SAVE_OPTIONS` — Font.Open(definition) + font.Save().
render-text-with-font: `RENDERING_API`.
