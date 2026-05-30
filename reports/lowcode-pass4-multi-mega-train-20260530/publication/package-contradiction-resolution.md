# Package Contradiction Resolution — Pass 4

Sprint: lowcode-pass4-multi-mega-train-20260530
Date: 2026-05-30

## Prior Contradiction

Prior sprint (multi-mega-train) had two conflicting documents:
1. `package-completion-report.json` (Lane F) — reported all 6 families COMPLETE
2. `validation-truth-model.json` (Lane D) — reported diagram/slides/email MISSING

## Root Cause

The `validation-truth-model.json` was written in Lane D BEFORE Lane F created the diagram/slides/email
packages. It was never updated. The truth model was stale, not the package report.

## Current Package Reality (Pass 4 ground truth)

| Family | Packages | Examples | PR Candidates |
|--------|---------|----------|---------------|
| cells  | cells-controlled-pilot | 9 | 9 |
| words  | words-controlled-pilot | 8 | 7 (comparer advisory) |
| pdf    | pdf-controlled-pilot, pr5–pr9, pr10 (7 total) | 19 | 19 |
| diagram | diagram-controlled-pilot | 2 | 2 |
| slides  | slides-controlled-pilot | 3 | 3 |
| email   | email-controlled-pilot  | 1 | 1 |
| **Total** | **12 packages** | **42** | **41** |

## PDF Package Detail (7 packages, 19 examples)

| Package | Count | Examples |
|---------|-------|----------|
| pdf-controlled-pilot | 3 | doc-converter, html, xls-converter |
| pdf-controlled-pilot-pr5 | 3 | jpeg, png, tiff |
| pdf-controlled-pilot-pr6 | 3 | image-extractor, table-generator, toc-generator |
| pdf-controlled-pilot-pr7 | 2 | form-flattener, security |
| pdf-controlled-pilot-pr8 | 2 | form-editor, form-exporter |
| pdf-controlled-pilot-pr9 | 1 | signature |
| pdf-controlled-pilot-pr10 | 5 | merger, optimizer, splitter, pdf-aconverter, text-extractor |
| **Total** | **19** | |

## Assembly Mechanism

All packages created via system scripts:
- `scripts/assemble_controlled_pilots.py` — cells, words, diagram, slides, email + pdf pr1-pr9
- `scripts/assemble_pdf_pr10_pilot.py` — pdf pr10 (5 template-repaired examples)

pr10 source: `workspace/runs/pilot-pdf-repair-20260530/generated/pdf/`

## Verdict

- All 6 families have publication packages: **CONFIRMED**
- No contradiction: truth model (Lane D) was stale, package report (Lane F) was correct
- All 12 packages on disk: **VERIFIED**
- 42 examples total: **CONFIRMED**
- 41 PR candidates: **CONFIRMED** (42 minus words-comparer advisory exclusion)
