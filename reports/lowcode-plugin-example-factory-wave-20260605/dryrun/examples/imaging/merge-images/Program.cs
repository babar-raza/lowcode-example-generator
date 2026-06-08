// imaging/merge-images
// Canonical: https://products.aspose.net/imaging/merge-images/
// Package: Aspose.Imaging 24.12.0
// Pattern: Create two BMP sources -> Create canvas -> Graphics.DrawImage -> Save PNG
using Aspose.Imaging;
using Aspose.Imaging.Brushes;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.Sources;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "merged.png");

var bmp1Opts = new BmpOptions { BitsPerPixel = 24 };
bmp1Opts.Source = new FileCreateSource(Path.Combine("output", "src1.bmp"), false);
using var img1 = Image.Create(bmp1Opts, 200, 150);
var g1 = new Aspose.Imaging.Graphics(img1);
g1.Clear(Aspose.Imaging.Color.SteelBlue);
g1.FillRectangle(new SolidBrush(Aspose.Imaging.Color.White), new Rectangle(20, 20, 160, 110));
img1.Save();

var bmp2Opts = new BmpOptions { BitsPerPixel = 24 };
bmp2Opts.Source = new FileCreateSource(Path.Combine("output", "src2.bmp"), false);
using var img2 = Image.Create(bmp2Opts, 200, 150);
var g2 = new Aspose.Imaging.Graphics(img2);
g2.Clear(Aspose.Imaging.Color.Tomato);
g2.FillRectangle(new SolidBrush(Aspose.Imaging.Color.White), new Rectangle(20, 20, 160, 110));
img2.Save();

var canvasOpts = new BmpOptions { BitsPerPixel = 24 };
canvasOpts.Source = new FileCreateSource(Path.Combine("output", "canvas.bmp"), false);
using var canvas = Image.Create(canvasOpts, 400, 150);
var gc = new Aspose.Imaging.Graphics(canvas);
gc.Clear(Aspose.Imaging.Color.White);
gc.DrawImage(img1, new Point(0, 0));
gc.DrawImage(img2, new Point(200, 0));
canvas.Save(outputPath, new PngOptions());

Console.WriteLine($"Merged: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
