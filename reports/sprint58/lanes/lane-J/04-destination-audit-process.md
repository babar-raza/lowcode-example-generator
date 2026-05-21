# Process: Destination Repo Deep Audit

**Process ID:** LANE-J-04
**Version:** Sprint 58
**Date:** 2026-05-21

---

## Overview

Sprint 57 Defect D07: `destination-repo-audit.json` confirmed file paths exist but did NOT verify: Program.cs content correctness, manifest versions, package version alignment, or README accuracy.

Sprint 58 requires a **deep** destination audit — per-example content verification.

---

## Target Repositories

| Family | Target Repo |
|--------|-------------|
| Cells | `aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples` |
| Words | `aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples` |
| PDF | `aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples` |
| Diagram | `aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples` |
| Email | `aspose-email-net/Aspose.Email.LowCode-for-.NET-Examples` |
| Slides | `aspose-slides-net/Aspose.Slides.LowCode-for-.NET-Examples` |

---

## Process Steps

### Step 1: Enumerate Examples per Family

For each family, list all example directories in the target repo via GitHub API:
```
GET /repos/{owner}/{repo}/contents/Examples
```

### Step 2: Deep Content Verification

For each example directory:
1. Verify `Program.cs` exists
2. Verify `{ExampleName}.csproj` exists
3. Check NuGet package version in `.csproj` matches expected version
4. Verify `README.md` exists
5. Check `Directory.Packages.props` for centrally managed versions

### Step 3: Count Verification

Expected counts:
- Cells: 9, Words: 8, PDF: 19, Diagram: 2, Email: 1, Slides: 3
- Total: 42

### Step 4: Package Version Alignment

Expected NuGet versions:
| Family | Expected Version |
|--------|----------------|
| Cells | 26.5.1 |
| Words | 26.5.0 |
| PDF | 26.5.0 |
| Diagram | 26.5.0 |
| Email | 26.4.0 |
| Slides | 26.5.0 |

### Step 5: Write Audit Output

Write to: `reports/sprint58/destination/deep-destination-audit.json`

Required fields per example:
```json
{
  "scenario_id": "...",
  "family": "...",
  "program_cs_present": true,
  "csproj_present": true,
  "readme_present": true,
  "package_version": "26.5.1",
  "version_match": true,
  "content_verified": true
}
```

---

## Acceptance Criteria

- All 42 examples: `content_verified=true`
- All 42 examples: `version_match=true`
- All 42 examples: `readme_present=true`
- Overall verdict: `FULLY_VERIFIED`
