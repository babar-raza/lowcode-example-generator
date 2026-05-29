# Replay Justification -- diagram

**Run ID**: pilot-diagram-20260529-221021
**Base Run**: pilot-diagram-20260528-142424
**Replay Mode**: `--replay-from generation`

## Justification

A fresh NuGet catalog download for `diagram` was avoided by replaying from `pilot-diagram-20260528-142424`, which has a verified api-catalog with matching denominator hash. The `--replay-from generation` mode skips `dependency_resolution`, `extraction`, `nuget_fetch`, and `reflection`, but re-runs all stages from `scenario_planning` onward including **generation** (with durable-fix templates applied), **validation** (dotnet build + run), **reviewer**, **publisher**, and **gates**.

## Durable Fixes Applied in This Run

- `DiagramConverter`: `template_first: true` -- uses deterministic C# template from `_generate_deterministic_template_for_scenario`
- `PdfConverter`: `template_first: true` -- uses deterministic C# template from `_generate_deterministic_template_for_scenario`
