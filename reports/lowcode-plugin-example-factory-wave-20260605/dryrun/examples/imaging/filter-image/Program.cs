// imaging/filter-image
// Canonical: https://products.aspose.net/imaging/filter-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: RasterImage.Filter(bounds, GaussWienerFilterOptions) -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.Brushes;
using Aspose.Imaging.ImageFilters.FilterOptions;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "filtered.png");

var bmpOptions = new BmpOptions { BitsPerPixel = 24 };
bmpOptions.Source = new FileCreateSource(Path.Combine("output", "source-filter.bmp"), false);

using (var image = Image.Create(bmpOptions, 300, 200))
{
    var gfx = new Aspose.Imaging.Graphics(image);
    gfx.Clear(Aspose.Imaging.Color.WhiteSmoke);
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.Black), new Rectangle(30, 30, 80, 80));
    gfx.FillEllipse(new SolidBrush(Aspose.Imaging.Color.Blue), new Rectangle(150, 30, 100, 80));
    gfx.FillRectangle(new SolidBrush(Aspose.Imaging.Color.Red), new Rectangle(30, 130, 80, 50));
    gfx.FillEllipse(new SolidBrush(Aspose.Imaging.Color.Green), new Rectangle(150, 130, 100, 50));
    image.Save();
    var raster = (RasterImage)image;
    raster.Filter(raster.Bounds, new GaussWienerFilterOptions(5, 1.5));
    raster.Save(outputPath, new PngOptions());
}
Console.WriteLine($"Filtered: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
