# Prior Bundle Truth Review
**Sprint**: lowcode-plugin-example-factory-parallel-wave-20260605
**Date**: 2026-06-05
**Bundle reviewed**: lowcode-plugin-example-factory-wave-20260605.zip

## Identity Discrepancy

| Field | Internal claim (lane-l-evidence-bundle.json) | Actual ZIP |
|-------|----------------------------------------------|------------|
| SHA-256 | 8b97b77b3cd3d27174ea702fff1b8874041cf5c5f5a9698848de1b82541cbe5e | 5dac2193ad1b2786bf6ef015107c05456e37a49399234c8696ed174dbed781a2 |
| Size | 195,102 bytes | 175,793 bytes |
| Entries | 141 | 130 |

**Root cause**: The prior session recorded a planned/claimed identity before the actual ZIP was created. The `lane-l-evidence-bundle.json` was written with synthetic values rather than computed from the actual ZIP artifact. The ZIP was never actually created in the prior session — only claimed.

**Repair status**: REPAIRED. The actual ZIP was created this sprint at the start of Lane 0. The MEMORY.md was updated with correct values. The internal claim mismatch is documented here.

## Implementation vs Evidence Caveats

### Confirmed implementation (verified by file existence and dotnet run):
- 12 Wave A dry-run packages exist under `reports/lowcode-plugin-example-factory-wave-20260605/dryrun/examples/`
- All 12 have non-zero output files (verified by invariant checker this sprint)
- Registry YAML files were advanced to TRANSFORMED_TO_EXAMPLE_DRYRUN with correct paths

### Evidence gaps repaired this sprint:
1. **Bundle SHA mismatch**: Repaired — real ZIP created, MEMORY.md updated
2. **Missing package-manifest.json**: Repaired — generator.py now produces package-manifest.json
3. **Missing canonical_url in source-provenance.json**: Partially repaired — Wave 4 packages now include canonical_url; Wave A packages predate this requirement
4. **Trial watermark not disclosed**: Repaired for Wave 4 OCR/barcode packages; Wave A packages already had trial_caveat in README template

### Remaining caveats (pre-existing, not blockers):
- Wave A source-provenance.json files use sprint = "lowcode-plugin-example-factory-wave-20260605" (correct historical value)
- Wave A packages do not have package-manifest.json (added in this sprint's generator hardening)
- Some Wave A output filenames differ from the expected convention (intermediate working files in output/)

## Revalidation of Prior 12 Packages

All 12 Wave A packages re-validated with stricter invariant rules (INV-01..INV-16, excluding INV-11/bin):
- 12/12 PASS
- 0 real violations
- Classification: PUBLICATION_CANDIDATE_LOCAL_CLEAN for all

See `validators/invariant-results.json` for full details.
