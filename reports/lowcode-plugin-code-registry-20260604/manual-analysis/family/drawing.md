# Family Manual Analysis: drawing

## Date: 2026-06-04
## Evidence: GitHub repo aspose-drawing/Aspose.Drawing-for-.NET, code: LoadSave.cs, DrawArc.cs

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. Bitmap + Graphics API (System.Drawing compatible).
## 4. Dedicated Plugin-Like Classes?
Yes:
- `Bitmap` — image/drawing surface
- `Graphics` — drawing operations (FromImage, DrawLine, DrawArc, DrawText)
- `ImageFormat` — output format

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Yes. Bitmap(width, height) or Bitmap(file) + bitmap.Save(path, ImageFormat).
## 7. Document Object Model Workflow? No (drawing operations are imperative).
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. Bitmap.Save to various formats.

## 10. Fixtures Needed?
- convert-drawing: Needs input image file
- create-drawing: No input needed (creates from scratch)

## 11. License-Sensitive?
Trial limitations on output quality.

## 12. Official Snippets?
- `LoadSave.cs` — `new Bitmap(inputPath)` + `bitmap.Save(outputPath, ImageFormat.Png)`
- `DrawArc.cs` — `new Bitmap(w, h)` + `Graphics.FromImage(bmp)` + `g.DrawArc(...)` + save

## 13. Classes/Methods?
- `Bitmap bmp = new Bitmap(inputPath);`
- `bmp.Save(outputPath, ImageFormat.Png);`
- `Bitmap bmp = new Bitmap(800, 600);`
- `Graphics g = Graphics.FromImage(bmp);`
- `g.DrawArc(pen, x, y, w, h, startAngle, sweepAngle);`

## 14. Plugins Sharing API Pattern?
Both plugins use Bitmap as core. convert uses load; create uses construct.

## 15. Plugins Needing Unique Mapping?
create-drawing: Graphics operations are creative — what to draw?

## 16. Plugins with No Code?
None — both matched.

## 17. Can Be Transformed Next Sprint?
- convert-drawing: YES (needs input image)
- create-drawing: YES (self-contained)

## 18. Blockers?
None significant.

## 19. Registry Strategy?
Both READY_FOR_TRANSFORMATION.

## 20. First Transformation Candidates?
1. create-drawing (no fixture needed)
2. convert-drawing

## Implementation Model
`RENDERING_API` — Bitmap + Graphics drawing surface operations.
