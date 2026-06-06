// finance/parse-xbrl — W18 probe attempt (offline XBRL fixture)
// NuGet: Aspose.Finance
// Pattern: XbrlDocument(path) — network dependency test
using System;
using System.IO;
using Aspose.Finance.Xbrl;

Directory.CreateDirectory("output");

string xbrlPath = Path.Combine("fixtures", "minimal-xbrl.xml");
Console.WriteLine($"Attempting to load: {xbrlPath}");

try
{
    var doc = new XbrlDocument(xbrlPath);
    var instance = doc.XbrlInstances[0];
    Console.WriteLine($"Loaded XBRL: {instance.Contexts.Count} contexts, {instance.Units.Count} units");
    File.WriteAllText("output/parse-result.txt", $"Contexts: {instance.Contexts.Count}, Units: {instance.Units.Count}");
}
catch (Exception ex)
{
    Console.Error.WriteLine($"BLOCKED: {ex.GetType().Name}: {ex.Message}");
    File.WriteAllText("output/blocker.txt", $"Exception: {ex.GetType().Name}\nMessage: {ex.Message}\nStackTrace:\n{ex.StackTrace}");
    Environment.Exit(1);
}
