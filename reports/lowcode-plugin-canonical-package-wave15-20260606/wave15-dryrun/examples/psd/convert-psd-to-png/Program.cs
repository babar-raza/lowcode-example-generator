// psd/convert-psd-to-png
// Canonical: https://products.aspose.net/psd/convert-psd-to-png/
// Package: Aspose.PSD 24.12.0
// Pattern: new PsdImage(w,h) -> Clear(Color) -> Save PSD -> Image.Load -> Save(PngOptions)
using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string psdFixturePath = Path.Combine("output", "fixture.psd");
string outputPath = Path.Combine("output", "output.png");

// Create PSD programmatically
using (var psdImage = new PsdImage(400, 300))
{
    var graphics = new Graphics(psdImage);
    graphics.Clear(Color.FromArgb(255, 173, 216, 230)); // Light blue background
    psdImage.Save(psdFixturePath);
}

// Load PSD and convert to PNG
using (var image = Image.Load(psdFixturePath))
{
    image.Save(outputPath, new PngOptions());
}
Console.WriteLine($"PSD converted to PNG: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
