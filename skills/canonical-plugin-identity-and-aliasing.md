# Skill: Canonical Plugin Identity and Aliasing

**Sprint introduced:** `lowcode-plugin-canonical-identity-wave7-20260605`

## Purpose

Enforce canonical plugin identity across all dry-run example packages. The authoritative plugin identity is the **exact slug from `products.aspose.net`** — not internal operation names or legacy keys.

## Core Concept

```
canonical_url  = "https://products.aspose.net/barcode/1d-barcode-writer/"
canonical_slug = "1d-barcode-writer"   ← last path segment of canonical_url
legacy_slug    = "generate-barcode"    ← old internal key, kept as alias only
```

## Identity Status Classifications

| Status | Meaning |
|--------|---------|
| `CANONICAL_IDENTITY_VERIFIED` | `plugin_slug` == `canonical_url` last segment |
| `SLUG_ALIAS_REQUIRED` | `canonical_url` exists but `plugin_slug` differs — alias must be documented |
| `MISSING_CANONICAL_URL` | No `canonical_url` field in registry entry — unblockable without page |

## Registry YAML Fields

Every plugin entry in `pipeline/plugin-code-registry/family/*.yaml` must have:

```yaml
- plugin_slug: generate-barcode          # legacy/internal key (preserved)
  canonical_plugin_slug: 1d-barcode-writer   # from products.aspose.net URL
  identity_status: SLUG_ALIAS_REQUIRED   # or CANONICAL_IDENTITY_VERIFIED
  canonical_url: https://products.aspose.net/barcode/1d-barcode-writer/
```

## Dry-Run Package source-provenance.json

```json
{
  "package_key": "barcode/1d-barcode-writer",
  "canonical_plugin_slug": "1d-barcode-writer",
  "canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/",
  "display_plugin_name": "1D Barcode Writer for .NET",
  "legacy_example_slug": "generate-barcode",
  "identity_status": "CANONICAL_IDENTITY_VERIFIED",
  "nuget_package": "Aspose.BarCode",
  "nuget_version": "24.12.0",
  "sprint": "lowcode-plugin-canonical-identity-wave7-20260605",
  "generated_at": "2026-06-05"
}
```

## Package Folder Naming Rule

- Folder name **must** be the `canonical_plugin_slug`, not the legacy slug
- `barcode/1d-barcode-writer/` ✓ — not `barcode/generate-barcode/` ✗

## BarCode Canonical Slugs

| Legacy Slug | Canonical Slug |
|-------------|---------------|
| `generate-barcode` | `1d-barcode-writer` |
| `generate-qr-code` | `2d-barcode-writer` |
| `recognize-barcode` | `1d-barcode-reader` |
| `scan-barcode` | `2d-barcode-reader` |

## PIV Validator Rules (PIV-01..PIV-14)

Run with: `run_plugin_identity_validators(pkg_dir, package_key)`

| Rule | Severity | Check |
|------|----------|-------|
| PIV-01 | ERROR | source-provenance.json exists |
| PIV-02 | ERROR | canonical_url present and non-empty |
| PIV-03 | ERROR | canonical_plugin_slug present |
| PIV-04 | ERROR | canonical_url slug matches canonical_plugin_slug |
| PIV-05 | ERROR/WARNING | folder name matches canonical slug or has documented alias |
| PIV-06 | WARNING | display_plugin_name present |
| PIV-07 | WARNING | identity_status present |
| PIV-08 | ERROR | BarCode generic names (generate-barcode etc.) never canonical |
| PIV-09 | WARNING | README.md exists |
| PIV-10 | WARNING | README title doesn't use generic barcode name |
| PIV-11 | WARNING | output-validation.json verdict present |
| PIV-12 | ERROR | PASS packages have non-zero output files |
| PIV-13 | ERROR | package-manifest.json canonical_url matches source-provenance.json |
| PIV-14 | ERROR | PUBLICATION_CANDIDATE_LOCAL_CLEAN requires CANONICAL_IDENTITY_VERIFIED |

## Publication Gate

A package is `PUBLICATION_CANDIDATE_LOCAL_CLEAN` **only if**:
1. `output-validation.json` verdict = `PASS`
2. `identity_status` = `CANONICAL_IDENTITY_VERIFIED`
3. No PIV ERROR violations
4. `canonical_plugin_slug` present in source-provenance.json

Prior-wave packages that pre-date this system are classified `IDENTITY_REVIEW_REQUIRED` until backfilled.

## PluginEntry Model Properties

```python
entry.canonical_plugin_slug    # str | None — from registry YAML
entry.identity_status          # str | None — CANONICAL_IDENTITY_VERIFIED etc.
entry.effective_canonical_slug # computed: canonical_plugin_slug → URL last seg → plugin_slug
entry.is_identity_verified     # bool — True iff identity_status == CANONICAL_IDENTITY_VERIFIED
```

## Validator Module Path

`src/plugin_examples/fixture_factory/plugin_identity_validators.py`

Key exports: `run_plugin_identity_validators`, `PivResult`, `GENERIC_BARCODE_SLUGS`, `CANONICAL_BARCODE_SLUGS`
