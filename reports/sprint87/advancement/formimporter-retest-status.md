Sprint 87 — FormImporter Retest Status
========================================
Date: 2026-05-25
Author: Lane 2

## Current Status: BLOCKED_EXTERNAL

### Bug Description
- **Component**: Aspose.PDF FormImporter LowCode API
- **Package**: Aspose.PDF for .NET 26.5.0
- **Error**: NullReferenceException during FormImporter.Process()
- **Repro**: `workspace/defect-repros/pdf-formimporter-nullref/`
- **First observed**: Sprint 75
- **Carry-forward**: Sprint 75 → 76 → 77 → 78 → 79 → 80 → 81 → 82 → 83 → 84 → 85 → 86 → 87

### Retest Conditions
The FormImporter bug is triggered by Aspose.PDF internal code, not by our pipeline.
Retesting requires a new Aspose.PDF release (>26.5.0) that fixes the NullRef.

### Sprint 87 Retest Check
- Current pinned version: 26.5.0
- Latest available version: NOT CHECKED (would require NuGet API call)
- Trigger: `pipeline/configs/families/pdf.yml` has `version_policy: latest-stable`
- TRG-01 auto-fires when NuGet version > 26.5.0

### Action Items
- No retest performed this sprint (no new Aspose.PDF version confirmed)
- FormImporter excluded from README I/O publication scope
- 18/19 PDF examples are publishable (FormImporter is the 19th)

### Resolution Path
1. Aspose releases PDF >26.5.0 with NullRef fix
2. TRG-01 fires on next discovery sweep
3. Re-run FormImporter repro script
4. If pass: remove BLOCKED_EXTERNAL, add FormImporter to publication scope
5. If fail: update pinned version, carry forward BLOCKED_EXTERNAL
