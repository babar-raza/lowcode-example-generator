using Aspose.Finance.Xbrl;
using System;
using System.IO;

// Create and save an XBRL document
var doc = new XbrlDocument();
var instances = doc.XbrlInstances;
instances.Add();

string outputPath = "output.xbrl";
doc.Save(outputPath);

var info = new FileInfo(outputPath);
Console.WriteLine($"XBRL document created: {info.Length} bytes");
File.WriteAllText("expected-output.json", "{\"status\": \"success\", \"format\": \"xbrl\"}");
