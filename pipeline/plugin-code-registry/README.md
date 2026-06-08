# Plugin-Code Registry

## Purpose

This registry stores per-plugin evidence for non-LowCode Aspose families. Every entry traces to:
1. A real `products.aspose.net` plugin page URL
2. Official source code (GitHub repo, gist, or inline snippet)
3. Manual family analysis

## Registry vs Prior plugin-capability-registry

- `pipeline/plugin-capability-registry/` — prior sprint bootstrap, reflection-based, package metadata
- `pipeline/plugin-code-registry/` — **this registry** — page/code evidence based, registry with history

## Structure

```
pipeline/plugin-code-registry/
  schema/                          # JSON schema for validation
    plugin-code-registry.schema.json
  family/                          # Per-family YAML files
    barcode.yaml
    imaging.yaml
    ...
  registry-index.json              # Summary index of all entries
  README.md                        # This file
```

## Registry Status Enum

| Status | Meaning |
|--------|---------|
| PAGE_DISCOVERED | URL known but no code harvested |
| CODE_HARVESTED | GitHub/gist code fetched |
| MANUALLY_ANALYZED | Family analysis complete |
| SYMBOLS_EXTRACTED | API symbols from code |
| REFLECTION_CONFIRMED | DllReflector confirmed classes exist |
| PROBE_CONFIRMED | Runnable probe succeeded |
| READY_FOR_TRANSFORMATION | All evidence present, can generate example |
| TRANSFORMED_TO_EXAMPLE | Example generated |
| BLOCKED_LICENSE | Trial license prevents this |
| BLOCKED_FIXTURE | Input fixture required but not available |
| NEEDS_MANUAL_MAPPING | No official code; pattern must be written manually |
| WEBSITE_PATTERN_UNVERIFIED | URL constructed from pattern, not from real page |
| CODE_FETCH_FAILED | Code URL found but fetch failed |

## Invariants

1. No entry may advance to READY_FOR_TRANSFORMATION without code_hashes.
2. Every entry must have evidence_paths.
3. Every entry must have history (at least one record).
4. WEBSITE_PATTERN_UNVERIFIED may not be READY_FOR_TRANSFORMATION.
5. Family-level probe is NOT plugin-level coverage.
6. Reflection fields are validation only.

## Sprint Created

`lowcode-plugin-code-registry-20260604`
