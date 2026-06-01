# Artifact Protocol

Sprint: lowcode-final-megasprint-20260601
Convention: NON_CIRCULAR_SIDECAR + DOCUMENTED_EXCLUSION + SIDECAR_ONLY

Build order:
1. Write all content files (reports, packages, tests, IV, etc.)
2. Write final-clean-proof.json (SIDECAR_ONLY — no ZIP hash)
3. Write sidecar-verification.log (SIDECAR_ONLY — no ZIP hash)
4. Write artifact-exclusion-list.json, self-reference-policy.md, artifact-protocol.md
5. Write bundle-manifest.json
6. Write per-file-sha256.json (hashes everything written so far, excluding 3 self-referential files)
7. Write zip-file-list.txt (lists ALL files including itself and self-contained-bundle-check)
8. Write self-contained-bundle-check.json (verifies consistency)
9. Build ZIP
10. Compute SHA-256, write external sidecars
