# Artifact Protocol — lowcode-systemization-pass3-20260530
Date: 2026-05-30

## K1 FIX: No Self-Reference SHA

A ZIP file CANNOT reliably contain a file that states the final ZIP SHA-256.
Changing the embedded SHA changes the ZIP, which changes the SHA — infinite loop.

## Pass3 Sidecar Convention

### Inside ZIP
- All tracked evidence files
- artifact/bundle-manifest.json (entry count, content SHA, build metadata)
- artifact/per-file-sha256.json (SHA of every file in ZIP)
- artifact/zip-file-list.txt (list of all entries)
- artifact/final-clean-proof.json (git HEAD, clean tree proof, build date)
- artifact/artifact-protocol.md (this file)

### Outside ZIP (sidecar — NOT inside ZIP)
- <bundle>.sha256.txt — final ZIP SHA-256
- <bundle>.size-count.json — final ZIP size in bytes + entry count

### Why Sidecar Works
The sidecar files are computed AFTER the ZIP is finalized.
They describe the ZIP without being part of it.
The ZIP verifier checks the sidecar against the actual ZIP.

## Implementation
build_systemization_pass3_zip.py implements 2-pass convention:
- Pass 1: Build content ZIP (no self-reference)
- Pass 2: Add artifact metadata (bundle-manifest, per-file-sha, zip-file-list, protocol)
- Write sidecar: <bundle>-sha256.txt with final SHA
