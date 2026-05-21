# Contract-Derived Assumptions — Sprint 61 Phase 7

## Summary

All 42 format-authority contracts currently have `api_verified=False`. This means
I/O format data is derived from contract schema and Program.cs parsing rather than
live DLL reflection.

---

## Authority Depth Matrix Results

| Depth Level | Count | Meaning |
|-------------|-------|---------|
| DUAL_SOURCE | 41 | Both format-authority contract AND Program.cs confirm I/O |
| CONTRACT_ONLY | 1 | Contract exists but no local Program.cs (pdf-pdf-aconverter) |
| PROGRAMCS_ONLY | 0 | No contract types have this gap |
| NO_AUTHORITY | 0 | All types have at least contract coverage |

**41/42 scenarios have dual-source I/O authority.**

The 1 CONTRACT_ONLY case (`pdf-pdf-aconverter`) has no local package and Program.cs
cannot be parsed locally. Its contract data provides the only authority.

---

## API Verification Status

All 42 contracts: `api_verified=False`

This is the planned state for Sprint 61. API verification (DLL reflection via
`DllReflector`) was established in Sprint 54/55 but the contract flag was not
backfilled for all types. This is tracked as a follow-up action, not a blocker.

**Corroboration evidence (substitute for api_verified):**
- 41/42 types: Program.cs I/O confirms contract I/O format
- 1/42 type: Contract-only (pdf-pdf-aconverter, no local package)

---

## API Catalog Snippets

Written to `api-catalog-snippets/`:

| File | Family | Types |
|------|--------|-------|
| `cells-api-catalog-snippet.json` | cells | 9 |
| `diagram-api-catalog-snippet.json` | diagram | 2 |
| `email-api-catalog-snippet.json` | email | 1 |
| `pdf-api-catalog-snippet.json` | pdf | 19 |
| `slides-api-catalog-snippet.json` | slides | 3 |
| `words-api-catalog-snippet.json` | words | 8 |

**Total: 42 types across 6 families**

Each snippet includes: `type_name`, `full_type_name`, `canonical_input_formats`,
`canonical_output_format`, `variant_count`, `api_verified`.

---

## Variant Coverage

Total output format variants across all types:

| Family | Types | Total Variants |
|--------|-------|---------------|
| cells | 9 | 19 |
| diagram | 2 | 6 |
| email | 1 | 6 |
| pdf | 19 | 20 |
| slides | 3 | 7 |
| words | 8 | 12 |

---

## Evidence Files

| File | Description |
|------|-------------|
| `authority-depth-matrix.json` | Per-scenario depth (41 DUAL_SOURCE, 1 CONTRACT_ONLY) |
| `contract-derived-assumptions.json` | 42 assumptions, 41 corroborated by Program.cs |
| `api-catalog-snippets/` | Per-family type/format snippets (6 files) |
| `contract-derived-assumptions.md` | This document |
