// Aspose.Font probe — convert-font (TTF → save, Montserrat)
// Pilot: TRAIN F - font family, Plugin 1
// PR-01: Aspose.Font.Font confirmed by DllReflector (125 types)
// PR-02: Font.Open(FontDefinition) + Font.Save(string) confirmed
// PR-03: Font abstract class with static Open factory + instance Save method
// PR-04: FontType.TTF confirmed; FontDefinition+FileSystemStreamSource pattern
// Note: trial mode requires one of: Montserrat, Noto Sans JP, Merriweather, Lora, Source Code Pro
using Aspose.Font;
using Aspose.Font.Sources;
using System.IO;

var outputPath = args.Length > 0 ? args[0] : "output.ttf";

// Montserrat-Regular.ttf is available in ExampleReviewer workspaces (free font)
var montserratPath = @"C:\Users\prora\AppData\Local\ExampleReviewer\workspaces\20260305_055117\workspace\runtime\runtime_0e026229f8f8cd38\Fonts\Montserrat-Regular.ttf";
if (!File.Exists(montserratPath))
{
    Console.Error.WriteLine($"Montserrat font not found at: {montserratPath}");
    return 1;
}

Console.WriteLine($"Using font: {montserratPath}");

// Load Montserrat TTF font
var fontDefinition = new FontDefinition(FontType.TTF, new FileSystemStreamSource(montserratPath));
var font = Font.Open(fontDefinition);

Console.WriteLine($"Loaded font: {font.FontName}");
Console.WriteLine($"Font type: {font.FontType}");
Console.WriteLine($"Num glyphs: {font.NumGlyphs}");
Console.WriteLine($"Font family: {font.FontFamily}");

// Save the font (copy to output path — demonstrates Font.Save API)
font.Save(outputPath);

var size = new FileInfo(outputPath).Length;
Console.WriteLine($"Saved font to: {outputPath} ({size} bytes)");
return 0;
