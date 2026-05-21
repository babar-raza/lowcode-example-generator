# Package Authority Depth Summary — Sprint 61 Phase 7

## Results

| Depth Level | Count | Description |
|-------------|-------|-------------|
| DUAL_SOURCE | 41 | Contract + Program.cs both confirm I/O |
| CONTRACT_ONLY | 1 | Contract only (pdf-pdf-aconverter, no local pkg) |
| PROGRAMCS_ONLY | 0 | — |
| NO_AUTHORITY | 0 | — |

**41/42 scenarios (97.6%) have dual-source I/O authority.**

## API Verification

All 42 type contracts have `api_verified=False`. Contracts derive from:
- `api-backed-format-contracts.json` + pipeline/contracts enrichment
- DLL reflection was established but backfill is incomplete

**Program.cs corroboration serves as substitute for api_verified:**
- 41/42 types: Program.cs I/O matches contract I/O
- 1/42: Contract-only (pdf-pdf-aconverter)

## Family Breakdown

| Family | Types | DUAL_SOURCE | CONTRACT_ONLY |
|--------|-------|-------------|---------------|
| cells | 9 | 9 | 0 |
| diagram | 2 | 2 | 0 |
| email | 1 | 1 | 0 |
| pdf | 19 | 18 | 1 (pdf-pdf-aconverter) |
| slides | 3 | 3 | 0 |
| words | 8 | 8 | 0 |

## Evidence Files

| File | Description |
|------|-------------|
| `package-authority-depth-matrix.json` | Per-scenario depth matrix (42 rows) |
| `authority-depth-matrix.json` | Same as above (build output) |
| `contract-derived-assumptions.json` | 42 assumptions, 41 corroborated |
| `contract-derived-assumptions.md` | Detailed assumption analysis |
| `api-catalog-snippets/` | Per-family type/format snippets (6 JSON files) |
| `package-authority-depth-summary.md` | This document |
