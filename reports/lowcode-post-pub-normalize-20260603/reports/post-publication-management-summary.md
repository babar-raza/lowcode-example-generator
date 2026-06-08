# Post-Publication Management Summary

Date: 2026-06-03
Sprint: lowcode-post-pub-normalize-20260603

## 1. What Remains Published
44 LowCode C# examples across 6 families (.NET 8.0). All build and run from main.

## 2. Repos Checked and Touched

| Repository | Checked | Mutation |
|-----------|---------|----------|
| cells | Yes | None |
| diagram | Yes | Removed 2 legacy duplicate folders (PR #4) |
| email | Yes | None |
| pdf | Yes | Removed 1 legacy duplicate folder (PR #25) |
| slides | Yes | None |
| words | Yes | None |

## 3. Example Counts (post-normalization, all match intended)
cells=9, diagram=2, email=1, pdf=20, slides=3, words=9. Total=44.

## 4. E2E Patrol
44/44 build, 44/44 run. 132 raw logs. Output validation pass for all 4 key examples.

## 5. README and Branch Drift
None. All READMEs list all examples. All repos main-only, 0 open PRs.

## 6. FormImporter Watch
Aspose.PDF 26.5.0 (no newer). UPSTREAM_BUG unchanged.

## 7. Repairs Made
- Diagram PR #4: removed diagram-diagram-converter, diagram-pdf-converter
- PDF PR #25: removed pdf-aconverter
- Both merged, branches deleted, post-repair E2E passed

## 8. Next Trigger
- Aspose.PDF > 26.5.0 with FormImporter fix
- New LowCode API class in any family
- Existing example regression on newer SDK
