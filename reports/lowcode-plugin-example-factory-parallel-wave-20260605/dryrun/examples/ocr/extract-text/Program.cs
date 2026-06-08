// ocr/extract-text
// Canonical: https://products.aspose.net/ocr/scanned-pdf-to-text/
// Package: Aspose.OCR 24.12.0
// Pattern: OcrInput(SingleImage) -> AsposeOcr.Recognize -> save extracted text
using Aspose.OCR;
using System;
using System.IO;

Directory.CreateDirectory("output");

// Write minimal fixture PNG
byte[] pngBytes = Convert.FromBase64String(
    "iVBORw0KGgoAAAANSUhEUgAAACgAAAAMCAYAAAAhMsU7AAAAH0lEQVR42mNk+M9QDwAD" +
    "hgGAWjR9awAAAABJRU5ErkJggg==");
string fixturePath = Path.GetFullPath("fixture.png");
File.WriteAllBytes(fixturePath, pngBytes);

var ocr = new AsposeOcr();
var input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
var results = ocr.Recognize(input);
string extracted = results.Count > 0 ? (results[0].RecognitionText ?? "") : "";
string report = $"Extracted text length: {extracted.Length}\nContent:\n{extracted}\n";
File.WriteAllText("output/extracted.txt", report);
Console.WriteLine($"Extracted {extracted.Length} chars. Saved to output/extracted.txt ({new FileInfo("output/extracted.txt").Length} bytes)");
