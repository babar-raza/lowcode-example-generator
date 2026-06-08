// Probe: Image.Load + Save — TC-IMPL-008
// Manual mapping (Image is abstract; Load is static factory — PR-03 applies to runtime type).
// PR-01: Image type confirmed in DllReflector (Aspose.Imaging 26.6.0 / Aspose.Imaging)
// PR-02: Save method confirmed in DllReflector output for Image type
// PR-03: Image.Load static factory returns concrete PngImage; runtime type is concrete
// PR-05: output path passed as CLI arg
// PR-08: dotnet run stdout/stderr captured
// Note: Image.Save(string) uses the extension to infer format.
using System;
using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;

var inputPath = args.Length > 0 ? args[0] : "input.png";
var outputPath = args.Length > 1 ? args[1] : "probe-output.jpg";

Console.WriteLine("[PROBE] Loading image from: " + inputPath);
using var image = Image.Load(inputPath);
Console.WriteLine("[PROBE] Image type: " + image.GetType().Name);
Console.WriteLine("[PROBE] Saving to: " + outputPath);
image.Save(outputPath, new JpegOptions());
Console.WriteLine("[PROBE] Image saved to: " + outputPath);
