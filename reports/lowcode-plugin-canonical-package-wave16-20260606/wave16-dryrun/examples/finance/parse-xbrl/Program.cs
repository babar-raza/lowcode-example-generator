// finance/parse-xbrl
// Canonical: https://products.aspose.net/finance/parse-xbrl/
// Package: Aspose.Finance 24.12.0
// Pattern: Write minimal XBRL XML fixture -> XbrlDocument(path) -> iterate facts -> write summary
using Aspose.Finance.Xbrl;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");

string xbrlFixturePath = Path.Combine("output", "fixture.xbrl");
string outputPath = Path.Combine("output", "parsed-facts.txt");

// Create a minimal valid XBRL instance document programmatically
string xbrlContent = @"<?xml version=""1.0"" encoding=""UTF-8""?>
<xbrl xmlns=""http://www.xbrl.org/2003/instance""
      xmlns:xsi=""http://www.w3.org/2001/XMLSchema-instance""
      xmlns:xbrli=""http://www.xbrl.org/2003/instance""
      xmlns:link=""http://www.xbrl.org/2003/linkbase""
      xmlns:xlink=""http://www.w3.org/1999/xlink""
      xmlns:ifrs=""http://xbrl.ifrs.org/taxonomy/2021-03-24/ifrs-full"">
  <link:schemaRef xlink:type=""simple""
    xlink:href=""https://xbrl.ifrs.org/taxonomy/2021-03-24/ifrs-full"" />
  <context id=""ctx1"">
    <entity><identifier scheme=""http://www.example.com"">EXMPL</identifier></entity>
    <period><instant>2026-12-31</instant></period>
  </context>
  <ifrs:Assets contextRef=""ctx1"" decimals=""0"" unitRef=""USD"">1000000</ifrs:Assets>
  <ifrs:Liabilities contextRef=""ctx1"" decimals=""0"" unitRef=""USD"">500000</ifrs:Liabilities>
  <ifrs:Equity contextRef=""ctx1"" decimals=""0"" unitRef=""USD"">500000</ifrs:Equity>
  <unit id=""USD""><measure>iso4217:USD</measure></unit>
</xbrl>";

File.WriteAllText(xbrlFixturePath, xbrlContent, Encoding.UTF8);

// Parse the XBRL document
var xbrlDocument = new XbrlDocument(xbrlFixturePath);

var sb = new StringBuilder();
sb.AppendLine("XBRL Parsed Facts:");
sb.AppendLine($"Instances found: {xbrlDocument.XbrlInstances.Count}");

int factCount = 0;
foreach (XbrlInstance instance in xbrlDocument.XbrlInstances)
{
    sb.AppendLine($"  Instance contexts: {instance.Contexts.Count}");
    sb.AppendLine($"  Instance units: {instance.Units.Count}");
    foreach (Item item in instance.Items)
    {
        sb.AppendLine($"  Item: {item.Name?.LocalName} = {item.Value}");
        factCount++;
    }
}

sb.AppendLine($"Total facts: {factCount}");
File.WriteAllText(outputPath, sb.ToString(), Encoding.UTF8);

long size = new FileInfo(outputPath).Length;
Console.WriteLine($"XBRL parsed: {factCount} facts extracted -> {outputPath} ({size} bytes)");
