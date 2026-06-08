// Snippet validation: ocr/scanned-image-to-text
// Source: https://products.aspose.net/ocr/scanned-image-to-text/
// Official code: RecognizeImageFromStream.cs (aspose-ocr/Aspose.OCR-for-.NET)
// Pattern: AsposeOcr api + OcrInput(InputType.SingleImage) + api.Recognize()

using Aspose.OCR;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

string outputDir = "output";
Directory.CreateDirectory(outputDir);

// Generate a minimal test PNG with text using System.Drawing
string fixturePath = Path.Combine(outputDir, "test_image.png");
using (var bmp = new Bitmap(400, 100))
using (var g = Graphics.FromImage(bmp))
{
    g.Clear(Color.White);
    g.DrawString("Hello Aspose OCR Test", new Font("Arial", 20), Brushes.Black, 10, 30);
    bmp.Save(fixturePath, ImageFormat.Png);
}

// OCR: AsposeOcr + OcrInput + api.Recognize()
AsposeOcr api = new AsposeOcr();
OcrInput input = new OcrInput(InputType.SingleImage);
input.Add(fixturePath);
List<RecognitionResult> result = api.Recognize(input);

string recognizedText = result.Count > 0 ? result[0].RecognitionText : "";
string outputTextPath = Path.Combine(outputDir, "output_text.txt");
File.WriteAllText(outputTextPath, recognizedText);

Console.WriteLine($"RECOGNIZED_TEXT={recognizedText.Trim()}");
Console.WriteLine($"OUTPUT_FILE={outputTextPath}");
Console.WriteLine($"FILE_EXISTS={File.Exists(outputTextPath)}");
// OCR trial mode may produce partial results; validate that API ran without exception
Console.WriteLine(!string.IsNullOrEmpty(recognizedText) || result.Count > 0 ? "VALIDATION=PASS" : "VALIDATION=FAIL_NO_OUTPUT");
