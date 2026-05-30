# Environment Proof — LANE 0

**Sprint ID**: lowcode-final-closure-pass3-20260530
**Date**: 2026-05-30
**Start time (UTC)**: 2026-05-30T04:39:45Z

## Git State

- Branch: main
- HEAD SHA: 35005a6fec84cfc7578222d99414e6c7a02f2bc2
- Working tree: 2 untracked files (classified in dirty-state-classification.md)
  - `.kilo/` — gitignored (line 67 in .gitignore), VS Code Kilo AI extension state, not sprint artifact
  - `docs/development/open-taskcard-closure-matrix.md` — generated file, not gitignored, requires disposition

## Python Environment

- Python path: C:/Python313/python.exe
- Python version: 3.13.2
- venv: .venv/Scripts/python.exe (for pytest)

## .NET SDK

- SDK version: 10.0.204

## NuGet Sources

1. nuget.org (Enabled) — https://api.nuget.org/v3/index.json
2. Microsoft Visual Studio Offline Packages (Enabled) — C:\Program Files (x86)\Microsoft SDKs\NuGetPackages\

## OS

- Platform: win32 / MINGW64_NT-10.0-26200 (Windows 11 Pro 10.0.26200)
- Machine: ALIENWARE-M18

## Approval Gates

- PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL: NOT_SET
- PLUGIN_EXAMPLES_MERGE_PR_APPROVAL: NOT_SET

**Push is prohibited.** Live PRs cannot be created.

## Prior Sprint

- Sprint: lowcode-durable-full-closure-20260529
- HEAD at prior sprint close: 35005a6fec84cfc7578222d99414e6c7a02f2bc2
- ZIP: .local/evidence-bundles/lowcode-durable-full-closure-20260529-evidence.zip
- Verdict assigned by reviewer: DURABLE_GENERATOR_REPAIR_PROGRESS_ACCEPTED_FULL_CLOSURE_NOT_YET_ACCEPTED

## This Sprint Objective

Convert durable repair progress into final trustworthy closure with:
- Raw bundled command logs
- Raw dotnet restore/build/run logs for all 42 examples
- Actual generated source snapshots (not just tree lists)
- Full pytest suite (not just durable-fix unit tests)
- No-replay proof or strict replay contract
- Verification/latest promotion (fix stale diagram publisher)
- Reviewer/fallback-review semantics defined
- 42 validation vs 41 PR-candidate truth model
- Local publication package dry-run for all eligible families
- External blocker raw NuGet proofs
