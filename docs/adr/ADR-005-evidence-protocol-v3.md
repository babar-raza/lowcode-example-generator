# ADR-005: Evidence Protocol v3 — External Attestation

**Status:** Accepted
**Date:** 2026-06-10
**Context:** Wave 25-26 sprints revealed a bootstrap paradox: including the attestation file inside the ZIP changes the ZIP hash, making the attestation's own SHA claim invalid.

## Decision

Evidence protocol v3 requires that attestation, sidecar, and post-freeze validation files are always **external** to the ZIP bundle.

- The ZIP evidence bundle contains all evidence artifacts except the attestation.
- A `.sha256` sidecar file records the SHA-256 hash of the ZIP.
- A `-final-attestation.json` file references the sidecar hash and is stored alongside the ZIP, never inside it.
- A `-post-freeze-validation.json` file verifies the bundle after freeze.

## Consequences

- Eliminates the bootstrap paradox from protocol v2.
- All three files (sidecar, attestation, post-freeze) must exist for a valid evidence bundle.
- Sprint closeout validators (LCV-03, LCV-04) enforce presence of these external artifacts.
- Older v2 bundles retain their sidecar/attestation but may have internal SHA mismatches (documented in W27 corrections).
