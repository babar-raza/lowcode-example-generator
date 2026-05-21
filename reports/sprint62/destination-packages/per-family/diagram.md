# Diagram Family — Destination Dry-Run Package

**Family:** diagram
**Repo:** aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples
**Version:** 26.4.0 (DRIFT from 26.5.0)
**Sprint:** 62

## Changes Planned

### 2 Example README Updates

| Example | Input | Output | Special Case |
|---------|-------|--------|--------------|
| diagram-converter | `.vsdx` | `.vdx` | No |
| pdf-converter | `.vsdx` | `.pdf` | No |

### Root README Update

Add I/O formats table with 2-row table.

### Directory.Packages.props Version Update (Phase 5)

```xml
<!-- Before -->
<PackageVersion Include="Aspose.Diagram" Version="26.4.0" />

<!-- After -->
<PackageVersion Include="Aspose.Diagram" Version="26.5.0" />
```

## Status

- **Version drift:** 26.4.0 → 26.5.0 (MINOR drift, must be fixed)
- **Approval required:** APPROVE_README_PUSH
- **Dry-run path:** workspace/pr-dry-run/diagram-controlled-pilot/
- **Package status:** DRY_RUN_READY_WITH_VERSION_DRIFT
- **Note:** Version update and README update must be in the same PR
