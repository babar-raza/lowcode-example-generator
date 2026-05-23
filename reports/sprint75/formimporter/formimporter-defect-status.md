# Sprint 75 — FormImporter Defect Status

**Date:** 2026-05-23
**Defect:** TC-PDF-FORMIMPORTER-RETEST
**Sprint 75 classification:** BLOCKED_EXTERNAL

## Summary

FormImporter remains blocked by an upstream NullReferenceException bug in Aspose.PDF 26.5.0.
The latest available NuGet version is 26.5.0 — no newer version has been published.
No retest is warranted this sprint.

## Defect Details

| Field | Value |
|-------|-------|
| Component | Aspose.PDF.LowCode.FormImporter |
| Exception | NullReferenceException in `Forms.Form.#=zZQILclhNTKUB` |
| Defect version | 26.5.0 |
| Latest NuGet version | 26.5.0 (confirmed 2026-05-23 via `dotnet package search`) |
| Version advanced beyond defect | false |
| Retest triggered | false |
| Prior retest cycles | Multiple: sprints 45-49, mega-train-005 |
| Repro path | `workspace/defect-repros/pdf-formimporter-nullref/` |
| Repro files | Program.cs, formimporter-repro.csproj, minimal-form.pdf, minimal-form-data.json |
| Watch automation | `src/plugin_examples/package_watcher/formimporter_watch.py` |

## NuGet Check Result (2026-05-23)

```
dotnet package search Aspose.PDF --format json --take 1
→ latestVersion: "26.5.0"
→ Version advanced beyond defect: false
→ Retest NOT triggered
```

## Impact on PDF Denominator

- Total PDF scenarios in scope: 19 (FormImporter excluded from denominator)
- If FormImporter is fixed in future version: PDF would become 20 scenarios
- Conservation: 19 = all remote examples verified

## Retest Trigger Condition

A retest will be triggered automatically when:
`Aspose.PDF NuGet latestVersion > 26.5.0`

The watch script (`formimporter_watch.py`) will:
1. Detect version advance
2. Upgrade `formimporter-repro.csproj` to new version
3. Run `dotnet run` in repro harness
4. Check for NullReferenceException resolution
5. Update taskcard with pass/fail result

## Classification

- **Weekly Review Item 2:** BLOCKED_EXTERNAL
- FormImporter is not forgotten.
- Taskcard TC-PDF-FORMIMPORTER-RETEST is active and current.
- No pipeline action possible until upstream bug is fixed.
