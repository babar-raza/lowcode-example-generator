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
    @"<svg xmlns=""http://www.w3.org/2000/svg"" width=""400"" height=""200"">" +
    @"<rect width=""400"" height=""200"" fill=""#f0f4ff""/>" +
    @"<rect x=""20"" y=""20"" width=""360"" height=""160"" rx=""10"" fill=""#4a90d9"" opacity=""0.8""/>" +
    @"<text x=""200"" y=""115"" text-anchor=""middle"" font-size=""32"" fill=""white"" font-family=""Arial"">SVG to PDF</text>" +
    @"</svg>";

using var document = new SVGDocument(svgContent, ".");
var pdfOptions = new PdfSaveOptions();
Converter.ConvertSVG(document, pdfOptions, outputPath);

Console.WriteLine($"PDF saved: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
