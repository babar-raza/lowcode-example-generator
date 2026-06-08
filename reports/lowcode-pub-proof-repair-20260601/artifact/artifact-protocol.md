# Artifact Sidecar Protocol

## Convention
1. ZIP contains: bundle-manifest.json, per-file-sha256.json, zip-file-list.txt
2. ZIP does NOT contain its own final hash (non-circular)
3. Sidecar files OUTSIDE ZIP contain: final SHA-256, size, entry count
4. Internal bundle-manifest has build timestamp and entry count but NOT the final ZIP hash
5. Sidecar is verified by re-computing SHA-256 of the actual ZIP file

## Verification
After ZIP build:
1. Compute SHA-256 of ZIP file
2. Write <bundle>.sha256 sidecar
3. Write <bundle>.size-count.json sidecar
4. Verify sidecar matches actual file
