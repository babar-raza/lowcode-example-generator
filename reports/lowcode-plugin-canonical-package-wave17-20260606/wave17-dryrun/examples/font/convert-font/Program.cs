using System;
using System.IO;
using Aspose.Font;
using Aspose.Font.Sources;

Directory.CreateDirectory("output");

// Load Source Code Pro TTF (allowed in Aspose.Font evaluation mode)
string fontPath = Path.Combine("output", "SourceCodePro-Regular.ttf");
var fontDef = new FontDefinition(FontType.TTF,
    new FontFileDefinition("ttf", new FileSystemStreamSource(fontPath)));
var font = Font.Open(fontDef);

// Write font metadata to output
string info = $"Family: {font.FontFamily}\nStyle: {font.Style}\nGlyphs: {font.NumGlyphs}";
File.WriteAllText("output/font-info.txt", info);
Console.WriteLine("Font loaded and metadata extracted successfully.");
Console.WriteLine(info);
