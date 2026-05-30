# Final Denominator Model — 41/42/8 Resolution

Sprint: lowcode-pass4-multi-mega-train-20260530
Date: 2026-05-30

## The Numbers

| Metric | Count | Explanation |
|--------|-------|-------------|
| Total examples in publication packages | 42 | All 42 across 6 families |
| PR candidates (for merge) | 41 | 42 minus 1 advisory exclusion |
| Words PR candidates | 7 | 8 in package minus words-comparer (advisory) |

## Per-Family Breakdown (42 total)

| Family | Package(s) | Examples | PR Candidates |
|--------|-----------|----------|---------------|
| cells  | cells-controlled-pilot | 9 | 9 |
| words  | words-controlled-pilot | 8 | 7 (comparer advisory-excluded) |
| pdf    | pdf-controlled-pilot (3) + pr5–pr9 (2+2+3+2+2) + pr10 (5) = 19 total | 19 | 19 |
| diagram | diagram-controlled-pilot | 2 | 2 |
| slides  | slides-controlled-pilot | 3 | 3 |
| email   | email-controlled-pilot  | 1 | 1 |
| **Total** | **12 packages** | **42** | **41** |

## Words Comparer Exclusion

`words-comparer` is in the words package but NOT in the 41 PR candidates because:
- It uses `Aspose.Words.Comparison` API (comparison-specific, not the core LowCode pattern)
- Advisory exclusion: included in the package for completeness but gated from PR

This is consistent across the durable-full-closure sprint and all prior closure sprints.

## PDF Package Split (19 examples across 7 packages)

| Package | Examples |
|---------|----------|
| pdf-controlled-pilot | doc-converter, form-editor, form-exporter, form-flattener |
| pdf-controlled-pilot-pr5 | html, jpeg |
| pdf-controlled-pilot-pr6 | png, tiff |
| pdf-controlled-pilot-pr7 | image-extractor, pdf-aconverter, security |
| pdf-controlled-pilot-pr8 | signature, table-generator |
| pdf-controlled-pilot-pr9 | toc-generator, xls-converter |
| pdf-controlled-pilot-pr10 | merger, optimizer, splitter, pdf-aconverter (template-repaired), text-extractor |

Note: pdf-aconverter appears in both pr7 and pr10. The pr10 version is the template-repaired version assembled via `scripts/assemble_pdf_pr10_pilot.py`.

## Verdict

- 42/42 examples validated and in packages
- 41/41 PR candidates confirmed
- 8 words examples in package, 7 in PR scope
- No contradiction: the denominator is correct
