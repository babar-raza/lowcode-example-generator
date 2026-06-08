# Family Manual Analysis: imaging

## Date: 2026-06-04
## Evidence: GitHub repo aspose-imaging/Aspose.Imaging-for-.NET

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. Image.Load() + image.Save() is the universal pattern.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `Image` (abstract base) — all imaging operations
- `RasterImage` — raster-specific operations (resize, crop, rotate, filter)
- Various format classes (JpegImage, PngImage, etc.)

## 5. Static Converter Classes?
No.

## 6. Load/Save with Format Options?
Yes. The universal pattern: `using (Image image = Image.Load(inputPath)) { image.Save(outputPath, new JpegOptions()); }`

## 7. Document Object Model Workflow?
No.

## 8. Recognition/Extraction APIs?
No.

## 9. Rendering/Export APIs?
Yes. Various output options (PngOptions, JpegOptions, TiffOptions, BmpOptions, PdfOptions).

## 10. Fixtures Needed?
Yes. All plugins need input images (JPEG, PNG, BMP, TIFF, EMF, SVG etc.).

## 11. License-Sensitive?
Trial watermark on output images. Full API needs license.

## 12. Official Snippets?
- `ConvertImageWithGrayscale.cs` — Image.Load() + save with JpegOptions (grayscale mode)
- `FlipDICOMImage.cs` — Image.Load() + RotateFlip()
- `CropEMFFile.cs` — Image.Load() + image.Crop(rectangle)
- `CombineImages.cs` — multiple image load + combine into single output

## 13. Classes/Methods?
- `Image.Load(inputPath)` — polymorphic load
- `image.Save(outputPath, ImageOptionsBase)` — polymorphic save
- `image.Resize(width, height, ResizeType.*)` — resize
- `image.Crop(Rectangle)` — crop
- `image.RotateFlip(RotateFlipType.*)` — rotate/flip
- `image.Filter(Rectangle, FilterOptionsBase)` — filter

## 14. Plugins Sharing API Pattern?
All 8 plugins use Image.Load/Save pattern with different operations in between.

## 15. Plugins Needing Unique Mapping?
- compress-image: May need quality settings via JpegOptions.Quality
- watermark-image: Needs Graphics overlay on image
- merge-images: Needs creating new canvas + drawing multiple images

## 16. Plugins with No Code? None — all 8 have matched files.

## 17. Can Be Transformed Next Sprint?
All 8. Need input image fixtures.

## 18. Blockers?
Trial watermark on output. Fixture images needed.

## 19. Registry Strategy?
All 8: READY_FOR_TRANSFORMATION with FIXTURE_REQUIRED note.

## 20. First Transformation Candidates?
1. convert-image (simplest: Image.Load + Save with new format)
2. resize-image (common use case)
3. crop-image

## Implementation Model
`LOAD_SAVE_OPTIONS` — all plugins follow Image.Load(input) → operation → image.Save(output, options).
