# Previous Bundle Audit

## Bundle Identity
- Sprint ID: lowcode-full-closure-mega-train-20260529
- ZIP: .local/evidence-bundles/lowcode-full-closure-mega-train-20260529-evidence.zip

## Actual ZIP Measurements (this audit)
- Actual SHA256: 315980b12f8fc287207add2d5eaaa8f437a3aa44f977e02a51574bbf3c5cfd0d
- Actual size: 32896 bytes (32.1 KB)
- Actual entry count: 39

## Claimed Metadata in artifact-verification.json
- Claimed SHA256: c554d285fd75b32bb65fc5cb9ef7b21e5b9d8ebe4e95a7a315115325f1bc4f8b
- Claimed size: 31652 bytes
- Claimed entry count: 37

## Metadata Mismatch
- SHA256: MISMATCH (actual ≠ claimed)
- Size: MISMATCH (32896 ≠ 31652 — delta = 1244 bytes)
- Entry count: MISMATCH (39 ≠ 37 — delta = 2 entries)

## Root Cause
The artifact-verification.json was written before the final 2 artifact-metadata entries
(zip-file-list.txt and artifact-verification.json itself) were appended to the ZIP.
The ZIP was re-opened in append mode after artifact-verification was written,
so the recorded SHA/size/count captured the intermediate state, not the final ZIP.

## Accepted Claims
- ECC 44/44: partially verified — ECC script ran and reported 44/44 PRESENT
- pytest 3174/0/18: partially verified — test run reported these counts
- 6 healed examples: work was done but durability not proven (workspace-only patches)

## Rejected Claims
See rejected-claims-register.json for full list.

## Usefulness
The prior bundle is useful as evidence of local healing work. It correctly documents
the 6 defects and workspace-level patches. It does NOT prove durable generation-level closure.

## Status
NOT ACCEPTED — requires this sprint to replace it with properly governed evidence.
