// Snippet validation: tex/latex-math-renderer
// Source: https://products.aspose.net/tex/latex-math-renderer/
// Pattern: MathRendererPlugin.Process(PngMathRendererPluginOptions)
// No file fixture required — LaTeX formula is an inline string

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

// Inline LaTeX math formula — no fixture file required
options.AddInputDataSource(new StringDataSource(@"$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$"));

using var outputStream = File.OpenWrite(outputPath);
options.AddOutputDataTarget(new StreamDataSource(outputStream));

renderer.Process(options);
outputStream.Flush();

bool exists = File.Exists(outputPath);
long size = exists ? new FileInfo(outputPath).Length : 0;
Console.WriteLine($"OUTPUT_FILE={outputPath}");
Console.WriteLine($"FILE_EXISTS={exists}");
Console.WriteLine($"FILE_SIZE_BYTES={size}");
Console.WriteLine(exists && size > 100 ? "VALIDATION=PASS" : "VALIDATION=FAIL");
