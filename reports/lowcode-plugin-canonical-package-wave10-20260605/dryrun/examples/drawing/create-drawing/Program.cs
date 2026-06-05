// drawing/create-drawing
// Canonical: https://products.aspose.net/drawing/net/create-drawing/
// Package: Aspose.Drawing 24.12.0
// Note: Aspose.Drawing provides System.Drawing compatibility layer
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "drawing.png");

using (var bmp = new Bitmap(400, 250))
using (var g = Graphics.FromImage(bmp))
{
    g.Clear(Color.FromArgb(240, 248, 255));
    g.FillRectangle(new SolidBrush(Color.FromArgb(42, 106, 210)), 0, 0, 400, 50);
    g.FillEllipse(new SolidBrush(Color.FromArgb(200, 255, 165, 0)), 30, 80, 80, 80);
    g.FillRectangle(new SolidBrush(Color.FromArgb(200, 60, 179, 113)), 150, 80, 80, 80);
    g.DrawPolygon(new Pen(Color.DarkRed, 2), new Point[]
    {
        new Point(290, 80), new Point(330, 160), new Point(250, 160)
    });
    bmp.Save(outputPath, ImageFormat.Png);
}

long size = new FileInfo(outputPath).Length;
Console.WriteLine($"Drawing created: {outputPath} ({size} bytes)");
