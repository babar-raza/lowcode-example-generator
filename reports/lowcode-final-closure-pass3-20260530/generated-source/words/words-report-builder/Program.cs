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

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");

            // BuildReport — no suitable overload found in catalog
            // BuildReportToImages — no suitable overload found in catalog
            // Demonstrate ReportBuilder.Create
            ReportBuilder.Create();

            Console.WriteLine("Done.");
        }
    }
}
