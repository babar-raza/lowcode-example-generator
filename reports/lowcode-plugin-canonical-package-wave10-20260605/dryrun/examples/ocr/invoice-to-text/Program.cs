// ocr/invoice-to-text
// Canonical: https://products.aspose.net/ocr/invoice-to-text/
// Package: Aspose.OCR 24.12.0
// Pattern: OcrInput(SingleImage) -> AsposeOcr.Recognize -> extract invoice data
using Aspose.OCR;
using System;
using System.IO;

Directory.CreateDirectory("output");
string fixturePath = Path.GetFullPath("fixture.png");
string outputPath = Path.Combine("output", "invoice-data.txt");

// Write minimal PNG fixture as base64
byte[] pngBytes = Convert.FromBase64String(
    "iVBORw0KGgoAAAANSUhEUgAAACgAAAAMCAYAAAAhMsU7AAAAH0lEQVR42mNk+M9QDwAD" +
    "hgGAWjR9awAAAABJRU5ErkJggg==");
File.WriteAllBytes(fixturePath, pngBytes);

var api = new AsposeOcr();
var input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
var results = api.Recognize(input);
string text = results.Count > 0 ? (results[0].RecognitionText ?? "") : "";
string invoiceData = $"invoice-to-text extraction ({text.Length} chars):\n{text}";
File.WriteAllText(outputPath, invoiceData);
Console.WriteLine($"Invoice OCR: {outputPath} ({text.Length} chars)");
