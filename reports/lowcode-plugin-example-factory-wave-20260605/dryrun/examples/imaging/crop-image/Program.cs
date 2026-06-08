// imaging/crop-image
// Canonical: https://products.aspose.net/imaging/crop-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: Image.Create(BmpOptions) -> Crop(Rectangle) -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.Brushes;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "cropped.png");

var bmpOptions = new BmpOptions { BitsPerPixel = 24 };
bmpOptions.Source = new FileCreateSource(Path.Combine("output", "source-crop.bmp"), false);

using (var image = Image.Create(bmpOptions, 300, 300))
{
    var gfx = new Aspose.Imaging.Graphics(image);
    gfx.Clear(Aspose.Imaging.Color.PaleGreen);
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.DarkGreen), new Rectangle(75, 75, 150, 150));
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.LightGreen), new Rectangle(85, 85, 130, 130));
    image.Save();
    var raster = (RasterImage)image;
    raster.Crop(new Rectangle(75, 75, 150, 150));
    raster.Save(outputPath, new PngOptions());
}
Console.WriteLine($"Cropped: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
