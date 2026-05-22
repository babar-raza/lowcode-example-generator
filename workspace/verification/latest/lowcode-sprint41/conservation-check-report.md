# Lane E — Conservation Check Report

**Status:** ALL_PASS

## Conservation Equations

### Per-Family: published + pending + blocked = pilot_allowed (for families with pilot scope)

| Family | Published | Pending | Blocked | Sum | Pilot Allowed | Conservation |
|--------|-----------|---------|---------|-----|---------------|-------------|
| Cells | 9 | 0 | 0 | 9 | 9 | PASS |
| Words | 8 | 0 | 0 | 8 | 8 | PASS (Processor blocked but outside pilot scope) |
| PDF | 5 | 14 | 0 | 19 | 19 | PASS (3 blocked types are outside pilot scope) |
| Diagram | 2 | 0 | 0 | 2 | 2 | PASS |
| Email | 1 | 0 | 0 | 1 | 1 | PASS |
| Slides | 3 | 0 | 0 | 3 | 3 | PASS |
| **Total** | **28** | **14** | **0** | **42** | **42** | **PASS** |

### Workflow Root Accounting

| Family | WF Roots | In Pilot | Blocked (in WF root, outside pilot) | Reclassified | Sum |
|--------|----------|----------|--------------------------------------|-------------|-----|
| Cells | 9 | 9 | 0 | 0 | 9 |
| Words | 9 | 8 | 1 (Processor) | 0 | 9 |
| PDF | 22 | 19 | 3 (FormImporter, Timestamp, Ofd) | 3 (PdfExtractor, PdfToImage, SelectField) | 22+3=25 raw, 22 adjusted |
| Diagram | 2 | 2 | 0 | 0 | 2 |
| Email | 1 | 1 | 0 | 0 | 1 |
| Slides | 3 | 3 | 0 | 0 | 3 |

### No Silent Omission Check

Every planned runnable example is in exactly one state:

| State | Count | Examples |
|-------|-------|----------|
| PUBLISHED (POST_MERGE_VERIFIED) | 28 | 9 cells + 8 words + 5 pdf + 2 diagram + 1 email + 3 slides |
| PENDING_PR (PR_READY) | 14 | 14 pdf in PRs #5-#10 |
| BLOCKED_WITH_EVIDENCE | 4 | Words Processor, PDF FormImporter/Timestamp/Ofd |
| PERMANENTLY_BLOCKED | 3 | Words Processor, PDF Timestamp, PDF Ofd |
| SILENTLY_DROPPED | 0 | NONE |

**Result:** No planned runnable example is silently ignored.

## Type-Level Conservation (Full SOT)

| Family | Total Types | WF Roots | Non-Runnable | Sum Check |
|--------|------------|----------|-------------|-----------|
| Cells | 22 | 9 | 13 | 9+13=22 PASS |
| Words | 25 | 9 | 16 | 9+16=25 PASS |
| PDF | 101 | 22 | 79 | 22+79=101 PASS |
| Diagram | 5 | 2 | 3 | 2+3=5 PASS |
| Email | 3 | 1 | 2 | 1+2=3 PASS |
| Slides | 5 | 3 | 2 | 3+2=5 PASS |
| **Total** | **161** | **46** | **115** | **PASS** |
