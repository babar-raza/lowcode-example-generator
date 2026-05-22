# Lane Ownership Matrix

| Lane | Owner Role | Files May Touch | Overlap Risk |
|------|-----------|-----------------|--------------|
| A — Evidence Intake | Evidence/state coordinator | workspace/verification/latest/lowcode-main-sprint/evidence-intake-* | None |
| B — State Reconciliation | State model / denominator | pipeline/configs/denominators/*.json, src/plugin_examples/publisher/release_status.py | Overlaps with C (denominators), D (README counts) |
| C — PDF Publication | Publication owner | workspace/pr-dry-run/*, workspace/verification/latest/lowcode-main-sprint/pdf-* | Overlaps with B (denominators), D (README) |
| D — README Hardening | README/portfolio owner | src/plugin_examples/publisher/readme_*.py | Overlaps with B (counts), C (PDF README) |
| E — Health/Drift | Health/version owner | workspace/verification/latest/lowcode-main-sprint/version-drift-*, target-repo-health-* | Overlaps with B (denominators) |
| F — Tests | Test/evidence owner | tests/unit/*, workspace/verification/latest/lowcode-main-sprint/test-* | Overlaps with all (validates everything) |
| G — Generation | Generation owner | workspace/runs/*, generated/* | Overlaps with B (state), C (packages), D (README) |

## Serialization Rules

1. Denominator JSON edits: B first, then E validates, then C/D/G may read
2. Evidence contract updates: F owns, all lanes read
3. README renderer/auditor: D owns, C reads
4. Release status code: B owns, all lanes read
5. Test files: F owns exclusively

## Current Sprint Number

Sprint 38 (computed from workspace/verification/ sprint directories: highest=37, next=38)
