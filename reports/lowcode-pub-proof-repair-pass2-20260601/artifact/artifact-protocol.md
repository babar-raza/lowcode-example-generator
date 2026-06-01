# Artifact Sidecar Protocol

Sprint: lowcode-pub-proof-repair-pass2-20260601

## Convention: NON_CIRCULAR_SIDECAR
1. ZIP contains: bundle-manifest.json, per-file-sha256.json, zip-file-list.txt
2. ZIP does NOT contain its own final hash (non-circular)
3. Sidecar files OUTSIDE ZIP contain: final SHA-256, size, entry count
4. Internal bundle-manifest states "does not contain final ZIP hash"
5. final-clean-proof.json is written AFTER ZIP build with actual values

## Verification
After ZIP build:
1. Compute SHA-256 of ZIP file
2. Write <bundle>.sha256 sidecar
3. Write <bundle>.size-count.json sidecar
4. Re-compute SHA-256 to verify sidecar
5. Write final-clean-proof.json referencing actual values
