// Dry-run example: svg/svg-to-image-converter
// Canonical URL: https://products.aspose.net/svg/svg-to-image-converter/
// Package: Aspose.SVG 24.12.0
// Pattern: new SVGDocument(svgString, baseUri) → Converter.ConvertSVG(document, saveOptions, outputPath)

using Aspose.Svg;
using Aspose.Svg.Converters;
using Aspose.Svg.Rendering.Image;
using Aspose.Svg.Saving;
using System;
using System.IO;

string outputDir = "output";
Directory.CreateDirectory(outputDir);
string outputPath = Path.Combine(outputDir, "output.png");

string svgContent = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"200\" height=\"200\">"
    + "<rect width=\"200\" height=\"200\" fill=\"lightblue\"/>"
    + "<text x=\"50\" y=\"110\" font-size=\"24\" fill=\"navy\">SVG Example</text></svg>";

using var document = new SVGDocument(svgContent, ".");
var saveOptions = new ImageSaveOptions(ImageFormat.Png);
Converter.ConvertSVG(document, saveOptions, outputPath);

Console.WriteLine($"Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
