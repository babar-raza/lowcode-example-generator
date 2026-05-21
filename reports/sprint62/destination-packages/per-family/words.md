# Words Family — Destination Dry-Run Package

**Family:** words
**Repo:** aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples
**Version:** 26.4.0 (DRIFT from 26.5.0)
**Sprint:** 62

## Changes Planned

### 8 Example README Updates

| Example | Input | Output | Special Case |
|---------|-------|--------|--------------|
| comparer | `.docx` | `.docx` | No |
| converter | `.docx` | `.pdf` | No |
| mail-merger | `template.docx` + merge data | `.docx` | YES — SC-08 |
| merger | `.docx` | `.docx` | No |
| replacer | `.docx` | `.docx` | No |
| report-builder | `template.docx` + data object | `.docx` | YES — SC-09 |
| splitter | `.docx` | `.docx` | No |
| watermarker | `.docx` | `.docx` | No |

### Root README Update

Add I/O formats table with 8-row table. mail-merger and report-builder rows use special case text.

### Directory.Packages.props Version Update (Phase 5)

```xml
<!-- Before -->
<PackageVersion Include="Aspose.Words" Version="26.4.0" />

<!-- After -->
<PackageVersion Include="Aspose.Words" Version="26.5.0" />
```

## Status

- **Version drift:** 26.4.0 → 26.5.0 (MINOR drift, must be fixed)
- **Approval required:** APPROVE_README_PUSH
- **Dry-run path:** workspace/pr-dry-run/words-controlled-pilot/
- **Package status:** DRY_RUN_READY_WITH_VERSION_DRIFT
- **Note:** Version update and README update must be in the same PR
