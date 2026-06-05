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

## Canonical-Primary Registry Model (Sprint Wave 8)

When a registry entry is canonical-primary, `plugin_slug` IS the canonical slug. Legacy generic slugs are in `legacy_aliases` only.

```yaml
- plugin_slug: 1d-barcode-writer          # IS the canonical slug
  canonical_plugin_slug: 1d-barcode-writer
  display_plugin_name: 1D Barcode Writer for .NET
  identity_status: CANONICAL_IDENTITY_VERIFIED
  migration_status: CANONICAL_PRIMARY_MIGRATED
  migrated_from: generate-barcode
  legacy_aliases:
    - generate-barcode
```

Use `loader.lookup_by_alias(family, old_slug)` to resolve legacy slugs to canonical entries.
Use `loader.canonical_primary_entries()` to get all 21 canonical-primary entries.

## CPV Validator Rules (CPV-01..CPV-12)

System-level validators. Run with: `run_canonical_primary_validators(packages, registry_entries, publication_matrix, family_plugin_lists)`

| Rule | Severity | Check |
|------|----------|-------|
| CPV-01 | ERROR | Publication candidate must not use legacy slug as primary |
| CPV-02 | ERROR | Canonical registry entry must have canonical_plugin_slug |
| CPV-03 | WARNING | Canonical registry entry must have display_plugin_name |
| CPV-04 | ERROR | Legacy alias must not be counted as separate canonical example |
| CPV-05 | ERROR | Dryrun path must use canonical slug, not generic slug without alias record |
| CPV-06 | WARNING | source-provenance canonical_url must match registry |
| CPV-07 | WARNING | README title must not use generic operation name |
| CPV-08 | ERROR | BarCode generic names must not appear in publication candidate list |
| CPV-09 | ERROR | publication matrix must not include identity_review_required as clean |
| CPV-10 | WARNING | Family-level probe must not count as plugin-level coverage |
| CPV-11 | WARNING | Canonical identity map must include family plugin list |
| CPV-12 | WARNING | Final summary must not count canonical and legacy aliases together |

CPV module: `src/plugin_examples/fixture_factory/canonical_primary_validators.py`

## FPP Validators (Full Package Proof — Wave 9)

FPP-01..FPP-12 validate that a package directory has complete proof files:

| Rule   | Severity | Check |
|--------|----------|-------|
| FPP-01 | ERROR    | Program.cs must exist |
| FPP-02 | ERROR    | *.csproj must exist |
| FPP-03 | WARNING  | README.md should exist |
| FPP-04 | ERROR    | source-provenance.json must exist |
| FPP-05 | WARNING  | package-manifest.json should exist |
| FPP-06 | WARNING  | restore.log should exist (root or logs/) |
| FPP-07 | WARNING  | build.log should exist (root or logs/) |
| FPP-08 | WARNING  | run.log should exist (root or logs/) |
| FPP-09 | ERROR    | output-validation.json must exist |
| FPP-10 | ERROR    | output/ must exist and be non-empty |
| FPP-11 | ERROR    | PASS verdict must not be claimed if FPP errors present |
| FPP-12 | WARNING  | METADATA_ONLY claimed but full package files present |

FPP module: `src/plugin_examples/fixture_factory/full_package_proof_validator.py`

## CCV Validators (Closeout Consistency — Wave 9)

CCV-01..CCV-14 validate sprint governance document consistency:

| Rule   | Severity | Check |
|--------|----------|-------|
| CCV-01 | ERROR    | Evidence bundle must not be PENDING when sprint verdict is COMPLETE |
| CCV-02 | ERROR    | Lane ledger lanes must not be PENDING when sprint verdict is COMPLETE |
| CCV-03 | ERROR    | Taskcards must not be PENDING when sprint verdict is COMPLETE |
| CCV-04 | ERROR    | Test log must exist when closeout claims test count |
| CCV-05 | WARNING  | Git status must be recorded when verdict is COMPLETE |
| CCV-06 | WARNING  | Commit proof must be recorded when verdict is COMPLETE |
| CCV-07 | ERROR    | CANONICAL_IDENTITY_VERIFIED entry must have canonical_url |
| CCV-08 | WARNING  | CANONICAL_IDENTITY_VERIFIED entry must have display_plugin_name |
| CCV-09 | ERROR    | Publication-clean candidates must have canonical_url |
| CCV-10 | ERROR    | Package claiming PASS must have Program.cs |
| CCV-11 | ERROR    | Package claiming PASS must have *.csproj |
| CCV-12 | WARNING  | Package claiming PASS should have log files |
| CCV-13 | ERROR    | Legacy alias slugs must not appear as publication candidates |
| CCV-14 | ERROR/W  | Publication matrix must include canonical_url column |

CCV module: `src/plugin_examples/fixture_factory/closeout_consistency_validators.py`

## Validator Module Path

`src/plugin_examples/fixture_factory/plugin_identity_validators.py`

Key exports: `run_plugin_identity_validators`, `PivResult`, `GENERIC_BARCODE_SLUGS`, `CANONICAL_BARCODE_SLUGS`
