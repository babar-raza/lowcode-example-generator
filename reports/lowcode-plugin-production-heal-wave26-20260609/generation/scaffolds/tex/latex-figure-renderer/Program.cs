using Aspose.TeX;
using Aspose.TeX.IO;
using Aspose.TeX.Presentation.Image;

Console.WriteLine("Aspose.TeX - LaTeX Figure Renderer");
var options = new TeXOptions(TeXConfig.ObjectLaTeX);
options.OutputWorkingDirectory = new OutputFileSystemDirectory(".");
options.SaveOptions = new PngSaveOptions();
Console.WriteLine("TeX engine configured.");
File.WriteAllText("output.txt", "LaTeX figure renderer scaffold complete.");
Console.WriteLine("LaTeX figure renderer scaffold complete: output.txt");
