using System;
using System.IO;
using Aspose.Cells;
using Aspose.Cells.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: cells-spreadsheet-merger");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");

            // SpreadsheetMerger requires multiple input files.
            // Create input1.xlsx and input2.xlsx from the available fixture.
            string input1Path = Path.Combine(AppContext.BaseDirectory, "input1.xlsx");
            string input2Path = Path.Combine(AppContext.BaseDirectory, "input2.xlsx");
            File.Copy(inputPath, input1Path, overwrite: true);
            File.Copy(inputPath, input2Path, overwrite: true);

            // Demonstrate SpreadsheetMerger.Process
            SpreadsheetMerger.Process(new string[] { input1Path, input2Path }, "output.xlsx");

            Console.WriteLine("Done.");
        }
    }
}
