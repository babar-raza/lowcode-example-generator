# Artifact Self-Reference Policy

Sprint: lowcode-pub-proof-pass3-20260601

## Problem
Certain artifact metadata files cannot include themselves:
- `per-file-sha256.json` cannot contain its own SHA-256 (would change on write)
- `zip-file-list.txt` content changes if it lists itself (stable if included as last entry)
- `final-clean-proof.json` references the ZIP hash which is unknown before ZIP build

## Convention: DOCUMENTED_EXCLUSION
Three files are excluded from per-file-sha256.json by mathematical necessity:
1. `per-file-sha256.json` — cannot hash itself
2. `final-clean-proof.json` — references ZIP hash (written pre-build as placeholder, updated post-build externally)
3. `sidecar-verification.log` — references ZIP hash (written pre-build as placeholder, updated post-build externally)

## zip-file-list.txt
zip-file-list.txt IS included in itself as the last entry. This is stable because the
file content is computed including the self-reference line before writing.

## Verification
- `artifact-exclusion-list.json` lists all excluded files and reasons
- `self-contained-bundle-check.json` verifies ZIP entries vs file list
- Validators enforce the convention (V18)
