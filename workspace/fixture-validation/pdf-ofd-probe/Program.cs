using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

Console.WriteLine("=== Ofd Probe ===");

// Reflect Ofd type
var ofdType = typeof(Ofd);
Console.WriteLine("Ofd ctors:");
foreach (var c in ofdType.GetConstructors()) Console.WriteLine($"  {c}");

// Find OFD options types
foreach (var t in typeof(Ofd).Assembly.GetTypes())
{
    if (t.Name.Contains("Ofd") || t.Name.Contains("OFD"))
        Console.WriteLine($"Type: {t.FullName} (ctors: {t.GetConstructors().Length})");
}

// Try to create a PDF and convert to OFD
var doc = new Document();
doc.Pages.Add();
doc.Save("input.pdf");
Console.WriteLine("PDF created");

// Try OFD options
Console.WriteLine("\nAttempting Ofd conversion...");
try
{
    // Find the correct options class via reflection
    var optTypes = typeof(Ofd).Assembly.GetTypes();
    Type? ofdOpts = null;
    foreach (var t in optTypes)
        if ((t.Name.Contains("OfdOptions") || t.Name == "OfdConvertOptions") && t.GetConstructors().Length > 0)
            ofdOpts = t;
    
    if (ofdOpts == null)
    {
        Console.WriteLine("OFD_BLOCKED: No OfdOptions type found with constructors");
    }
    else
    {
        Console.WriteLine($"Found options type: {ofdOpts.Name}");
        var opts = Activator.CreateInstance(ofdOpts);
        Console.WriteLine($"Options created: {opts?.GetType().Name}");
    }
}
catch (Exception ex)
{
    Console.WriteLine($"OFD_FAIL: {ex.GetType().Name}: {ex.Message}");
}
