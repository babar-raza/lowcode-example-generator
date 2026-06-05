// psd/photo-processor
// Canonical: https://products.aspose.net/psd/photo-processor/
// Package: Aspose.PSD 24.12.0
// Pattern: PsdImage.Load -> resize/process -> Save(JpegOptions)
using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string psdFixturePath = Path.Combine("output", "fixture.psd");
string outputPath = Path.Combine("output", "processed.jpg");

// Create a PSD fixture programmatically with color background
using (var psdImage = new PsdImage(200, 150))
{
    var graphics = new Graphics(psdImage);
    graphics.Clear(Color.FromArgb(34, 139, 34));  // ForestGreen
    psdImage.Save(psdFixturePath);
}

// Load and process: resize + convert to JPEG
using (var image = (PsdImage)Image.Load(psdFixturePath))
{
    // Resize (simulate photo processing: scale down)
    image.Resize(100, 75);

    // Save as processed JPEG
    var jpegOptions = new JpegOptions { Quality = 85 };
    image.Save(outputPath, jpegOptions);
}

var fileInfo = new FileInfo(outputPath);
Console.WriteLine($"Photo processed: {outputPath} ({fileInfo.Length} bytes)");
