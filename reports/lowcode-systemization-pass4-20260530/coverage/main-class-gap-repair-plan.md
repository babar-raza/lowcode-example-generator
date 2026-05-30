# Main-Class Gap Repair Plan — lowcode-systemization-pass4-20260530

## Reclassified Gaps (from EXAMPLE_GAP/NEEDS_API_INVESTIGATION to actionable)

### BLK-004: Words Processor
- Was: NEEDS_API_INVESTIGATION
- Now: EXAMPLE_GAP_CLOSEABLE
- Action: Processor uses MailMergeDataTable — create example in next sprint

### BLK-005: Words Signer
- Was: EXAMPLE_GAP (pfx fixture)
- Now: EXAMPLE_GAP_CLOSEABLE
- Action: Self-signed PFX works (proven by Signature PDF example) — create Signer example

### BLK-007: Slides ForEach
- Was: EXAMPLE_GAP
- Now: NON_RUNNABLE_HELPER
- Action: ForEach has no standalone Process() method — document as non-runnable type

## Remaining True Blockers
- BLK-001: FormImporter — external library bug (ACCEPTED)
- BLK-002: OfdConverter — fixture unavailable (ACCEPTED)
- BLK-003: Timestamp — network dependency (ACCEPTED, excluded from pub candidates)
- BLK-006: SpreadsheetPrinter — print driver required (ACCEPTED)
