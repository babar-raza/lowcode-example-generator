"""
Lane D: Generate Wave A dry-run packages for lowcode-plugin-example-factory-wave-20260605.
Produces 12 packages under reports/lowcode-plugin-example-factory-wave-20260605/dryrun/examples/.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.plugin_examples.plugin_code_registry.loader import PluginCodeRegistryLoader
from src.plugin_examples.example_factory.generator import ExamplePackageGenerator

REPORT_ROOT = Path(__file__).parents[1] / "reports" / "lowcode-plugin-example-factory-wave-20260605"
DRYRUN_ROOT = REPORT_ROOT / "dryrun" / "examples"

# ── Program.cs content for each candidate ─────────────────────────────────────

PROGRAMS: dict[str, str] = {

"barcode/generate-qr-code": """\
// barcode/generate-qr-code
// Canonical: https://products.aspose.net/barcode/qr-code-generator/
// Package: Aspose.BarCode 24.12.0
// Pattern: BarcodeGenerator(EncodeTypes.QR, text) -> Save PNG
using Aspose.BarCode.Generation;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "qr-code.png");

var generator = new BarcodeGenerator(EncodeTypes.QR, "https://www.aspose.com");
generator.Parameters.Barcode.XDimension.Pixels = 6;
generator.Parameters.Barcode.QR.QrErrorLevel = QRErrorLevel.LevelH;
generator.Save(outputPath, BarCodeImageFormat.Png);

Console.WriteLine($"QR code saved: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",

"barcode/scan-barcode": """\
// barcode/scan-barcode
// Canonical: https://products.aspose.net/barcode/barcode-scanner/
// Package: Aspose.BarCode 24.12.0
// Pattern: BarcodeGenerator -> Save -> BarCodeReader -> ReadBarCodes
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System;
using System.IO;

Directory.CreateDirectory("output");

// Step 1: Generate a Code128 barcode to use as input
string barcodePath = Path.Combine("output", "input-barcode.png");
var gen = new BarcodeGenerator(EncodeTypes.Code128, "SCAN-DEMO-20260605");
gen.Parameters.Barcode.XDimension.Pixels = 3;
gen.Save(barcodePath, BarCodeImageFormat.Png);

// Step 2: Scan (recognize) it
var reader = new BarCodeReader(barcodePath, DecodeType.AllSupportedTypes);
var results = reader.ReadBarCodes();

string resultText = results.Length > 0
    ? $"Type: {results[0].CodeTypeName}, Value: {results[0].CodeText}"
    : "No barcode recognized";

string resultPath = Path.Combine("output", "scan-result.txt");
File.WriteAllText(resultPath, resultText);
Console.WriteLine($"Scan result: {resultText}");
Console.WriteLine($"Result saved: {resultPath}");
""",

"svg/svg-to-pdf-converter": """\
// svg/svg-to-pdf-converter
// Canonical: https://products.aspose.net/svg/svg-to-pdf/
// Package: Aspose.SVG 24.12.0
// Pattern: new SVGDocument(svgString, baseUri) -> Converter.ConvertSVG(doc, PdfSaveOptions, outputPath)
using Aspose.Svg;
using Aspose.Svg.Converters;
using Aspose.Svg.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.pdf");

string svgContent =
    "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"400\" height=\"200\">" +
    "<rect width=\"400\" height=\"200\" fill=\"#f0f4ff\"/>" +
    "<rect x=\"20\" y=\"20\" width=\"360\" height=\"160\" rx=\"10\" fill=\"#4a90d9\" opacity=\"0.8\"/>" +
    "<text x=\"200\" y=\"115\" text-anchor=\"middle\" font-size=\"32\" fill=\"white\" font-family=\"Arial\">SVG to PDF</text>" +
    "</svg>";

using var document = new SVGDocument(svgContent, ".");
var pdfOptions = new PdfSaveOptions();
Converter.ConvertSVG(document, pdfOptions, outputPath);

Console.WriteLine($"PDF saved: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",

"tex/latex-figure-renderer": (
    "// tex/latex-figure-renderer\n"
    "// Canonical: https://products.aspose.net/tex/latex-figure-renderer/\n"
    "// Package: Aspose.TeX 24.12.0\n"
    "// Pattern: PngFigureRendererPlugin -> Process(options with StringDataSource + StreamDataTarget)\n"
    "using Aspose.TeX.Plugins;\n"
    "using System;\n"
    "using System.IO;\n"
    "\n"
    "Directory.CreateDirectory(\"output\");\n"
    "string outputPath = Path.Combine(\"output\", \"figure.png\");\n"
    "\n"
    "// TikZ figure: coordinate axes with a linear function\n"
    "string tikzFigure =\n"
    "    \"\\\\begin{tikzpicture}\" +\n"
    "    \"\\\\draw[thick,->] (0,0) -- (3,0) node[right] {$x$};\" +\n"
    "    \"\\\\draw[thick,->] (0,0) -- (0,2.5) node[above] {$y$};\" +\n"
    "    \"\\\\draw[blue,thick] (0,0) -- (2.8,1.96);\" +\n"
    "    \"\\\\node[below] at (1.5,0) {$y = 0.7x$};\" +\n"
    "    \"\\\\end{tikzpicture}\";\n"
    "\n"
    "var plugin = new PngFigureRendererPlugin();\n"
    "var options = new PngFigureRendererPluginOptions\n"
    "{\n"
    "    Resolution = 150,\n"
    "    Margin = 10,\n"
    "    BackgroundColor = System.Drawing.Color.White\n"
    "};\n"
    "options.AddInputDataSource(new StringDataSource(tikzFigure));\n"
    "\n"
    "using var outStream = File.Open(outputPath, FileMode.Create);\n"
    "options.AddOutputDataTarget(new StreamDataTarget(outStream));\n"
    "\n"
    "plugin.Process(options);\n"
    "outStream.Close();\n"
    "\n"
    "Console.WriteLine($\"Figure rendered: {outputPath} ({new FileInfo(outputPath).Length} bytes)\");\n"
),

"zip/create-archive": """\
// zip/create-archive
// Canonical: https://products.aspose.net/zip/create-archive/
// Package: Aspose.ZIP 24.12.0
// Pattern: new Archive() -> archive.CreateEntry(name, stream) -> archive.Save(outputPath)
using Aspose.Zip;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "archive.zip");

