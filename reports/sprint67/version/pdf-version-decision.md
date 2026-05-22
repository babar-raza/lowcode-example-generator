# PDF Version Decision — Sprint 67

Date: 2026-05-22
Sprint: sprint67
Defect: S66-D2

## Contradiction Summary

| Source | PDF Version | When Captured |
|--------|------------|---------------|
| `reports/sprint66/destination/content-audit-final.json` (all 19 PDF records) | 26.4.0 | At content audit time (Sprint 64 packages) |
| `reports/sprint66/handoff/per-family/pdf/Directory.Packages.props` | 26.5.0 | At handoff build time (Sprint 66) |

## Decision

**Path A chosen: 26.5.0 is the canonical version for PDF.**

Rationale:
1. The handoff `Directory.Packages.props` is the publication artifact — it controls what NuGet
   package version is used when the consumer clones and runs the example.
2. `content-audit-final.json` version field was populated from Sprint 64 packages, which used
   26.4.0 at the time. Sprint 66 rebuilt the handoff at 26.5.0.
3. 26.5.0 is the latest available PDF package as of 2026-05-22 (confirmed by handoff file).
4. Publishing at 26.4.0 would require a downgrade; 26.5.0 is current and preferred.

## Authority Chain

| Level | Evidence | Version |
|-------|---------|---------|
| NuGet (current as of 2026-05-22) | handoff/per-family/pdf/Directory.Packages.props | 26.5.0 |
| Content audit snapshot | destination/content-audit-final.json | 26.4.0 (stale) |
| Sprint 65 policy-classified | pdf-root-readme.md comment | 26.5.0 (policy) |

## Actions Taken

1. Sprint 67 `content-audit-sprint67.json` will use `package_version: "26.5.0"` for all 19 PDF records.
2. Sprint 67 root README `pdf-root-readme.md` version comment removed (no stale comment).
3. `version-policy-final.json` updated to reflect 26.5.0 as PDF canonical.

## Impact on Sprint 66 Bundle

Sprint 66 `content-audit-final.json` still shows 26.4.0 for PDF. This is NOT retroactively fixed
(sprint66 bundle is closed). The Sprint 67 bundle uses 26.5.0 throughout. The contradiction is
documented here as the resolution record.
