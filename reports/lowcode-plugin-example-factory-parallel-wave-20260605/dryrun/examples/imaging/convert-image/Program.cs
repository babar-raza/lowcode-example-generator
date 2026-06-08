// imaging/convert-image
// Canonical: https://products.aspose.net/imaging/image-converter/
// Package: Aspose.Imaging 24.12.0
// Pattern: Create BMP -> Save as PNG (format conversion)
using Aspose.Imaging;
using Aspose.Imaging.Brushes;
using Aspose.Imaging.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "converted.png");

using (var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(200, 200))
{
    var graphics = new Graphics(bmp);
    graphics.Clear(Color.FromArgb(255, 245, 250, 255));

    // Blue filled rectangle
    graphics.FillRectangle(
        new SolidBrush(Color.FromArgb(255, 74, 144, 217)),
        new Rectangle(20, 20, 160, 80));

    // White filled rectangle (inner)
    graphics.FillRectangle(
        new SolidBrush(Color.White),
        new Rectangle(40, 40, 120, 40));

    // Green ellipse
    graphics.FillEllipse(
        new SolidBrush(Color.FromArgb(255, 80, 200, 120)),
        new Rectangle(60, 130, 80, 50));

    bmp.Save(outputPath, new PngOptions());
}
Console.WriteLine($"Converted BMP->PNG: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
