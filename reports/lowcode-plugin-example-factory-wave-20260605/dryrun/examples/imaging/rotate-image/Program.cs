// imaging/rotate-image
// Canonical: https://products.aspose.net/imaging/rotate-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: Create BMP -> RasterImage.Rotate(90f) -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.Brushes;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "rotated.png");

var bmpOptions = new BmpOptions { BitsPerPixel = 24 };
bmpOptions.Source = new FileCreateSource(Path.Combine("output", "source-rotate.bmp"), false);

using (var image = Image.Create(bmpOptions, 300, 150))
{
    var gfx = new Aspose.Imaging.Graphics(image);
    gfx.Clear(Aspose.Imaging.Color.LightCoral);
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.DarkRed), new Rectangle(20, 20, 260, 110));
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.LightCoral), new Rectangle(30, 30, 240, 90));
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.DarkRed), new Rectangle(240, 60, 40, 10));
    image.Save();
    var raster = (RasterImage)image;
    raster.Rotate(90f);
    raster.Save(outputPath, new PngOptions());
}
Console.WriteLine($"Rotated: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
