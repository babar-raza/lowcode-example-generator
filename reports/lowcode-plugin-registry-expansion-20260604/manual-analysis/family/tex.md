# Manual Family Analysis: tex
## Sprint: lowcode-plugin-registry-expansion-20260604 | Date: 2026-06-04
## Evidence: https://products.aspose.net/tex/ (2 canonical pages) + LaTeXPdfConversionAlternative.cs

### Implementation Model: DEDICATED_PLUGIN_CLASS
TeX uses dedicated renderer plugin classes: `FigureRendererPlugin`, `MathRendererPlugin`.
Pattern: instantiate plugin → configure options (with LaTeX source string) → call `.Process()`.
This is NOT the TeXJob/TeXOptions pattern (which is the traditional TeX compilation path).

### API Pattern
```csharp
// Render LaTeX figure to PNG
var renderer = new FigureRendererPlugin();
var options = new PngFigureRendererPluginOptions() {
    BackgroundColor = Color.White,
    Resolution = 150,
    Margin = 10
};
options.AddInputDataSource(new StringDataSource(@"\begin{tikzpicture}...\end{tikzpicture}"));
options.AddOutputDataTarget(new StreamDataTarget(outputStream));
renderer.Process(options);

// Render LaTeX math formula to PNG
var renderer = new MathRendererPlugin();
var options = new PngMathRendererPluginOptions() {
    BackgroundColor = Color.White,
    Resolution = 150,
    Preamble = @"\usepackage{amsmath}"
};
options.AddInputDataSource(new StringDataSource(@"$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$"));
options.AddOutputDataTarget(new StreamDataTarget(outputStream));
renderer.Process(options);
```

### 2 Canonical Pages (new-URL pattern)
- latex-figure-renderer — render LaTeX figure/tikz to PNG/SVG (DEDICATED_PLUGIN_CLASS, FigureRendererPlugin.Process())
- latex-math-renderer — render LaTeX math formula to PNG/SVG (DEDICATED_PLUGIN_CLASS, MathRendererPlugin.Process())

### Fixture Requirements
- latex-figure-renderer: NO file fixture needed — LaTeX source is a string parameter in options
- latex-math-renderer: NO file fixture needed — math formula is a string parameter in options
- Both can run fully in-memory, making these ideal for dry-run packages

### Transformation Priority: HIGH
- No file fixture needed — lowest barrier of all families
- LaTeX string can be hardcoded inline in the example
- Both entries READY_FOR_TRANSFORMATION
- Package: Aspose.TeX for .NET (NuGet: Aspose.TeX)
