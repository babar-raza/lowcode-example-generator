# ADR-006: Non-LowCode Fallback Strategy via Capability Registry

**Status:** Accepted
**Date:** 2026-06-04
**Context:** Not all Aspose product families expose LowCode or Plugins namespaces. Families like Imaging, ZIP, BarCode, CAD, Font, and Tasks have direct API patterns that differ from the LowCode convention. The pipeline originally hard-stopped when no LowCode namespace was found.

## Decision

Introduce a **capability registry** fallback strategy for non-LowCode families.

- When DLL reflection finds no `*.LowCode.*` or `*.Plugins.*` namespaces, the pipeline falls back to the capability registry.
- The capability registry maps families to their known public API entry points, discovered via probes (`probe_generator/`) and website catalog scraping (`website_catalog/`).
- Non-LowCode families use `fallback_strategy: capability_registry` in their family YAML config.
- Source-of-truth status for fallback families is `PROBE_CONFIRMED` rather than `REFLECTION_CONFIRMED`.
- FSV-07 validator enforces that discovery_only/fallback families have `PROBE_CONFIRMED` entries.

## Consequences

- Pipeline coverage expands from 6 LowCode families to 12+ families.
- Non-LowCode examples are generated from different prompt templates constrained to probed API symbols.
- Plugin PR folder layout uses `examples/<family>/<slug>/` (no `/plugins/` segment).
- Quality tier tracking distinguishes LowCode (tier 1) from fallback (tier 2) families.
