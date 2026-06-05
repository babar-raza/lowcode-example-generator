// ocr/scan-document
// Canonical: https://products.aspose.net/ocr/scan-document/
// Package: Aspose.OCR 24.12.0
// Pattern: OcrInput(SingleImage) -> AsposeOcr.Recognize -> save text result
using Aspose.OCR;
using System;
using System.IO;

Directory.CreateDirectory("output");

// Embed minimal fixture PNG (40x12 white image)
byte[] pngBytes = Convert.FromBase64String(
    "iVBORw0KGgoAAAANSUhEUgAAACgAAAAMCAYAAAAhMsU7AAAAH0lEQVR42mNk+M9QDwAD" +
    "hgGAWjR9awAAAABJRU5ErkJggg==");
string fixturePath = Path.GetFullPath("fixture.png");
File.WriteAllBytes(fixturePath, pngBytes);

var ocr = new AsposeOcr();
var input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
var results = ocr.Recognize(input);
string text = results.Count > 0 ? (results[0].RecognitionText ?? "") : "";
string outputText = $"Scanned document result ({text.Length} chars):\n{text}\nFixture: {fixturePath}\nScanned at: {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC";
File.WriteAllText("output/scanned.txt", outputText);
Console.WriteLine($"Scanned: '{text.Trim().Replace("\n", " ")}'");
Console.WriteLine($"Saved: output/scanned.txt ({new FileInfo("output/scanned.txt").Length} bytes)");
