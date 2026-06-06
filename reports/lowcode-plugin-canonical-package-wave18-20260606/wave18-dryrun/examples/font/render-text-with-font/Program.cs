// font/render-text-with-font — W18 canonical package proof
// Canonical URL: https://products.aspose.net/font/render-text-with-font/
// NuGet: Aspose.Font 24.12.0
// Pattern: Font.Open -> enumerate glyph IDs for text -> extract metrics -> save report
using System;
using System.IO;
using System.Collections.Generic;
using Aspose.Font;
using Aspose.Font.Glyphs;
using Aspose.Font.Sources;

Directory.CreateDirectory("output");

// Load Source Code Pro (OFL licensed, eval-mode safe)
string fontPath = Path.Combine("fixtures", "SourceCodePro-Regular.ttf");
if (!File.Exists(fontPath))
    throw new FileNotFoundException($"Font fixture not found: {fontPath}");

var fontDef = new FontDefinition(FontType.TTF,
    new FontFileDefinition("ttf", new FileSystemStreamSource(fontPath)));
var font = Font.Open(fontDef);

Console.WriteLine($"Font loaded: {font.FontFamily} {font.Style}");
Console.WriteLine($"Glyph count: {font.NumGlyphs}");

// Render text by resolving glyph IDs for each character
string sampleText = "Hello, Font!";
var glyphLines = new List<string>();
foreach (char ch in sampleText)
{
    uint codepoint = (uint)ch;
    var glyphId = font.Encoding.DecodeToGid(codepoint);
    glyphLines.Add($"U+{codepoint:X4} '{ch}' -> GID={glyphId?.ToString() ?? "N/A"}");
}

// Get glyph 'A' bounding metrics
var glyphIdA = font.Encoding.DecodeToGid((uint)'A');
string boundsReport = "N/A";
if (glyphIdA != null)
{
    var glyph = font.GetGlyphById(glyphIdA);
    if (glyph != null)
        boundsReport = $"WidthVectorX={glyph.WidthVectorX:F1}, LeftSidebearingX={glyph.LeftSidebearingX:F1}";
}

// Compose render report
string report =
    $"Font Family:    {font.FontFamily}\n" +
    $"Font Style:     {font.Style}\n" +
    $"Glyph Count:    {font.NumGlyphs}\n" +
    $"Units per Em:   {font.Metrics.UnitsPerEM}\n" +
    $"Ascender:       {font.Metrics.Ascender}\n" +
    $"Descender:      {font.Metrics.Descender}\n\n" +
    $"Glyph IDs for \"{sampleText}\":\n" +
    string.Join("\n", glyphLines) +
    $"\n\nGlyph 'A' metrics: {boundsReport}";

string reportPath = "output/render-report.txt";
File.WriteAllText(reportPath, report);
Console.WriteLine("\n" + report);
Console.WriteLine($"\nRender report saved: {reportPath}");
