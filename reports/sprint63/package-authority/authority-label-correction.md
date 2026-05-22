# Package Authority Label Correction — Sprint 63 Phase 5

## Problem

Sprint 62 claimed `api_verified=CONFIRMED_FROM_PROGRAMCS` for all 42 scenarios.
This label was used to support `authority=DUAL_SOURCE` for all entries.

**The label is misleading:**
- `CONFIRMED_FROM_PROGRAMCS` means: "the generated code calls this API"
- It does NOT mean: "this API is an officially documented, published package API"
- True "package API authority" requires: NuGet documentation, SDK reference, or official API docs

Calling this `DUAL_SOURCE` when both sources are the same generator output (contract + generated
Program.cs) overstates the authority. Two derived outputs from the same source is not dual authority.

## Correction

| Old Label | New Label | Meaning |
|-----------|-----------|---------|
| `api_verified=CONFIRMED_FROM_PROGRAMCS` | `api_verified=PROGRAMCS_USAGE_CONFIRMED` | Code uses the API |
| (implied) package authority | `package_api_authority=False` | NOT documented/published API authority |
| `authority=DUAL_SOURCE` | Retained (with caveat) | Contract + Program.cs, NOT two independent sources |

New fields added:
- `programcs_api_usage_verified: bool` — True when Program.cs confirmed to call the API
- `package_api_authority: bool` — True ONLY when backed by NuGet docs or official reference
- `authority_note: str` — Explanation of what authority means for this entry

## Current State (Sprint 63)

- `programcs_api_usage_verified=True`: 42/42
- `package_api_authority=True`: 0/42 (NuGet docs verification not performed)

## Impact on Verdict

Sprint 62 claimed "42/42 api_verified=CONFIRMED_FROM_PROGRAMCS" as a key achievement.
The corrected framing is:
- **What is true**: "42/42 generated examples have code that calls the documented LowCode API"
- **What is overclaimed**: "42/42 have independently verified package API authority"

The correct package API authority for all 42 scenarios comes from the Aspose NuGet documentation
and the SDK source, which has NOT been formally audited in this pipeline. The pipeline
generates examples from contracts that are themselves derived from the Aspose public API.

## Files

- `package-authority-matrix-corrected.json` — 42 entries with corrected labels
