# Replay Justification -- email

**Run ID**: pilot-email-20260529-220716
**Base Run**: pilot-email-20260528-142456
**Replay Mode**: `--replay-from generation`

## Justification

A fresh NuGet catalog download for `email` was avoided by replaying from `pilot-email-20260528-142456`, which has a verified api-catalog with matching denominator hash. The `--replay-from generation` mode skips `dependency_resolution`, `extraction`, `nuget_fetch`, and `reflection`, but re-runs all stages from `scenario_planning` onward including **generation** (with durable-fix templates applied), **validation** (dotnet build + run), **reviewer**, **publisher**, and **gates**.

## Durable Fixes Applied

No new fixes for this family in this sprint. Templates from prior sprint still active.
