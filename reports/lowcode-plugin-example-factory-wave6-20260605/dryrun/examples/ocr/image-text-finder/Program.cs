// ocr/image-text-finder
// Canonical: https://products.aspose.net/ocr/image-text-finder/
// Package: Aspose.OCR 24.12.0
// Pattern: OcrInput(SingleImage) -> AsposeOcr.Recognize -> extract text
using Aspose.OCR;
using System;
using System.IO;

Directory.CreateDirectory("output");
string fixturePath = Path.GetFullPath("fixture.png");
string outputPath = Path.Combine("output", "found-text.txt");

// Write minimal PNG fixture (40x12 white image) as base64
byte[] pngBytes = Convert.FromBase64String(
    "iVBORw0KGgoAAAANSUhEUgAAACgAAAAMCAYAAAAhMsU7AAAAH0lEQVR42mNk+M9QDwAD" +
    "hgGAWjR9awAAAABJRU5ErkJggg==");
File.WriteAllBytes(fixturePath, pngBytes);

var api = new AsposeOcr();
var input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
var results = api.Recognize(input);
string text = results.Count > 0 ? (results[0].RecognitionText ?? "") : "";
string output = $"image-text-finder result ({text.Length} chars):\n{text}";
File.WriteAllText(outputPath, output);
Console.WriteLine($"Image text found: {outputPath} ({text.Length} chars recognized)");
