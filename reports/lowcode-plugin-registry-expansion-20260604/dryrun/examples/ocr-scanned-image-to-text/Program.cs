// Dry-run example: ocr/scanned-image-to-text
// Canonical URL: https://products.aspose.net/ocr/scanned-image-to-text/
// Package: Aspose.OCR 24.12.0
// Pattern: AsposeOcr + OcrInput(InputType.SingleImage) + api.Recognize()

using Aspose.OCR;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

string outputDir = "output";
Directory.CreateDirectory(outputDir);

// Generate minimal test PNG fixture with System.Drawing
string fixturePath = Path.Combine(outputDir, "test_image.png");
using (var bmp = new Bitmap(400, 100))
using (var g = Graphics.FromImage(bmp))
{
    g.Clear(Color.White);
    g.DrawString("Hello Aspose OCR Example", new Font("Arial", 20), Brushes.Black, 10, 30);
    bmp.Save(fixturePath, ImageFormat.Png);
}

// Recognize text from image
AsposeOcr api = new AsposeOcr();
OcrInput input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
List<RecognitionResult> result = api.Recognize(input);

string text = result.Count > 0 ? result[0].RecognitionText : "(no text)";
string outputTextPath = Path.Combine(outputDir, "output_text.txt");
File.WriteAllText(outputTextPath, text);

Console.WriteLine($"Recognized: {text.Trim().Substring(0, Math.Min(60, text.Trim().Length))}...");
Console.WriteLine($"Output: {outputTextPath}");
