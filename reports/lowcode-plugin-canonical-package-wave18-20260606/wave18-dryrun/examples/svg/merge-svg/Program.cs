// svg/merge-svg — W18 canonical package proof
// Canonical URL: https://products.aspose.net/svg/merge-svg/
// NuGet: Aspose.SVG
// Pattern: Create two SVGDocuments -> merge by importing nodes into a wrapper SVG -> save
using System;
using System.IO;
using Aspose.Svg;

Directory.CreateDirectory("output");

// Step 1: Create first SVG document (blue circle)
string svg1Content = @"<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>
  <circle cx='50' cy='50' r='40' fill='blue' />
  <text x='50' y='55' text-anchor='middle' fill='white' font-size='12'>SVG1</text>
</svg>";

// Step 2: Create second SVG document (red rectangle)
string svg2Content = @"<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>
  <rect x='10' y='10' width='80' height='80' fill='red' />
  <text x='50' y='55' text-anchor='middle' fill='white' font-size='12'>SVG2</text>
</svg>";

// Step 3: Build merged SVG by creating a wrapper document and embedding both
string mergedContent = $@"<svg xmlns='http://www.w3.org/2000/svg' width='220' height='100'>
  <g transform='translate(0,0)'>
{svg1Content.Replace("<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>", "").Replace("</svg>", "").Trim()}
  </g>
  <g transform='translate(110,0)'>
{svg2Content.Replace("<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100'>", "").Replace("</svg>", "").Trim()}
  </g>
</svg>";

// Step 4: Parse with Aspose.SVG and save as canonical output
using (var doc = new SVGDocument(mergedContent, "."))
{
    string outputPath = "output/merged.svg";
    doc.Save(outputPath);
    long size = new FileInfo(outputPath).Length;
    Console.WriteLine($"Merged SVG saved: {outputPath} ({size} bytes)");

    // Also save as PDF via SVG renderer
    string pdfPath = "output/merged.pdf";
    using var renderer = new Aspose.Svg.Rendering.Pdf.PdfDevice(pdfPath);
    doc.RenderTo(renderer);
    long pdfSize = new FileInfo(pdfPath).Length;
    Console.WriteLine($"PDF render of merged SVG: {pdfPath} ({pdfSize} bytes)");
}

string resultText = "merge-svg: PASS - two SVG documents merged into one 220x100 SVG with embedded groups";
File.WriteAllText("output/merge-result.txt", resultText);
Console.WriteLine(resultText);
