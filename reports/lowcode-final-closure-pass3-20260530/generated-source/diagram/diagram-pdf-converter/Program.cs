using System;
using System.IO;
using Aspose.Diagram;
using Aspose.Diagram.LowCode;

var inputPath = "input.vsdx";
var diagram = new Diagram();
var page = diagram.Pages[0];
long shapeId = page.DrawEllipse(1.0, 1.0, 2.0, 2.0);
var shape = page.Shapes.GetShape(shapeId);
if (shape != null)
{
    shape.Name = "SampleShape";
    shape.XForm.PinX.Value = 2.0;
    shape.XForm.PinY.Value = 2.0;
    shape.XForm.Width.Value = 1.0;
    shape.XForm.Height.Value = 1.0;
}
diagram.Save(inputPath, SaveFileFormat.Vsdx);

var outputPath = "output.pdf";
PdfConverter.Process(inputPath, outputPath);

Console.WriteLine(File.Exists(outputPath)
    ? $"PDF generated successfully: {outputPath}"
    : $"PDF conversion failed, output not found at '{outputPath}'.");
