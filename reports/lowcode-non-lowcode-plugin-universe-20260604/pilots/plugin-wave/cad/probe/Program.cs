// Aspose.CAD probe — convert-cad-to-pdf
// Pilot: TRAIN F - cad family, Plugin 1
// PR-01: Aspose.CAD.Image confirmed by DllReflector (5028 types)
// PR-02: Image.Save(string, ImageOptionsBase) confirmed
// PR-03: Image has static Load method and instance Save
// PR-04: PdfOptions enum confirmed in CAD namespace
using Aspose.CAD;
using Aspose.CAD.ImageOptions;
using System.IO;

var outputPath = args.Length > 0 ? args[0] : "output.pdf";

// Create minimal DXF content in memory (no file needed)
var dxfContent = @"0
SECTION
2
HEADER
9
$ACADVER
1
AC1009
0
ENDSEC
0
SECTION
2
ENTITIES
0
LINE
8
0
10
0.0
20
0.0
30
0.0
11
100.0
21
100.0
31
0.0
0
ENDSEC
0
EOF
";

// Write minimal DXF to temp file
var tempDxf = Path.Combine(Path.GetTempPath(), "probe_minimal.dxf");
File.WriteAllText(tempDxf, dxfContent);

try
{
    using var cadImage = Image.Load(tempDxf);
    var pdfOptions = new PdfOptions();
    var rasterOptions = new CadRasterizationOptions
    {
        PageWidth = 1200,
        PageHeight = 1200
    };
    pdfOptions.VectorRasterizationOptions = rasterOptions;
    cadImage.Save(outputPath, pdfOptions);
    Console.WriteLine($"CAD probe: Saved PDF to {outputPath}");
    Console.WriteLine($"Output size: {new FileInfo(outputPath).Length} bytes");
}
finally
{
    if (File.Exists(tempDxf)) File.Delete(tempDxf);
}
