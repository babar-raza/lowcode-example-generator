// Source: https://raw.githubusercontent.com/aspose-svg/Aspose.SVG-for-.NET/master/Examples/CSharp/LoadSaveConvert/ConvertSVGToImage.cs
// Fetched: 2026-06-04 | Sprint: lowcode-plugin-registry-expansion-20260604

// CORE PATTERN (using Converter.ConvertSVG static method):
// var code = "<svg ...>...</svg>";
// File.WriteAllText("example.svg", code);
// using var document = new SVGDocument("example.svg");
// var saveOptions = new Aspose.Svg.Saving.ImageSaveOptions(ImageFormat.Png);
// Aspose.Svg.Converters.Converter.ConvertSVG(document, saveOptions, "output.png");

// ALTERNATIVE (using ImageDevice/SVGDocument.RenderTo):
// using var document = new SVGDocument("paths.svg");
// using var device = new ImageDevice(new ImageRenderingOptions(ImageFormat.Png), "output.png");
// document.RenderTo(device);

using Aspose.Svg;
using Aspose.Svg.Rendering.Image;
using System.IO;

public class ConvertSVGToImage {
    public static void Run() {
        var code = "<svg xmlns='http://www.w3.org/2000/svg'><circle cx='50' cy='50' r='40' fill='red'/></svg>";
        File.WriteAllText("example.svg", code);
        using var document = new SVGDocument("example.svg");
        var saveOptions = new Aspose.Svg.Saving.ImageSaveOptions(ImageFormat.Png);
        Aspose.Svg.Converters.Converter.ConvertSVG(document, saveOptions, "output.png");
    }
}
