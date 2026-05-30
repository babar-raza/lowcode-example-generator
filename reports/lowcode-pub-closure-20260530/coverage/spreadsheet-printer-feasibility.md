# SpreadsheetPrinter Feasibility — lowcode-pub-closure-20260530

## Investigation
Aspose.Cells.LowCode.SpreadsheetPrinter requires a printer device or virtual printer.
- Windows: Microsoft Print to PDF (virtual printer) may work
- Linux/Docker CI: no printer available
- Aspose does not expose a no-printer/mock mode in the LowCode API

## Virtual Printer Strategy
If run on Windows with Microsoft Print to PDF:
```csharp
var printer = new SpreadsheetPrinterOptions { PrinterName = "Microsoft Print to PDF" };
SpreadsheetPrinter.Process(inputPath, outputPath, printer);
```
This MIGHT work but is not portable to CI/Linux.

## Verdict: ENVIRONMENT_DEPENDENT
- Windows: potentially runnable with Microsoft Print to PDF
- CI/Linux: blocked (no printer device)
- Classification: CLOSEABLE_WINDOWS_ONLY — out of scope for cross-platform CI
