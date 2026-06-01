# Artifact Sidecar Protocol

Sprint: lowcode-pub-proof-pass3-20260601

## Convention: NON_CIRCULAR_SIDECAR + DOCUMENTED_EXCLUSION
1. ZIP built from reports/ after all content is written
2. Pre-build: final-clean-proof.json and sidecar-verification.log written as placeholders (no ZIP hash)
3. Post-build: actual SHA-256, size, entries computed
4. External sidecars written: .sha256, .size-count.json
5. final-clean-proof.json updated externally (not re-inserted into ZIP)
6. sidecar-verification.log updated externally
7. Three self-referential files excluded from per-file-sha256.json per DOCUMENTED_EXCLUSION policy
8. zip-file-list.txt includes itself via pre-computation
