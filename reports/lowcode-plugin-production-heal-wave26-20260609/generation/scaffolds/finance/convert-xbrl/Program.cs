using Aspose.Finance.Xbrl;

Console.WriteLine("Aspose.Finance - XBRL Converter");
var doc = new XbrlDocument();
var inst = doc.XbrlInstances.Add();
Console.WriteLine($"XBRL instance created with {inst.Facts.Count} facts");
doc.Save("output.xbrl");
Console.WriteLine("XBRL document saved successfully: output.xbrl");
