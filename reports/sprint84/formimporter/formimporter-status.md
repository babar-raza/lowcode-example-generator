Sprint 84 — FormImporter Status
=================================
Date: 2026-05-24
Author: Lane F

## Status: BLOCKED_EXTERNAL (carry-forward)

## Summary
Aspose.PDF FormImporter (Wave H, 20th example type) is blocked by a library bug in Aspose.PDF 26.5.0.
NullReferenceException occurs in FormImporter.Process() when NuGet version > 26.5.0.

## Evidence
- Defect repro preserved: workspace/defect-repros/pdf-formimporter-nullref/
- TRG-01 fires when NuGet version > 26.5.0 (regression trigger)
- Bug reported to Aspose.PDF team

## Classification
BLOCKED_EXTERNAL — pipeline cannot resolve; waiting on Aspose.PDF fix.

## Sprint 84 Action
None. Carry-forward only. No new repro data this sprint.

## When Resolved
Monitor Aspose.PDF changelog for fix. When fixed:
1. Update defect-repros with repaired state
2. Unblock Wave H in PDF allowed_types
3. Generate FormImporter example
