# Missing / Blocked Main Class Examples
Date: 2026-05-30

## BLK-001: FormImporter (pdf)
Type: EXTERNAL_BUG_BLOCKER
Description: FormImporter.ImportFromJson() throws NullReferenceException on valid input
Retry: Aspose.PDF bug fix release

## BLK-002: OfdConverter (pdf)
Type: FIXTURE_BLOCKER
Description: No legal OFD fixture file available for testing
Retry: Legal OFD fixture file obtained

## BLK-003: TimestampEmbedder (pdf)
Type: NETWORK_DEPENDENCY_BLOCKER
Description: Requires live TSA endpoint for RFC 3161 timestamp
Retry: Valid TSA endpoint credential available

## BLK-004: ForEach (slides)
Type: EXAMPLE_GAP
Description: ForEach class has no publication example yet
Retry: Example generation in next sprint

## BLK-005: Signer (words)
Type: EXAMPLE_GAP
Description: Signer class has no publication example yet (requires pfx fixture)
Retry: Example generation in next sprint

## BLK-006: Processor (words)
Type: NEEDS_API_INVESTIGATION
Description: Processor classification uncertain — may be internal infrastructure class
Retry: API investigation complete

## BLK-007: SpreadsheetPrinter (cells)
Type: FIXTURE_BLOCKER
Description: SpreadsheetPrinter requires printer device — not feasible in CI
Retry: Virtual printer fixture or mock available

