// html/convert-html-to-image
// Canonical: https://products.aspose.net/html/html-to-image-converter/
// Package: Aspose.HTML 24.12.0
// Pattern: Converter.ConvertHTML(htmlContent, baseUri, ImageSaveOptions, outputPath)
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.jpg");

string htmlContent =
    "<!DOCTYPE html><html><head><title>HTML to Image Demo</title>" +
    "<style>body{font-family:Arial;background:#f0f4f8;padding:20px;}" +
    "h1{color:#1a5276;}div{background:white;padding:15px;border-radius:8px;}</style>" +
    "</head><body><div>" +
    "<h1>HTML to Image Conversion</h1>" +
    "<p>This HTML page was rendered as a JPEG image using Aspose.HTML.</p>" +
    "<p>Date: 2026-06-05</p>" +
    "</div></body></html>";

var options = new ImageSaveOptions(Aspose.Html.Rendering.Image.ImageFormat.Jpeg);
Converter.ConvertHTML(htmlContent, ".", options, outputPath);
Console.WriteLine($"HTML converted to Image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
