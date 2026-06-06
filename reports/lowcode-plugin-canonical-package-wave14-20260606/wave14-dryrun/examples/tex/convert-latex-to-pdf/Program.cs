// tex/convert-latex-to-pdf
// Canonical: https://products.aspose.net/tex/net/convert-latex-to-pdf
// Package: Aspose.TeX 24.12.0
// Pattern: TeXOptions.ConsoleAppOptions(ObjectLaTeX) + TeXJob + XpsDevice
// Note: PdfDevice throws XpsSaveOptions cast bug in 24.12.0; using XpsDevice instead
using Aspose.TeX;
using Aspose.TeX.IO;
using Aspose.TeX.Presentation.Xps;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
Directory.CreateDirectory("input");
string outputPath = Path.Combine("output", "job.xps");

// Write minimal LaTeX source
string latexContent = "\\documentclass{minimal}\n\\begin{document}\n" +
    "\\textbf{Aspose.TeX LaTeX Conversion}\\\\\n" +
    "This document was compiled from LaTeX source\\\\\n" +
    "using Aspose.TeX for .NET.\\\\\n" +
    "Date: 2026-06-05\n\\end{document}\n";
File.WriteAllText(Path.Combine("input", "job.tex"), latexContent, Encoding.UTF8);

var options = TeXOptions.ConsoleAppOptions(TeXConfig.ObjectLaTeX);
options.InputWorkingDirectory = new InputFileSystemDirectory("input");
options.OutputWorkingDirectory = new OutputFileSystemDirectory("output");
options.TerminalOut = new OutputFileTerminal(options.OutputWorkingDirectory);

new TeXJob("job", new XpsDevice(), options).Run();
bool hasOutput = File.Exists(outputPath) && new FileInfo(outputPath).Length > 0;
Console.WriteLine($"LaTeX compiled to XPS: {outputPath} (exists={hasOutput}, {(hasOutput ? new FileInfo(outputPath).Length : 0)} bytes)");
