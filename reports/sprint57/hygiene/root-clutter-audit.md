# Root Clutter Audit — Sprint 57

**Sprint:** 57
**Date:** 2026-05-21
**Lane:** E

## Artifacts Found and Removed

The following files/directories existed at the repo root and were removed during Sprint 57 Phase 5:

| File/Dir | Size | Date | Source | Action |
|----------|------|------|--------|--------|
| `input.pdf` | 29 KB | 2026-05-19 | PDF generation run | REMOVED |
| `output.pdf` | 616 KB | 2026-05-19 | PDF generation run | REMOVED |
| `test.pfx` | 2 KB | 2026-05-19 | Security example run | REMOVED |
| `leg.zip` | 12 MB | 2026-05-21 | Sprint bundle | REMOVED |
| `output.jpg/` | dir | 2026-05-19 | JPEG extraction run | REMOVED |
| `output.png/` | dir | 2026-05-21 | PNG extraction run | REMOVED |
| `input.pptx` | 34 KB | 2026-05-19 | Slides generation run | REMOVED |
| `output.pptx` | 19 KB | 2026-05-19 | Slides generation run | REMOVED |
| `output.json` | 1 KB | 2026-05-19 | JSON generation run | REMOVED |
| `input.vsdx` | — | — | Diagram generation run | REMOVED |
| `output.tiff/` | dir | 2026-05-19 | TIFF extraction run | REMOVED |

**Total artifacts removed:** 11 files/directories

## Root State After Cleanup

```
repo root/
├── .gitignore
├── .gitattributes
├── global.json
├── pyproject.toml
├── README.md
├── CHANGELOG.md (if any)
├── pipeline/
├── src/
├── tests/
├── reports/
├── generated/
└── workspace/ (gitignored except queues, manifests, verification/latest)
```

**Result:** CLEAN — no artifact files at root.

## Policy Going Forward

Generated outputs must live under `workspace/runs/{run-id}/outputs/` or `generated/{scenario-id}/`.
Source fixtures must live under `workspace/fixtures/` or within the generated project.
No files from generation runs should be left at the repo root.

The `.gitignore` has `workspace/runs/` excluded from git, which prevents accidental staging of outputs.
Root artifact creation by the pipeline is a process defect — runners must clean up after themselves.

## .gitignore Compliance Check

Current `.gitignore` at root:
- `workspace/runs/*/` — runs excluded ✓
- `workspace/fixture-validation/` — excluded ✓
- `workspace/pr-dry-run/` — excluded ✓
- `workspace/verification/*.zip` — bundle zips excluded ✓
- `/workspace` — only applies to root-level workspace directory (but workspace is tracked through force-add) ✓

Root artifact files (`*.pdf`, `*.pptx`, etc.) are NOT explicitly gitignored at root.
**Recommendation:** Add root-level artifact patterns to `.gitignore`:
```
# Root-level artifact files (should never be at root)
/*.pdf
/*.docx
/*.xlsx
/*.pptx
/*.vsdx
/*.json
/*.pfx
/*.tiff
/*.png
/*.jpg
# Except package-managed JSON files
!pyproject.toml
!global.json
```
