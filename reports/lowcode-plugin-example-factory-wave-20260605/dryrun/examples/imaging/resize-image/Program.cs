// imaging/resize-image
// Canonical: https://products.aspose.net/imaging/resize-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: Image.Create(BmpOptions) -> ResizeWidthProportionally -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.Brushes;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "resized.png");

var bmpOptions = new BmpOptions { BitsPerPixel = 24 };
bmpOptions.Source = new FileCreateSource(Path.Combine("output", "source.bmp"), false);

using (var image = Image.Create(bmpOptions, 400, 300))
{
    var gfx = new Aspose.Imaging.Graphics(image);
    gfx.Clear(Aspose.Imaging.Color.LightSkyBlue);
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.Navy), new Rectangle(20, 20, 360, 260));
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.LightSkyBlue), new Rectangle(30, 30, 340, 240));
    image.Save();
    image.ResizeWidthProportionally(200, ResizeType.HighQualityResample);
    image.Save(outputPath, new PngOptions());
}
Console.WriteLine($"Resized: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
