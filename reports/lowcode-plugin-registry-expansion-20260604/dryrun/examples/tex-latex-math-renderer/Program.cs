// Dry-run example: tex/latex-math-renderer
// Canonical URL: https://products.aspose.net/tex/latex-math-renderer/
// Package: Aspose.TeX 24.12.0
// Pattern: MathRendererPlugin.Process(PngMathRendererPluginOptions)
// Namespace: Aspose.TeX.Plugins

using Aspose.TeX.Plugins;
using System;
using System.IO;

string outputDir = "output";
Directory.CreateDirectory(outputDir);
string outputPath = Path.Combine(outputDir, "output_math.png");

var renderer = new MathRendererPlugin();
var options = new PngMathRendererPluginOptions
{
    Resolution = 150,
    Preamble = @"\usepackage{amsmath}"
};

// Inline LaTeX formula — no fixture file required
options.AddInputDataSource(new StringDataSource(@"$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$"));

using var outputStream = File.OpenWrite(outputPath);
options.AddOutputDataTarget(new StreamDataSource(outputStream));
renderer.Process(options);
outputStream.Flush();

Console.WriteLine($"Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
