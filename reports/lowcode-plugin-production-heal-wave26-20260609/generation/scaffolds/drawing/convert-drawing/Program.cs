using System.Drawing;
using System.Drawing.Imaging;

Console.WriteLine("Aspose.Drawing - Convert Drawing");
using var bmp = new Bitmap(100, 100);
using var g = Graphics.FromImage(bmp);
g.Clear(Color.White);
g.DrawRectangle(Pens.Black, 10, 10, 80, 80);
bmp.Save("output.png", ImageFormat.Png);
Console.WriteLine("Drawing converted successfully: output.png");
