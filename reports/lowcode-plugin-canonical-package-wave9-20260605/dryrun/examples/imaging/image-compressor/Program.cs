// imaging/compress-image
// Canonical: https://products.aspose.net/imaging/image-compressor/
// Package: Aspose.Imaging 24.12.0
// Pattern: Create BMP -> Save as JPEG with quality=75 (compression)
using Aspose.Imaging;
using Aspose.Imaging.Brushes;
using Aspose.Imaging.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "compressed.jpg");

using (var bmp = new Aspose.Imaging.FileFormats.Bmp.BmpImage(400, 300))
{
    var graphics = new Graphics(bmp);
    graphics.Clear(Color.FromArgb(255, 240, 248, 255));

    // Draw layered rectangles for visual interest
    int[] r = {200, 100, 150, 80, 120};
    int[] g = {60,  180,  40, 220,  90};
    int[] b = {60,   60, 200,  60, 190};
    for (int i = 0; i < 5; i++)
    {
        graphics.FillRectangle(
            new SolidBrush(Color.FromArgb(255, (byte)r[i], (byte)g[i], (byte)b[i])),
            new Rectangle(20 + i * 60, 30 + i * 30, 150, 80));
    }

    // Save as JPEG quality 75 — compress relative to BMP source
    bmp.Save(outputPath, new JpegOptions { Quality = 75 });
}
long size = new FileInfo(outputPath).Length;
Console.WriteLine($"Compressed JPEG (q=75): {outputPath} ({size} bytes)");
