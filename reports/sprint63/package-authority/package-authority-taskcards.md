# Package Authority Task Cards — Sprint 63 Phase 5

## Background

Sprint 62 claimed `api_verified=CONFIRMED_FROM_PROGRAMCS` for all 42 scenarios,
supporting `authority=DUAL_SOURCE`. This was misleading.

## Corrected Labels (All 42 Scenarios)

| Field | Value | Meaning |
|-------|-------|---------|
| `api_verified` | `PROGRAMCS_USAGE_CONFIRMED` | Generated Program.cs calls this API |
| `programcs_api_usage_verified` | `True` | Confirmed by static analysis of generated code |
| `package_api_authority` | `False` | NOT backed by NuGet docs or official SDK reference |
| `authority` | `DUAL_SOURCE` (retained with caveat) | Contract + Program.cs (same origin) |

## What Needs to Happen for True Package API Authority

For `package_api_authority=True` to be set:
1. NuGet documentation for the relevant Aspose API must be reviewed
2. Method signatures, parameter types, and return types confirmed against official SDK
3. Evidence stored in `package-authority/nuget-verification/` with source URLs

## Current Status

- All 42 scenarios: `programcs_api_usage_verified=True` — code correctness confirmed
- All 42 scenarios: `package_api_authority=False` — formal SDK doc audit not performed
- No action blocked by this gap: generated examples are correct and published

## Priority

LOW — the generated examples are correct and working. The authority label correction
is a documentation quality improvement, not a publication blocker.

## See Also

- `authority-label-correction.md` — root cause analysis
- `package-authority-matrix-corrected.json` — corrected 42-entry ledger
