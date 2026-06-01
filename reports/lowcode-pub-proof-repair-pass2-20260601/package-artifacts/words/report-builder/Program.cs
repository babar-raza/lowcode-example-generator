using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: words-report-builder");

            string templatePath = "template.docx";
            var doc = new Document();
            var builder = new DocumentBuilder(doc);
            builder.Writeln("Report: <<[Name]>>");
            builder.Writeln("Value: <<[Value]>>");
            doc.Save(templatePath);

            string outputPath = "output.docx";
            var data = new ReportData { Name = "LowCode Report", Value = 42 };
            ReportBuilder.BuildReport(templatePath, outputPath, data);

            Console.WriteLine(File.Exists(outputPath)
                ? $"Report built: {outputPath}"
                : "Report build failed: output not found.");
        }
    }

    public class ReportData
    {
        public string Name { get; set; }
        public int Value { get; set; }
    }
}
