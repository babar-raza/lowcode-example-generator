# Canonical-First Example Generator Design
Sprint: lowcode-plugin-canonical-primary-wave8-20260605
Date: 2026-06-05

## Purpose

This document describes the design changes to the example factory tooling
required to enforce canonical-primary identity throughout the generation
pipeline. Prior waves (A through 7) sometimes used generic operation names
(e.g., `generate-barcode`) as the plugin slug. This sprint enforces that
only `products.aspose.net` URL last-segment slugs are used as primary keys.

## Canonical Identity Contract

A plugin entry is **canonical-primary** when:
1. `plugin_slug` == `canonical_plugin_slug` == last segment of `canonical_url` path
2. `identity_status == "CANONICAL_IDENTITY_VERIFIED"`
3. `display_plugin_name` is set (human-readable product name)
4. Any old operation names are in `legacy_aliases` only

### Example (BarCode 1D writer)

```yaml
plugin_slug: 1d-barcode-writer
canonical_plugin_slug: 1d-barcode-writer
canonical_url: https://products.aspose.net/barcode/1d-barcode-writer/
display_plugin_name: 1D Barcode Writer for .NET
identity_status: CANONICAL_IDENTITY_VERIFIED
migration_status: CANONICAL_PRIMARY_MIGRATED
migrated_from: generate-barcode
legacy_aliases:
  - generate-barcode
```

## Generator Input Selection

The `ExampleFactory` (and any Wave-N generation scripts) must select entries
from the registry using `loader.ready_entries()` or `loader.active_entries()`,
which already exclude protected families.

**New requirement**: Before generating, validate each candidate entry:

```python
from src.plugin_examples.plugin_code_registry.loader import PluginCodeRegistryLoader

loader = PluginCodeRegistryLoader().load()
for entry in loader.ready_entries():
    violations = loader.validate_entry(entry)
    if violations:
        raise RuntimeError(f"Registry violations: {violations}")
    if entry.identity_status != "CANONICAL_IDENTITY_VERIFIED":
        # Skip or warn — do not generate for unverified identity
        continue
    # proceed with generation using entry.plugin_slug (canonical)
```

## Output Path Convention

All generated dryrun packages MUST use the canonical slug in the output path:

```
reports/<sprint>/dryrun/examples/<family>/<canonical_plugin_slug>/
```

**PROHIBITED**: paths using legacy alias slugs without an alias record.

## Source Provenance

Each generated package must write `source-provenance.json` with:

```json
{
  "family": "<family>",
  "plugin_slug": "<canonical_plugin_slug>",
  "canonical_plugin_slug": "<canonical_plugin_slug>",
  "canonical_url": "<products.aspose.net url>",
  "display_plugin_name": "<human name>",
  "identity_status": "CANONICAL_IDENTITY_VERIFIED",
  "generation_sprint": "<sprint_id>",
  "generated_at": "<ISO date>"
}
```

If migrating a prior generic package, also set:
```json
{
  "legacy_example_slug": "<old generic slug>",
  "migrated_from": "<old generic slug>"
}
```

## README Title

README.md `# Title` MUST use `display_plugin_name`, not a generic operation name.

- CORRECT: `# 1D Barcode Writer for .NET`
- INCORRECT: `# Generate Barcode`

## Package Key

`output-validation.json` MUST set `package_key` to `<family>/<canonical_plugin_slug>`.
This is required for the publication readiness matrix.

## Alias Backward Compatibility

The `PluginCodeRegistryLoader.lookup_by_alias(family, old_slug)` method allows
callers to resolve an old slug to its canonical entry. Generation tools MUST
NOT create separate dryrun packages for aliases — only for canonical entries.

## Wave 8 Candidate Selection

Wave 8 generation uses `loader.ready_entries()` filtered to
`identity_status == "CANONICAL_IDENTITY_VERIFIED"`. Entries with
`SLUG_ALIAS_REQUIRED` or `MISSING_CANONICAL_URL` are deferred until
their canonical identity is confirmed in the registry.

Preferred Wave 8 candidates (from current registry state):
- `html/html-converter` — CANONICAL_IDENTITY_VERIFIED, CODE_HARVESTED
- `tasks/project-converter` — CODE_HARVESTED, has classes
- `zip/archive-extractor` — multiple entries, need audit

## Invariant Summary

| Rule | Description |
|------|-------------|
| GEN-01 | plugin_slug in generated package must equal canonical_plugin_slug |
| GEN-02 | dryrun path must use canonical_plugin_slug, not legacy alias |
| GEN-03 | source-provenance.json must set canonical_plugin_slug |
| GEN-04 | README title must use display_plugin_name |
| GEN-05 | output-validation.json must set package_key = family/canonical_slug |
| GEN-06 | No new packages generated for legacy alias slugs |
| GEN-07 | All READY_FOR_TRANSFORMATION entries must pass validate_entry() before generation |

## Status

Lane D tooling design: COMPLETE
Model/loader updates: COMPLETE (canonical_primary_entries=17, alias lookup verified)
CPV validator rules: Lane E (next)
