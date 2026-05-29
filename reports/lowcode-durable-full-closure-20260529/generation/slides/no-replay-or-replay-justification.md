# Replay Justification -- slides

**Run ID**: pilot-slides-20260529-221814
**Base Run**: pilot-slides-20260528-143001
**Replay Mode**: `--replay-from generation`

## Justification

A fresh NuGet catalog download for `slides` was avoided by replaying from `pilot-slides-20260528-143001`, which has a verified api-catalog with matching denominator hash. The `--replay-from generation` mode skips `dependency_resolution`, `extraction`, `nuget_fetch`, and `reflection`, but re-runs all stages from `scenario_planning` onward including **generation** (with durable-fix templates applied), **validation** (dotnet build + run), **reviewer**, **publisher**, and **gates**.

## Durable Fixes Applied in This Run

- `Convert`: `template_first: true` -- uses deterministic C# template from `_generate_deterministic_template_for_scenario`
