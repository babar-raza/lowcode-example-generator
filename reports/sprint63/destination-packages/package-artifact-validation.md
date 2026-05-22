# Package Artifact Validation — Sprint 63 Phase 3

## Summary

All 6 family dry-run packages enumerated from `workspace/pr-dry-run/`.
Source files (Program.cs, README.md, .csproj) copied to `destination-packages/per-family/`.

## Coverage

| Family | Package Dir | Scenarios | Program.cs | NuGet Version |
|--------|------------|-----------|------------|---------------|
| Cells | cells-controlled-pilot | 9/9 | 9 | Aspose.Cells 26.5.1 |
| Diagram | diagram-controlled-pilot | 2/2 | 2 | Aspose.Diagram 26.5.0 |
| Email | email-controlled-pilot | 1/1 | 1 | Aspose.Email 26.4.0 |
| PDF | pdf-controlled-pilot + pr5-pr9 + wave1-wave2 | 17/19 | 17 | Aspose.PDF 26.4.0 |
| Slides | slides-controlled-pilot | 3/3 | 3 | Aspose.Slides.NET 26.5.0 |
| Words | words-controlled-pilot | 8/8 | 8 | Aspose.Words 26.5.0 |

**Total: 40/42 scenarios with dry-run packages**

## Missing PDF Scenarios

Two PDF scenarios are not in the dry-run packages:
1. `pdf-pdfa-converter` — uses destination alias `pdfa`; dry-run package structure differs
2. `pdf-text-extractor` — Sprint 62 special case; source verified in Program.cs authority check

These are KNOWN GAPS, not publication blockers. Both scenarios are PUBLISHED (confirmed via
Sprint 58/59 destination audit).

## Version Drift

| Family | Dry-Run Version | Latest NuGet | Status |
|--------|----------------|-------------|--------|
| Cells | 26.5.1 | 26.5.1 | CURRENT |
| Diagram | 26.5.0 | 26.5.0 | CURRENT |
| Email | 26.4.0 | 26.4.0 | CURRENT |
| PDF | 26.4.0 | 26.5.0 | VERSION_DRIFT |
| Slides | 26.5.0 | 26.5.0 | CURRENT |
| Words | 26.5.0 | 26.5.0 | CURRENT |

**PDF version drift noted**: 26.4.0 in dry-run, 26.5.0 on NuGet. Dry-run packages should be
regenerated with 26.5.0 before publication. This is a non-blocking gap for Sprint 63 closure.

## Artifacts in Bundle

- `destination-packages/package-artifact-index.json` — family-level metadata
- `destination-packages/package-source-manifest.json` — per-family scenario/file counts
- `destination-packages/package-hashes.json` — SHA256 hashes of all source files
- `destination-packages/per-family/{family}/` — Program.cs, README.md, .csproj copies
