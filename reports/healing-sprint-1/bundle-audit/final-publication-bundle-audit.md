# Healing Sprint 1 — Lane 5: Final Publication Bundle Audit

**Lane:** 5 — Evidence Contract / Bundle Structure Healing
**Date:** 2026-05-27

## Bundle Under Audit

`reports/final-publication/bundles/final-publication-closure-evidence-20260527.zip`

## File Count

- Bundle file count: **42**
- bundle-manifest.json present in bundle: **YES**
- bundle-manifest.json `file_count`: 42
- Match: **YES**

## Bundle Composition

The bundle contains all files under `reports/final-publication/` excluding:
- The `bundles/` directory itself
- Any `*.zip` files

This matches the build script at `scripts/build_final_publication_bundle.py`:
```python
for f in sorted(sprint_dir.rglob("*")):
    if f.is_file() and "bundles" not in f.parts and not f.name.endswith(".zip"):
        files_to_include.append(f)
```

## Structural Checks

| Check | Result |
|---|---|
| ZIP file exists | YES |
| ZIP file size | 36,924 bytes (non-zero) |
| File count matches manifest | YES (42 == 42) |
| bundle-manifest.json present | YES |
| ZIP is not corrupt | YES (opened successfully) |

## Key File Presence in Bundle

| File | In Bundle |
|---|---|
| reports/final-publication/final-verdict.md | YES |
| reports/final-publication/sprint-state.json | YES |
| reports/final-publication/evidence/final-validation-result.json | YES |
| reports/final-publication/evidence/evidence-contract-computed.json | YES |
| reports/final-publication/publication/publication-truth-matrix-final.json | YES |
| reports/final-publication/preflight/approval-check.md | YES |
| reports/final-publication/iv/independent-verification-report.md | YES |

## Lane 5 Bundle Audit Verdict

**BUNDLE_AUDIT_PASS** — 42 files, all key files present, ZIP valid, count consistent.
