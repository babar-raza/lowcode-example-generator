using System.Drawing;
using System.Drawing.Imaging;

Console.WriteLine("Aspose.Drawing - Create Drawing");
using var bmp = new Bitmap(200, 200);
using var g = Graphics.FromImage(bmp);
g.Clear(Color.LightBlue);
g.FillEllipse(Brushes.Red, 50, 50, 100, 100);
g.DrawString("Hello", new Font("Arial", 12), Brushes.Black, 10, 10);
bmp.Save("output.png", ImageFormat.Png);
Console.WriteLine("Drawing created successfully: output.png");
