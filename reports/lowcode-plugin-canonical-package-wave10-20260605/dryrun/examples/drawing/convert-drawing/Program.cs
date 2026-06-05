// drawing/convert-drawing
// Canonical: https://products.aspose.net/drawing/net/convert-drawing/
// Package: Aspose.Drawing 24.12.0
// Note: Aspose.Drawing provides System.Drawing compatibility layer
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "converted.png");

using (var bmp = new Bitmap(300, 200))
using (var g = Graphics.FromImage(bmp))
{
    g.Clear(Color.WhiteSmoke);
    g.FillRectangle(new SolidBrush(Color.SteelBlue), 20, 20, 260, 160);
    g.DrawRectangle(new Pen(Color.DarkBlue, 3), 20, 20, 260, 160);
    g.DrawLine(new Pen(Color.White, 2), 20, 20, 280, 180);
    g.DrawLine(new Pen(Color.White, 2), 280, 20, 20, 180);
    g.DrawEllipse(new Pen(Color.Gold, 2), 100, 60, 100, 80);
    bmp.Save(outputPath, ImageFormat.Png);
}

long size = new FileInfo(outputPath).Length;
Console.WriteLine($"Drawing converted: {outputPath} ({size} bytes)");
