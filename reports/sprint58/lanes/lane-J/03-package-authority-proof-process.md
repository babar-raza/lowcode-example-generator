# Process: Package Authority Proof (DLL Reflection → Authority Matrix)

**Process ID:** LANE-J-03
**Version:** Sprint 58
**Date:** 2026-05-21

---

## Overview

Package authority proof requires that every I/O type claim is backed by **external** evidence (DLL reflection, XML documentation, runtime probe) — not internal FA contracts authored by the pipeline.

Sprint 57 Defect D06: `package-evidence-ledger.json` cited `pipeline/format-authority/contracts/*.json` as ground truth. These contracts were written by the pipeline itself and do not constitute external proof.

---

## Evidence Sources (in priority order)

| Source | File Path | Authority Level |
|--------|-----------|----------------|
| DLL Reflection | `workspace/runs/discovery-{family}-{ts}/catalog/{family}/api-catalog.json` | HIGHEST |
| XML Documentation | Same catalog (xml_summary fields) | HIGH |
| Runtime Assembly Probe | Same catalog (type enumeration) | HIGH |
| FA Contract | `pipeline/format-authority/contracts/{family}.json` | INTERNAL ONLY — not external proof |

**Rule:** `authority_source` in `io-authority-evidence-matrix.json` MUST NOT be `contract_only` for any entry.

---

## Process Steps

### Step 1: Locate DLL Reflection Catalogs

```bash
ls workspace/runs/discovery-*/catalog/*/api-catalog.json
```

Discovery runs are produced by `DllReflector` during pipeline execution. Each catalog contains:
- `package_name`, `version`, `assembly`
- `types[]` — list of LowCode types with methods and XML docs

### Step 2: Build Reflection Ledger

For each family, extract from `api-catalog.json`:
- `package_name`, `version`, `assembly`
- `lowcode_type_count`, `types[]` with method signatures

Write to: `reports/sprint58/lanes/lane-B/reflection-ledger.json`

### Step 3: Build XML Doc Ledger

For each family, check `xml_summary` field availability per type.
Write to: `reports/sprint58/lanes/lane-B/xml-doc-ledger.json`

### Step 4: Build Runtime Probe Ledger

Enumerate all types discovered at runtime (from api-catalog.json type enumeration).
Write to: `reports/sprint58/lanes/lane-B/runtime-probe-ledger.json`

### Step 5: Build I/O Authority Evidence Matrix

For each of 42 types:
- Map type to its reflection catalog entry
- Set `authority_source`: `"reflection"` or `"reflection+xml_doc"` (never `"contract_only"`)
- Record `input_formats`, `output_formats`, `primary_output`, `evidence_reference`

Write to: `reports/sprint58/lanes/lane-B/io-authority-evidence-matrix.json`

---

## Acceptance Criteria

- `reflection-ledger.json`: 6 families, all with version from reflection (not hardcoded)
- `xml-doc-ledger.json`: 6 families, xml_available recorded
- `runtime-probe-ledger.json`: all LowCode types enumerated
- `io-authority-evidence-matrix.json`: 42 entries, zero `contract_only` entries
