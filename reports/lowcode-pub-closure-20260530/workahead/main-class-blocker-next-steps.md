# Main-Class Blocker Next Steps — lowcode-pub-closure-20260530

## Closeable Blockers

### cells-SpreadsheetPrinter
- Action: Test with Microsoft Print to PDF virtual printer (Windows only)
- Command: `dotnet run -- --printer "Microsoft Print to PDF" --output output.pdf`
- ETA: Closeable in next sprint if Windows CI available

### words-Signer
- Action: Generate self-signed PFX via fixture generator
- Command: `openssl req -x509 ... -out signing.pfx`
- ETA: Closeable in next sprint (1 day effort)

### words-Processor
- Action: API investigation — determine if standalone demo possible
- Source: Aspose.Words documentation + reflection scan
- ETA: Closeable if API supports standalone mode

### pdf-Ofd
- Action: Find/create minimal legal OFD fixture
- Source: Chinese government open standard resources
- ETA: Indeterminate (external format dependency)

## True External Blockers (no action possible now)
- pdf-FormImporter: Wait for Aspose.PDF bug fix (NullRef in Process())
- pdf-Timestamp: Wait for offline/test TSA mode in Aspose.PDF
- cells-SpreadsheetPrinter (CI): Wait for CI virtual printer support
