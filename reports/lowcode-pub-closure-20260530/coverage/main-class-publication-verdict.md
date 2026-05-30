# Main-Class Publication Verdict — lowcode-pub-closure-20260530

## Fully Covered (examples generated, built, run, PR-ready)
- cells: 8/9 lowcode classes covered (SpreadsheetPrinter = closeable blocker)
- diagram: 1/1 covered (Converter)
- email: 1/1 covered (EmailConverter)
- pdf: 15/19 workflow-root types covered (3 blocked + 1 timestamp excluded)
- slides: 3/5 covered (ForEach = non-runnable helper, Splitter = existing)
- words: 7/9 covered (Signer + Processor = closeable blockers)

## True Blockers (external dependencies, confirmed)
1. pdf-FormImporter: NullRef bug in Aspose.PDF library — external bug, retry when fixed
2. pdf-Timestamp: TSA server URL required — external network dependency
3. pdf-Ofd: OFD input format, no programmatic fixture generator — closeable if fixture found

## Closeable Blockers (action possible)
1. cells-SpreadsheetPrinter: needs printer mock/virtual printer investigation
2. words-Signer: needs PFX fixture generation (safe self-signed cert)
3. words-Processor: needs API investigation (may not have runnable standalone mode)

## Non-runnable helpers
- slides-ForEach: utility class, not a standalone runnable example
