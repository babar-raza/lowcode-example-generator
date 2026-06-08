"""Fix imaging Program.cs files — use Aspose.Imaging.Brushes.SolidBrush, no DrawString."""
import pathlib

BASE = pathlib.Path(__file__).parents[1] / "reports" / "lowcode-plugin-example-factory-wave-20260605" / "dryrun" / "examples" / "imaging"

FILES = {}

FILES["resize-image"] = """\
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
"""

FILES["crop-image"] = """\
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
"""

FILES["filter-image"] = """\
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
"""

FILES["merge-images"] = """\
// imaging/merge-images
// Canonical: https://products.aspose.net/imaging/merge-images/
// Package: Aspose.Imaging 24.12.0
// Pattern: Create two BMP sources -> Create canvas -> Graphics.DrawImage -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.Brushes;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "merged.png");

var bmp1Opts = new BmpOptions { BitsPerPixel = 24 };
bmp1Opts.Source = new FileCreateSource(Path.Combine("output", "src1.bmp"), false);
using var img1 = Image.Create(bmp1Opts, 200, 150);
var g1 = new Aspose.Imaging.Graphics(img1);
g1.Clear(Aspose.Imaging.Color.SteelBlue);
g1.FillRectangle(new SolidBrush(Aspose.Imaging.Color.White), new Rectangle(20, 20, 160, 110));
img1.Save();

var bmp2Opts = new BmpOptions { BitsPerPixel = 24 };
bmp2Opts.Source = new FileCreateSource(Path.Combine("output", "src2.bmp"), false);
using var img2 = Image.Create(bmp2Opts, 200, 150);
var g2 = new Aspose.Imaging.Graphics(img2);
g2.Clear(Aspose.Imaging.Color.Tomato);
g2.FillRectangle(new SolidBrush(Aspose.Imaging.Color.White), new Rectangle(20, 20, 160, 110));
img2.Save();

var canvasOpts = new BmpOptions { BitsPerPixel = 24 };
canvasOpts.Source = new FileCreateSource(Path.Combine("output", "canvas.bmp"), false);
using var canvas = Image.Create(canvasOpts, 400, 150);
var gc = new Aspose.Imaging.Graphics(canvas);
gc.Clear(Aspose.Imaging.Color.White);
gc.DrawImage(img1, new Point(0, 0));
gc.DrawImage(img2, new Point(200, 0));
canvas.Save(outputPath, new PngOptions());

Console.WriteLine($"Merged: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
"""

FILES["watermark-image"] = """\
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
"""

FILES["rotate-image"] = """\
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
"""

for slug, content in FILES.items():
    p = BASE / slug / "Program.cs"
    p.write_text(content, encoding="utf-8")
    print(f"Written: {p}")

print("Done.")
