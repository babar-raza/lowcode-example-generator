using Aspose.OCR;
using System.Drawing;
using System.Drawing.Imaging;

Console.WriteLine("Aspose.OCR - Image Text Finder");
using var bmp = new Bitmap(200, 50);
using var g = Graphics.FromImage(bmp);
g.Clear(Color.White);
g.DrawString("Sample Text", new Font("Arial", 14), Brushes.Black, 10, 10);
bmp.Save("test-input.png", ImageFormat.Png);

var api = new AsposeOcr();
var result = api.RecognizeImage("test-input.png");
Console.WriteLine($"Found text: {result}");
File.WriteAllText("output.txt", result);
Console.WriteLine("Text found successfully: output.txt");
