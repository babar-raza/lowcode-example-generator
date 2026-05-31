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
            Console.WriteLine("Example: cells-spreadsheet-converter");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");

            // Demonstrate SpreadsheetConverter.Process
            SpreadsheetConverter.Process(Path.Combine(AppContext.BaseDirectory, "input.xlsx"), "output.csv");

            Console.WriteLine("Done.");
        }
    }
}
