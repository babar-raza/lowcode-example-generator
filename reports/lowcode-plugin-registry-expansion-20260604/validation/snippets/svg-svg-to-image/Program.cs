// Snippet validation: svg/svg-to-image-converter
// Source: https://products.aspose.net/svg/svg-to-image-converter/
// Official code: ConvertSVGToImage.cs (aspose-svg/Aspose.SVG-for-.NET)
// Pattern: Converter.ConvertSVG(document, new ImageSaveOptions(ImageFormat.Png), outputPath)

using Aspose.Svg;
using Aspose.Svg.Converters;
using Aspose.Svg.Saving;
using Aspose.Svg.Rendering.Image;
using System;
using System.IO;

string outputDir = "output";
Directory.CreateDirectory(outputDir);
string outputPath = Path.Combine(outputDir, "output.png");

// Inline SVG — no fixture file required
string svgContent = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"200\" height=\"200\"><rect width=\"200\" height=\"200\" fill=\"lightblue\"/><text x=\"50\" y=\"110\" font-size=\"24\" fill=\"navy\">SVG Test</text></svg>";

using var document = new SVGDocument(svgContent, ".");
var saveOptions = new ImageSaveOptions(ImageFormat.Png);
Converter.ConvertSVG(document, saveOptions, outputPath);

bool exists = File.Exists(outputPath);
long size = exists ? new FileInfo(outputPath).Length : 0;
Console.WriteLine($"OUTPUT_FILE={outputPath}");
Console.WriteLine($"FILE_EXISTS={exists}");
Console.WriteLine($"FILE_SIZE_BYTES={size}");
Console.WriteLine(exists && size > 100 ? "VALIDATION=PASS" : "VALIDATION=FAIL");
