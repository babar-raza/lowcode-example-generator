// omr/generate-omr-template — W18 probe
// NuGet: Aspose.OMR
using System;
using System.IO;
using Aspose.OMR.Api;
using Aspose.OMR.Generation;

Directory.CreateDirectory("output");

var api = new OmrEngine();

// Build a minimal OMR template markup
string markup = @"
?text=Wave18 OMR Test Template
?empty_line=

?answer_sheet=Questions
  elements_count=5
  columns_count=4
  answers_count=4
?end

?text=Answer key below
";

try
{
    var result = api.GenerateTemplate(new MemoryStream(System.Text.Encoding.UTF8.GetBytes(markup)));
    if (result.ErrorCode == 0)
    {
        result.Save("output", "template");
        Console.WriteLine("OMR template generated in output/");
        File.WriteAllText("output/result.txt", "PASS: OMR template generated");
    }
    else
    {
        Console.Error.WriteLine($"Template generation error: {result.ErrorCode}");
        foreach (var w in result.Warnings)
            Console.Error.WriteLine($"  Warning: {w}");
        File.WriteAllText("output/result.txt", $"FAIL: ErrorCode={result.ErrorCode}");
        Environment.Exit(1);
    }
}
catch (Exception ex)
{
    Console.Error.WriteLine($"BLOCKED: {ex.GetType().Name}: {ex.Message}");
    File.WriteAllText("output/blocker.txt", ex.ToString());
    Environment.Exit(1);
}
