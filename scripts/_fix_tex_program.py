"""Fix tex/latex-figure-renderer Program.cs with correct API and verbatim strings."""
import pathlib

p = pathlib.Path(__file__).parents[1] / "reports" / "lowcode-plugin-example-factory-wave-20260605" / "dryrun" / "examples" / "tex" / "latex-figure-renderer" / "Program.cs"

lines = [
    '// tex/latex-figure-renderer',
    '// Canonical: https://products.aspose.net/tex/latex-figure-renderer/',
    '// Package: Aspose.TeX 24.12.0',
    '// Pattern: FigureRendererPlugin + PngFigureRendererPluginOptions -> Process',
    'using Aspose.TeX.Plugins;',
    'using System;',
    'using System.IO;',
    '',
    'Directory.CreateDirectory("output");',
    'string outputPath = Path.Combine("output", "figure.png");',
    '',
    '// TikZ figure: coordinate axes',
    'string tikzFigure =',
    '    @"\\begin{tikzpicture}" +',
    '    @"\\draw[thick,->] (0,0) -- (3,0) node[right] {$x$};" +',
    '    @"\\draw[thick,->] (0,0) -- (0,2.5) node[above] {$y$};" +',
    '    @"\\draw[blue,thick] (0,0) -- (2.8,1.96);" +',
    '    @"\\end{tikzpicture}";',
    '',
    'var plugin = new FigureRendererPlugin();',
    'var options = new PngFigureRendererPluginOptions',
    '{',
    '    Resolution = 150,',
    '    Margin = 10f,',
    '    Preamble = @"\\usepackage{tikz}"',
    '};',
    'options.AddInputDataSource(new StringDataSource(tikzFigure));',
    '',
    'using var outStream = File.Open(outputPath, FileMode.Create);',
    'options.AddOutputDataTarget(new StreamDataSource(outStream));',
    '',
    'plugin.Process(options);',
    'outStream.Flush();',
    '',
    'Console.WriteLine($"Figure rendered: {outputPath} ({new FileInfo(outputPath).Length} bytes)");',
]

p.write_text('\n'.join(lines) + '\n', encoding='utf-8')

# Verify
content = p.read_text(encoding='utf-8')
for lineno, line in enumerate(content.splitlines(), 1):
    if 'begin' in line or 'draw' in line or 'end' in line or 'usepackage' in line:
        print(f"L{lineno}: {line}")
print("Done.")
