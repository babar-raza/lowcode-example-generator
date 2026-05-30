# PDF Timestamp Publication Decision — lowcode-pub-closure-20260530

## Decision: EXCLUDED — external TSA dependency

## Rationale
- PdfTimestamp requires external TSA (Time Stamp Authority) server URL
- Cannot run in offline/CI environment without network access to TSA
- Classified as PERMANENTLY_BLOCKED (external network dependency)

## Effect on counts
- pr_candidates: reduced by 1 (from denominator basis)
- timestamp_excluded: 1
