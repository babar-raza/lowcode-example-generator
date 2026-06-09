using Aspose.OCR;
using System.Drawing;
using System.Drawing.Imaging;

Console.WriteLine("Aspose.OCR - Document Scanner");
// Create a test image with text
using var bmp = new Bitmap(200, 50);
using var g = Graphics.FromImage(bmp);
g.Clear(Color.White);
g.DrawString("Hello OCR", new Font("Arial", 14), Brushes.Black, 10, 10);
bmp.Save("test-input.png", ImageFormat.Png);

var api = new AsposeOcr();
var result = api.RecognizeImage("test-input.png");
Console.WriteLine($"OCR result: {result}");
File.WriteAllText("output.txt", result);
Console.WriteLine("Document scanned successfully: output.txt");
