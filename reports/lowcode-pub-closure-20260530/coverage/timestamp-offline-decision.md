# PDF Timestamp Offline Decision — lowcode-pub-closure-20260530

## Status: PERMANENTLY_BLOCKED — external TSA dependency

## Analysis
Aspose.Pdf.LowCode.Timestamp requires a live TSA (Time Stamp Authority) server URL.
No offline/mock TSA implementation exists.

## Decision: EXCLUDE from PR candidates
- package_included: YES (example exists)
- pr_candidate: NO (external network dependency)
- Retry condition: If Aspose adds offline/test TSA mode
