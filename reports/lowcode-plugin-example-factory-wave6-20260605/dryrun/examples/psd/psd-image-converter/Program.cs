// psd/psd-image-converter
// Canonical: https://products.aspose.net/psd/image-converter/
// Package: Aspose.PSD 24.12.0
// Pattern: new PsdImage(w,h) -> Clear(Color) -> Save PSD -> reload -> Save(JpegOptions)
using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string psdFixturePath = Path.Combine("output", "fixture.psd");
string outputPath = Path.Combine("output", "output.jpg");

// Create PSD programmatically with blue background
using (var psdImage = new PsdImage(200, 150))
{
    var graphics = new Graphics(psdImage);
    graphics.Clear(Color.FromArgb(70, 130, 180));  // SteelBlue
    psdImage.Save(psdFixturePath);
}

// Load and convert to JPEG
using (var image = (PsdImage)Image.Load(psdFixturePath))
{
    image.Save(outputPath, new JpegOptions { Quality = 90 });
}
Console.WriteLine($"PSD converted to JPEG: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
