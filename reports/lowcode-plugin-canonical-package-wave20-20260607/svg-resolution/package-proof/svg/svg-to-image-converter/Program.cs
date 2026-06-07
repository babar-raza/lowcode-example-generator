// svg/svg-to-image-converter
// Canonical: https://products.aspose.net/svg/svg-to-image-converter/
// Package: Aspose.SVG 24.12.0
// Pattern: SVGDocument -> Converter.ConvertSVG(doc, ImageSaveOptions(PNG), outputPath)
using Aspose.Svg;
using Aspose.Svg.Converters;
using Aspose.Svg.Saving;
using Aspose.Svg.Rendering.Image;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.png");

string svgContent =
    @"<svg xmlns=""http://www.w3.org/2000/svg"" width=""400"" height=""300"">" +
    @"<rect width=""400"" height=""300"" fill=""#f0f8ff""/>" +
    @"<rect x=""20"" y=""20"" width=""360"" height=""260"" rx=""15"" fill=""#4a90d9"" opacity=""0.85""/>" +
    @"<circle cx=""200"" cy=""130"" r=""60"" fill=""white"" opacity=""0.9""/>" +
    @"<text x=""200"" y=""140"" text-anchor=""middle"" font-size=""28"" fill=""#4a90d9"" font-family=""Arial"">SVG</text>" +
    @"<text x=""200"" y=""250"" text-anchor=""middle"" font-size=""16"" fill=""white"">Image Converter</text>" +
    @"</svg>";

using var document = new SVGDocument(svgContent, ".");
var imageOptions = new ImageSaveOptions(ImageFormat.Png);
Converter.ConvertSVG(document, imageOptions, outputPath);
Console.WriteLine($"PNG saved: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
