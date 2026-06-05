// psd/convert-psd-to-pdf
// Canonical: https://products.aspose.net/psd/psd-to-pdf/
// Package: Aspose.PSD 24.12.0
// Pattern: new PsdImage(w,h) -> Clear(Color) -> Save PSD -> Image.Load -> Save(PdfOptions)
using Aspose.PSD;
using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string psdFixturePath = Path.Combine("output", "fixture.psd");
string outputPath = Path.Combine("output", "output.pdf");

// Create PSD programmatically
using (var psdImage = new PsdImage(300, 200))
{
    var graphics = new Graphics(psdImage);
    graphics.Clear(Color.FromArgb(255, 255, 255));  // White background
    psdImage.Save(psdFixturePath);
}

// Load PSD and convert to PDF
using (var image = Image.Load(psdFixturePath))
{
    image.Save(outputPath, new PdfOptions());
}
Console.WriteLine($"PSD converted to PDF: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