using (var archive = new Archive())
{
    // Add first entry from memory stream
    byte[] data1 = Encoding.UTF8.GetBytes("Hello from Aspose.ZIP — file1.txt");
    archive.CreateEntry("file1.txt", new MemoryStream(data1));

    // Add second entry
    byte[] data2 = Encoding.UTF8.GetBytes("Second document content for demonstration.");
    archive.CreateEntry("docs/file2.txt", new MemoryStream(data2));

    // Add a JSON entry
    byte[] data3 = Encoding.UTF8.GetBytes("{\"generated\": \"2026-06-05\", \"sprint\": \"factory-wave\"}");
    archive.CreateEntry("metadata.json", new MemoryStream(data3));

    archive.Save(outputPath);
}

Console.WriteLine($"Archive created: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",

"zip/compress-folder": """\
// zip/compress-folder
// Canonical: https://products.aspose.net/zip/compress-folder/
// Package: Aspose.ZIP 24.12.0
// Pattern: Create temp dir with files -> new Archive() -> CreateEntries(DirectoryInfo) -> Save
using Aspose.Zip;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "compressed-folder.zip");

// Create a temporary directory structure to compress
string tempDir = Path.Combine(Path.GetTempPath(), "aspose-zip-demo-" + Guid.NewGuid().ToString("N")[..8]);
Directory.CreateDirectory(Path.Combine(tempDir, "subdir"));

File.WriteAllText(Path.Combine(tempDir, "readme.txt"), "Folder compression demo via Aspose.ZIP");
File.WriteAllText(Path.Combine(tempDir, "data.csv"), "id,name,value\n1,alpha,100\n2,beta,200\n3,gamma,300");
File.WriteAllText(Path.Combine(tempDir, "subdir", "notes.txt"), "Notes in subdirectory");

try
{
    using (var archive = new Archive())
    {
        archive.CreateEntries(new DirectoryInfo(tempDir));
        archive.Save(outputPath);
    }
    Console.WriteLine($"Folder compressed: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
}
finally
{
    Directory.Delete(tempDir, true);
}
""",

"imaging/resize-image": """\
// imaging/resize-image
// Canonical: https://products.aspose.net/imaging/resize-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: Image.Create(BmpOptions, w, h) -> ResizeWidthProportionally -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "resized.png");

// Create a 400x300 BMP programmatically
var bmpOptions = new BmpOptions { BitsPerPixel = 24 };
bmpOptions.Source = new FileCreateSource(Path.Combine("output", "source.bmp"), false);

using (var sourceImage = Image.Create(bmpOptions, 400, 300))
{
    var gfx = new Aspose.Imaging.Graphics(sourceImage);
    gfx.Clear(Aspose.Imaging.Color.LightSkyBlue);
    gfx.DrawRectangle(new Aspose.Imaging.Pen(Aspose.Imaging.Color.Navy, 4), 20, 20, 360, 260);
    gfx.DrawString("400x300 Source", new Aspose.Imaging.Font("Arial", 18), new Aspose.Imaging.SolidBrush(Aspose.Imaging.Color.DarkBlue), 80, 130);
    sourceImage.Save();

    // Resize proportionally to width=200
    sourceImage.ResizeWidthProportionally(200, ResizeType.HighQualityResample);
    sourceImage.Save(outputPath, new PngOptions());
}

Console.WriteLine($"Resized image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",

"imaging/crop-image": """\
// imaging/crop-image
// Canonical: https://products.aspose.net/imaging/crop-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: Image.Create(BmpOptions) -> Crop(Rectangle) -> Save PNG
using Aspose.Imaging;
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

    // Draw a distinct pattern to make crop visible
    for (int i = 0; i < 300; i += 30)
    {
        gfx.DrawLine(new Aspose.Imaging.Pen(Aspose.Imaging.Color.DarkGreen, 1), 0, i, 300, i);
        gfx.DrawLine(new Aspose.Imaging.Pen(Aspose.Imaging.Color.DarkGreen, 1), i, 0, i, 300);
    }
    gfx.DrawRectangle(new Aspose.Imaging.Pen(Aspose.Imaging.Color.Red, 3), 75, 75, 150, 150);
    image.Save();

    // Crop to centre 150x150 region
    var raster = (RasterImage)image;
    raster.Crop(new Rectangle(75, 75, 150, 150));
    raster.Save(outputPath, new PngOptions());
}

