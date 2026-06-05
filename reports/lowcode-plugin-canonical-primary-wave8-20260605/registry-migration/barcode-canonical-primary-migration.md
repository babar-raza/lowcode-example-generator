# BarCode Canonical-Primary Migration

Sprint: lowcode-plugin-canonical-primary-wave8-20260605
Date: 2026-06-05

## Migrated Entries

| Legacy Slug | Canonical Primary |
|-------------|------------------|
| generate-barcode | 1d-barcode-writer |
| recognize-barcode | 1d-barcode-reader |
| generate-qr-code | 2d-barcode-writer |
| scan-barcode | 2d-barcode-reader |

## Fields Updated

- `plugin_slug`: set to canonical slug
- `legacy_aliases`: old slug preserved
- `identity_status`: CANONICAL_IDENTITY_VERIFIED
- `migration_status`: CANONICAL_PRIMARY_MIGRATED
- `migrated_from`: old slug
- `dryrun_package_path`: updated to Wave 7 canonical path
