# Artifact Self-Reference Policy

Sprint: lowcode-final-megasprint-20260601

## Convention: DOCUMENTED_EXCLUSION (3 files)
Three files are excluded from per-file-sha256.json:
1. per-file-sha256.json — cannot hash itself (circular)
2. zip-file-list.txt — written after per-file-sha256 (would invalidate hash)
3. self-contained-bundle-check.json — written after per-file-sha256

All other artifact metadata files (final-clean-proof.json, sidecar-verification.log,
bundle-manifest.json, artifact-protocol.md, artifact-exclusion-list.json) ARE hashed
because they are written before per-file-sha256.json.

## final-clean-proof.json and sidecar-verification.log
These files use the SIDECAR_ONLY convention:
- Inside the ZIP, they honestly state that actual ZIP hash values live in external sidecar files
- They do NOT say PENDING_ZIP_BUILD
- They say SIDECAR_ONLY with explanation
- External sidecar files (.sha256, .size-count.json) contain the actual values
- This is mathematically honest: the ZIP cannot contain its own hash

## zip-file-list.txt
Lists ALL files in the ZIP, including itself and self-contained-bundle-check.json.
Achieved by pre-computing the complete file list before writing.
