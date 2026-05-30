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
            Console.WriteLine("Example: cells-spreadsheet-locker");

            // Input file provided by pipeline fixture factory
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");

            // Demonstrate SpreadsheetLocker.Process
            SpreadsheetLocker.Process(Path.Combine(AppContext.BaseDirectory, "input.xlsx"), "output.xlsx", "test-password", "test-password");

            Console.WriteLine("Done.");
        }
    }
}
