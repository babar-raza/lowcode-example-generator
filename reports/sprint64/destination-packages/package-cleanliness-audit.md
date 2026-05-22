# Package Artifact Cleanliness Audit — Sprint 64 Phase 3

## Summary

**Sprint 63 Defect S63-D3:** Package artifacts included `obj/` intermediate build files
from MSBuild compilation. These are not source artifacts and should not be included in
evidence bundles.

## Sprint 64 Fix

Package extraction was rebuilt to include only:
- `Program.cs` — generated example source
- `README.md` — documentation
- `*.csproj` — project file
- `Directory.Packages.props` — NuGet version pinning

**Excluded:** `obj/`, `bin/`, `.vs/`, `.vscode/`, any other non-source files.

## Cleanliness Check Results

| Family | Scenarios | Clean Files | obj/ Files | bin/ Files |
|--------|-----------|-------------|------------|------------|
| cells | 9 | 28 | 0 | 0 |
| diagram | 2 | 7 | 0 | 0 |
| email | 1 | 4 | 0 | 0 |
| pdf | 17 | 52 | 0 | 0 |
| slides | 3 | 10 | 0 | 0 |
| words | 8 | 25 | 0 | 0 |
| **Total** | **40** | **126** | **0** | **0** |

**Result: CLEAN — no obj/ or bin/ contamination.**

## Special Cases (2 PDF Scenarios)

Two PDF scenarios are not in the standard dry-run pipeline:

| Scenario | API Type | Classification | Source |
|----------|----------|----------------|--------|
| pdf-pdf-aconverter | PdfAConverter | SPECIAL_CASE_NO_DRY_RUN | pilot-pdf-20260514-211320 |
| pdf-text-extractor | TextExtractor | SPECIAL_CASE_NO_DRY_RUN | pilot-pdf-20260514-211320 |

These were generated during Sprint 57 PDF pilot runs. They are excluded from the
standard dry-run packaging pipeline (no `workspace/pr-dry-run/` directory exists).
Their clean Program.cs, README.md, and .csproj files are stored in:
`reports/sprint64/destination-packages/special-cases/`

## Total Coverage

- Standard scenarios: 40/40 (9+2+1+17+3+8)
- Special cases: 2/2 (pdf-pdfa-converter, pdf-text-extractor)
- **Total: 42/42** (100%)

## Acceptance

42/42 scenarios represented by clean artifacts or explicit special-case classification.
No obj/ or bin/ intermediate build files included in any package artifact.
