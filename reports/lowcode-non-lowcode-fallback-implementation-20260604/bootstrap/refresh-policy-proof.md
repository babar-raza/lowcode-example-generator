# Registry Refresh Policy — Proof Document

**Sprint:** non-lowcode-fallback-implementation-20260604  
**Generated:** 2026-06-04

## Refresh Policy

All registry entries with `bootstrap_status: PROBE_CONFIRMED` must be refreshed
quarterly (every 90 days) to account for NuGet package updates and potential
API surface changes.

| trigger | action |
|---------|--------|
| `refresh_due` date reached | Re-run DllReflector; compare API surface with fingerprint ledger |
| Package version changed | Re-run probe; update `assembly_fingerprint` and `last_validated` |
| `confidence_score` < 0.70 | Promote to NEEDS_MANUAL_MAPPING |
| Probe output size = 0 | Re-classify as PROBE_FAILED with failure_taxonomy |

## Current Refresh Schedule

| family | last_validated | refresh_due | delta_days |
|--------|---------------|------------|-----------|
| barcode | 2026-06-04 | 2026-09-04 | 92 |
| imaging | 2026-06-04 | 2026-09-04 | 92 |
| zip | 2026-06-04 | 2026-09-04 | 92 |

## Refresh Verification Protocol

1. Fetch latest NuGet version: `GET https://api.nuget.org/v3-flatcontainer/{pkg}/index.json`
2. Compare version with `last_reflected_package_version`
3. If version changed: re-download, re-extract, re-run DllReflector
4. If API surface changed (new/removed types/methods): update registry entry and re-probe
5. If no changes: update `last_validated` only; keep `assembly_fingerprint`

## Fingerprint Change Policy

A change in `assembly_fingerprint` (DLL SHA-256) triggers mandatory re-probe.
No entry advances to VERIFIED_PUBLISHABLE without a current probe_evidence file.
