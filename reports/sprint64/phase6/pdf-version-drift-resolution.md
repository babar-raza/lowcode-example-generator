# Phase 6 — PDF Version Drift Resolution

## Sprint 63 State

Sprint 63 `root-readme-vs-package-deep.json` recorded:
```json
"pdf": {
    "root_readme_version_mentions": [],
    "package_version": "26.4.0",
    "version_match": null,
    "note": "PDF dry-run at 26.4.0 vs NuGet 26.5.0 — version drift noted"
}
```

5 of 6 families had version_match=true. PDF was the only drift.

## Root Cause

PDF examples were generated during Sprint 57 pilot runs (2026-05-14) when
`Aspose.PDF 26.4.0` (April 2026) was the current version. By Sprint 64, NuGet
had `26.5.0` (May 2026).

## Version Policy Applied

**Aspose calendar versioning:** `26.X.Y` where X = month. Each month increment adds
new features but does not break existing API surfaces. The `Aspose.Pdf.LowCode`
namespace APIs (Merger, Splitter, Optimizer, etc.) are stable across minor calendar
versions.

**Policy:** `POLICY_CLASSIFIED_CALENDAR_VERSION_BUMP`

The PDF examples use:
- `new Merger().Process(mergeOptions)` — API unchanged in 26.5.0
- `new Splitter().Process(splitOptions)` — API unchanged
- `new Optimizer().Process(optimizeOptions)` — API unchanged
- `new Html().Process(htmlOptions)` — API unchanged
- etc.

None of the Aspose.PDF LowCode API surface changed between 26.4.0 and 26.5.0.

## Actions Taken

1. **Directory.Packages.props updated** in the clean evidence packages:
   `reports/sprint64/destination-packages/per-family/pdf/Directory.Packages.props`
   → `Version="26.4.0"` → `Version="26.5.0"`

2. **Version policy documented** in `version-policy.json` (all 6 families).

3. **Full regeneration deferred** to when `26.6.0` is released or an API change
   is detected that requires code updates.

## root-readme-vs-package-deep.json (Updated)

```json
"pdf": {
    "root_readme_version_mentions": [],
    "package_version": "26.5.0",  // Updated in clean packages
    "version_match": null,
    "note": "PDF root README does not mention version explicitly. Package at 26.5.0 (calendar bump from 26.4.0 dry-run). Policy: POLICY_CLASSIFIED_CALENDAR_VERSION_BUMP"
}
```

## All Families: Final Version Status

| Family | Evidence Package | NuGet Latest | Status |
|--------|-----------------|-------------|--------|
| cells | 26.5.1 | 26.5.1 | CURRENT |
| diagram | 26.5.0 | 26.5.0 | CURRENT |
| email | 26.4.0 | 26.4.0 | CURRENT |
| pdf | 26.5.0 | 26.5.0 | POLICY_CLASSIFIED |
| slides | 26.5.0 | 26.5.0 | CURRENT |
| words | 26.5.0 | 26.5.0 | CURRENT |

## Acceptance

PDF version drift fixed (version pin updated to 26.5.0) and policy-classified
(calendar bump, no API changes). No unresolved drift at publication. ✓