Console.WriteLine($"Cropped image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",

"imaging/filter-image": """\
// imaging/filter-image
// Canonical: https://products.aspose.net/imaging/filter-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: RasterImage.Filter(bounds, GaussWienerFilterOptions) -> Save PNG
using Aspose.Imaging;
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

    // Draw some sharp shapes that blur nicely
    var pen = new Aspose.Imaging.Pen(Aspose.Imaging.Color.Black, 2);
    gfx.DrawRectangle(pen, 30, 30, 80, 80);
    gfx.DrawEllipse(pen, 150, 30, 100, 80);
    gfx.FillRectangle(new Aspose.Imaging.SolidBrush(Aspose.Imaging.Color.Blue), 30, 130, 80, 50);
    gfx.FillEllipse(new Aspose.Imaging.SolidBrush(Aspose.Imaging.Color.Red), 150, 130, 100, 50);
    image.Save();

    // Apply Gauss-Wiener smoothing filter
    var raster = (RasterImage)image;
    var filterOptions = new GaussWienerFilterOptions(5, 1.5);
    raster.Filter(raster.Bounds, filterOptions);
    raster.Save(outputPath, new PngOptions());
}

Console.WriteLine($"Filtered image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",

"imaging/merge-images": """\
// imaging/merge-images
// Canonical: https://products.aspose.net/imaging/merge-images/
// Package: Aspose.Imaging 24.12.0
// Pattern: Create two BMP sources -> Create canvas -> Graphics.DrawImage -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "merged.png");

// Create first source BMP (left half)
var bmp1Opts = new BmpOptions { BitsPerPixel = 24 };
bmp1Opts.Source = new FileCreateSource(Path.Combine("output", "src1.bmp"), false);
using var img1 = Image.Create(bmp1Opts, 200, 150);
var g1 = new Aspose.Imaging.Graphics(img1);
g1.Clear(Aspose.Imaging.Color.SteelBlue);
g1.DrawString("Image 1", new Aspose.Imaging.Font("Arial", 16), new Aspose.Imaging.SolidBrush(Aspose.Imaging.Color.White), 40, 60);
img1.Save();

// Create second source BMP (right half)
var bmp2Opts = new BmpOptions { BitsPerPixel = 24 };
bmp2Opts.Source = new FileCreateSource(Path.Combine("output", "src2.bmp"), false);
using var img2 = Image.Create(bmp2Opts, 200, 150);
var g2 = new Aspose.Imaging.Graphics(img2);
g2.Clear(Aspose.Imaging.Color.Tomato);
g2.DrawString("Image 2", new Aspose.Imaging.Font("Arial", 16), new Aspose.Imaging.SolidBrush(Aspose.Imaging.Color.White), 40, 60);
img2.Save();

// Create merged canvas 400x150
var canvasOpts = new BmpOptions { BitsPerPixel = 24 };
canvasOpts.Source = new FileCreateSource(Path.Combine("output", "canvas.bmp"), false);
using var canvas = Image.Create(canvasOpts, 400, 150);
var gc = new Aspose.Imaging.Graphics(canvas);
gc.Clear(Aspose.Imaging.Color.White);
gc.DrawImage(img1, new Point(0, 0));
gc.DrawImage(img2, new Point(200, 0));
canvas.Save(outputPath, new PngOptions());

Console.WriteLine($"Merged image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",

"imaging/watermark-image": """\
// imaging/watermark-image
// Canonical: https://products.aspose.net/imaging/watermark-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: Create BMP -> Graphics.DrawString (diagonal watermark via Matrix transform) -> Save PNG
using Aspose.Imaging;
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

    // Base content
    gfx.DrawRectangle(new Aspose.Imaging.Pen(Aspose.Imaging.Color.SaddleBrown, 3), 20, 20, 360, 260);
    gfx.DrawString("Original Content", new Aspose.Imaging.Font("Arial", 20), new Aspose.Imaging.SolidBrush(Aspose.Imaging.Color.SaddleBrown), 90, 130);

    // Diagonal watermark using matrix rotation
    var watermarkBrush = new Aspose.Imaging.SolidBrush(Aspose.Imaging.Color.FromArgb(80, 128, 128, 128));
    var watermarkFont = new Aspose.Imaging.Font("Arial", 28, Aspose.Imaging.FontStyle.Bold);

    var matrix = new Aspose.Imaging.Matrix();
    matrix.Translate(200, 150);
    matrix.Rotate(-35f);
    gfx.Transform = matrix;

    var sf = new Aspose.Imaging.StringFormat { Alignment = Aspose.Imaging.StringAlignment.Center };
    gfx.DrawString("CONFIDENTIAL", watermarkFont, watermarkBrush, 0, 0, sf);

    gfx.ResetTransform();
    image.Save(outputPath, new PngOptions());
}

Console.WriteLine($"Watermarked image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",

"imaging/rotate-image": """\
// imaging/rotate-image
// Canonical: https://products.aspose.net/imaging/rotate-image/
// Package: Aspose.Imaging 24.12.0
// Pattern: Create BMP -> RasterImage.Rotate(angle) -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "rotated.png");

var bmpOptions = new BmpOptions { BitsPerPixel = 24 };
bmpOptions.Source = new FileCreateSource(Path.Combine("output", "source-rotate.bmp"), false);

using (var image = Image.Create(bmpOptions, 300, 200))
{
    var gfx = new Aspose.Imaging.Graphics(image);
    gfx.Clear(Aspose.Imaging.Color.LightCoral);

    // Draw an arrow-like shape to make rotation visible
    gfx.DrawRectangle(new Aspose.Imaging.Pen(Aspose.Imaging.Color.DarkRed, 3), 20, 20, 260, 160);
    gfx.DrawString("ROTATE ME", new Aspose.Imaging.Font("Arial", 22, Aspose.Imaging.FontStyle.Bold),
        new Aspose.Imaging.SolidBrush(Aspose.Imaging.Color.DarkRed), 55, 75);

    // Draw arrow
    var pen = new Aspose.Imaging.Pen(Aspose.Imaging.Color.DarkRed, 4);
    gfx.DrawLine(pen, 230, 90, 270, 90);
    gfx.DrawLine(pen, 255, 75, 270, 90);
    gfx.DrawLine(pen, 255, 105, 270, 90);

    image.Save();

    // Rotate 90 degrees clockwise
    var raster = (RasterImage)image;
    raster.Rotate(90f);
    raster.Save(outputPath, new PngOptions());
}

Console.WriteLine($"Rotated image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
""",

}


def main():
    loader = PluginCodeRegistryLoader().load()
    gen = ExamplePackageGenerator(DRYRUN_ROOT)
    DRYRUN_ROOT.mkdir(parents=True, exist_ok=True)

    results = []
    for key, program_cs in PROGRAMS.items():
        family, slug = key.split("/", 1)

        # Find registry entry
        families = loader.all_families()
        entry = None
        if family in families:
            for p in families[family].plugins:
                if p.plugin_slug == slug:
                    entry = p
                    break

        if entry is None:
            print(f"WARN: no registry entry for {key}, skipping")
            continue

        print(f"  Generating scaffold: {key}")
        pkg_dir = gen.generate_scaffold(entry, program_cs)
        results.append({"key": key, "pkg_dir": str(pkg_dir), "status": "SCAFFOLDED"})
        print(f"    -> {pkg_dir}")

    # Write generation manifest
    manifest_path = REPORT_ROOT / "dryrun" / "wave-a-generation-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({
        "sprint": "lowcode-plugin-example-factory-wave-20260605",
        "wave": "A",
        "generated_at": "2026-06-05",
        "packages": results
    }, indent=2))

    print(f"\nGenerated {len(results)} packages under {DRYRUN_ROOT}")
    print(f"Manifest: {manifest_path}")
    return results


if __name__ == "__main__":
    main()
