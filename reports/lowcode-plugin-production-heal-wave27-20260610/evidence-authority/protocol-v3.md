# Evidence Authority Protocol v3

## Problem with v2

Protocol v2 embedded `final-attestation.json` inside the ZIP before computing the final SHA.
This creates a bootstrap paradox: the SHA changes when the attestation is written, invalidating itself.

The W26 bundle demonstrated this:
- Internal attestation claimed SHA `791e9d08...` (computed before the final re-freeze)
- Actual ZIP after re-freeze had SHA `92e73f93...`
- External sidecar and external attestation correctly recorded `92e73f93...`

## Protocol v3 — Strict Separation

### Step 1: Build ZIP (primary evidence bundle)
Include everything EXCEPT final-attestation.json and .sha256 sidecar.
Include a non-authoritative `evidence-authority/pre-bundle-closeout.json` inside the ZIP.

### Step 2: Freeze ZIP — no further modifications
After `zipfile.close()`, the ZIP is frozen. No re-opening, no appending.

### Step 3: Compute SHA-256 of frozen ZIP
Read the frozen bytes. Compute `hashlib.sha256(frozen_bytes).hexdigest()`.

### Step 4: Write external `.sha256` sidecar
Format: `{sha256}  {filename}\n`
Path: `.local/evidence-bundles/{sprint}.sha256`

### Step 5: Write external `final-attestation.json`
Path: `.local/evidence-bundles/{sprint}-final-attestation.json`
Contains: SHA-256, size, entry count, verdict, achievements, blockers.

### Step 6: Write external `post-freeze-validation.json`
Path: `.local/evidence-bundles/{sprint}-post-freeze-validation.json`
Contains: re-read ZIP SHA, compare to sidecar, compare to attestation, PASS/FAIL.

### Invariants
- ZIP is NEVER reopened after Step 2.
- Final attestation is NEVER inside the ZIP.
- Sidecar is NEVER inside the ZIP.
- Internal `pre-bundle-closeout.json` is clearly labeled non-authoritative.
- All three external files reference the same SHA-256.
