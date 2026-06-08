// imaging/watermark-image
// Canonical: https://products.aspose.net/imaging/watermark-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: Create BMP -> diagonal stripe watermark via FillRectangle -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.Brushes;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "watermarked.png");

var bmpOptions = new BmpOptions { BitsPerPixel = 24 };
bmpOptions.Source = new FileCreateSource(Path.Combine("output", "source-watermark.bmp"), false);

using (var image = Image.Create(bmpOptions, 400, 300))
{
    var gfx = new Aspose.Imaging.Graphics(image);
    gfx.Clear(Aspose.Imaging.Color.LightYellow);
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.SaddleBrown), new Rectangle(20, 20, 360, 260));
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.LightYellow), new Rectangle(25, 25, 350, 250));

    // Watermark: semi-transparent diagonal stripe effect (simulated)
    var watermarkBrush = new SolidBrush(Aspose.Imaging.Color.FromArgb(60, 180, 180, 180));
    for (int i = -300; i < 400; i += 50)
    {
        gfx.FillRectangle(watermarkBrush, new Rectangle(i, 0, 15, 300));
    }

    image.Save(outputPath, new PngOptions());
}
Console.WriteLine($"Watermarked: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
