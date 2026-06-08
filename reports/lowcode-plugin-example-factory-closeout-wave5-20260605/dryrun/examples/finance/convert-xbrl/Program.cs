// finance/convert-xbrl
// Canonical: https://products.aspose.net/finance/convert-xbrl/
// Package: Aspose.Finance 24.12.0
// Pattern: Write XBRL fixture -> new XbrlDocument(path) -> Save(outPath, SaveOptions{SaveFormat.IXBRL})
using Aspose.Finance.Xbrl;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "report.ixbrl");

string xbrl = @"<?xml version=""1.0"" encoding=""UTF-8""?>
<xbrl xmlns=""http://www.xbrl.org/2003/instance""
      xmlns:xbrli=""http://www.xbrl.org/2003/instance""
      xmlns:link=""http://www.xbrl.org/2003/linkbase""
      xmlns:xlink=""http://www.w3.org/1999/xlink"">
  <context id=""ctx_fy2025"">
    <entity><identifier scheme=""http://www.lei.org"">TESTENTITY001</identifier></entity>
    <period><startDate>2025-01-01</startDate><endDate>2025-12-31</endDate></period>
  </context>
  <unit id=""USD""><measure>iso4217:USD</measure></unit>
</xbrl>";

string fixturePath = "fixture.xbrl";
File.WriteAllText(fixturePath, xbrl, System.Text.Encoding.UTF8);

var doc = new XbrlDocument(fixturePath);
var saveOptions = new SaveOptions { SaveFormat = SaveFormat.IXBRL };
doc.Save(outputPath, saveOptions);

long size = new FileInfo(outputPath).Length;
Console.WriteLine($"XBRL converted to iXBRL: {outputPath} ({size} bytes)");
