# Docs Refactor Report

Date: 2026-05-11

## Summary

The docs tree was reorganized from scattered planning, discovery, and publishing reports into a smaller information architecture:

- `docs/README.md` is now the single docs landing page.
- Canonical references were created under `docs/reference/`.
- Scenario docs were created under `docs/guides/`.
- Operator runbooks were created under `docs/operations/`.
- Architecture docs were created under `docs/architecture/`.
- Contributor docs were created under `docs/development/`.
- Historical and merged source docs were moved under `docs/_archive/`.
- Existing audit outputs remain under `docs/_audit/`.

The repo root `README.md` now points to `docs/README.md` and the most important workflows. `AGENTS.md` now points to the active governance page at `docs/architecture/decisions.md` because the old execution plan moved to the archive.

## Moves, Merges, and Splits

High-level migration:

- Root orphans were removed from `docs/` root:
  - `docs/monthly-runbook.md` moved to `docs/_archive/root-orphans/monthly-runbook.md`; durable content merged into `docs/operations/monthly-maintenance.md`.
  - `docs/verifier-integration.md` moved to `docs/_archive/root-orphans/verifier-integration.md`; durable content merged into `docs/reference/validation-and-reviewer.md`.
- `docs/ci/environment-variables.md` moved and rewritten as `docs/reference/environment-variables.md`.
- Discovery, plan, and publishing preflight/result files were archived under `docs/_archive/discovery/`, `docs/_archive/plans/`, `docs/_archive/publishing/`, or `docs/_archive/merged/`.
- The historical execution plan moved to `docs/_archive/plans/plugin-example-generation-execution-plan.md`; active rules were summarized in `docs/architecture/decisions.md`.
- `docs/discovery/open-taskcard-closure-matrix.md` was replaced by `docs/development/taskcards.md`, which documents regeneration from evidence instead of storing a stale generated matrix as canonical docs.

Required canonical files created:

- `docs/README.md`
- `docs/reference/config.md`
- `docs/reference/cli.md`
- `docs/reference/file-contracts.md`
- `docs/guides/run-family-pipeline.md`
- `docs/guides/discovery-sweep.md`
- `docs/guides/add-or-update-family.md`
- `docs/guides/generate-and-validate-examples.md`

## Docs Coverage Checklist

| Traceability feature | Canonical coverage |
|---|---|
| Package/CLI entry point | `docs/reference/cli.md`, `README.md` |
| Full pipeline staged run | `docs/architecture/pipeline-stages.md`, `docs/guides/run-family-pipeline.md` |
| Tiered execution | `docs/reference/cli.md` |
| Family YAML model | `docs/reference/config.md`, `docs/guides/add-or-update-family.md` |
| Disabled/experimental/discovery-only family handling | `docs/reference/config.md` |
| NuGet fetch/latest/pinned resolution | `docs/reference/config.md`, `docs/architecture/pipeline-stages.md` |
| Dependency resolution | `docs/reference/config.md`, `docs/architecture/pipeline-stages.md` |
| Nupkg extraction/framework selection | `docs/architecture/pipeline-stages.md`, `docs/reference/file-contracts.md` |
| DllReflector/API catalog | `docs/development/testing.md`, `docs/reference/file-contracts.md`, `docs/reference/schemas-and-contracts.md` |
| Plugin namespace detection | `docs/overview/concepts.md`, `docs/architecture/pipeline-stages.md` |
| Discovery sweep | `docs/guides/discovery-sweep.md`, `docs/reference/cli.md` |
| API delta | `docs/architecture/pipeline-stages.md`, `docs/reference/file-contracts.md` |
| Fixture registry/cache | `docs/reference/file-contracts.md`, `docs/reference/config.md` |
| Generated fixture factory | `docs/reference/file-contracts.md`, `docs/guides/generate-and-validate-examples.md` |
| Existing example miner | `docs/architecture/pipeline-stages.md`, `docs/reference/config.md` |
| Scenario planner | `docs/architecture/pipeline-stages.md`, `docs/reference/file-contracts.md` |
| Catalog hash enforcement | `docs/reference/file-contracts.md`, `docs/reference/gates-and-verdicts.md` |
| LLM preflight/routing | `docs/reference/config.md`, `docs/reference/environment-variables.md` |
| Template generation | `docs/reference/config.md`, `docs/guides/generate-and-validate-examples.md` |
| Prompt packet generation | `docs/reference/schemas-and-contracts.md` |
| Generated project layout | `docs/reference/file-contracts.md` |
| Dotnet validation | `docs/reference/validation-and-reviewer.md`, `docs/development/testing.md` |
| Output semantic validation | `docs/reference/validation-and-reviewer.md` |
| External example-reviewer | `docs/reference/validation-and-reviewer.md`, `docs/operations/troubleshooting.md` |
| Gate verdicts | `docs/reference/gates-and-verdicts.md` |
| Per-example lifecycle/backlog | `docs/reference/gates-and-verdicts.md`, `docs/reference/file-contracts.md` |
| Evidence completeness | `docs/reference/file-contracts.md`, `docs/reference/gates-and-verdicts.md` |
| Evidence layout/promotion | `docs/reference/file-contracts.md` |
| Dry-run package publishing | `docs/reference/publishing-and-github.md`, `docs/operations/live-publishing.md` |
| Live GitHub PR creation | `docs/operations/live-publishing.md`, `docs/reference/publishing-and-github.md` |
| Publish readiness/repo access/permission probes | `docs/operations/live-publishing.md`, `docs/reference/publishing-and-github.md` |
| Merge PR workflow | `docs/operations/live-publishing.md`, `docs/reference/publishing-and-github.md` |
| Release status | `docs/operations/post-merge-verification.md`, `docs/reference/cli.md` |
| README rendering/audit/publish | `docs/operations/readme-publishing.md`, `docs/reference/publishing-and-github.md` |
| Agent metrics | `docs/reference/metrics.md`, `docs/operations/telemetry.md` |
| Monthly GitHub Actions refresh | `docs/operations/monthly-maintenance.md`, `docs/development/testing.md` |
| Build/test CI | `docs/development/testing.md` |
| Taskcard sync | `docs/development/taskcards.md` |
| Published example build regression | `docs/operations/post-merge-verification.md` |
| Denominator model/contracts | `docs/reference/schemas-and-contracts.md` |

## Verification Commands

Gate A preflight:

```powershell
Get-ChildItem docs -File | Select-Object -ExpandProperty Name
Select-String -Path docs/_audit/docs_migration_plan.md -Pattern '^\| `docs/[^/]+\.md`'
```

Gate B postflight:

```powershell
Get-ChildItem docs -File | Select-Object -ExpandProperty Name
```

Result after migration:

```text
README.md
```

Active-doc link check:

```powershell
$files = @()
$files += Get-Item README.md
$files += Get-Item AGENTS.md
$files += Get-ChildItem -Recurse docs -File -Filter *.md |
  Where-Object { $_.FullName -notmatch '\\docs\\_archive\\' -and $_.FullName -notmatch '\\docs\\_audit\\' }
$broken=@()
foreach($f in $files){
  $text=Get-Content $f.FullName -Raw
  $matches=[regex]::Matches($text,'\[[^\]]+\]\(([^)]+)\)')
  foreach($m in $matches){
    $link=$m.Groups[1].Value
    if($link -match '^(https?:|mailto:|#)'){ continue }
    $path=$link.Split('#')[0]
    if([string]::IsNullOrWhiteSpace($path)){ continue }
    $target=Join-Path $f.DirectoryName $path
    if(-not (Test-Path -LiteralPath $target)){ $broken += [PSCustomObject]@{File=$f.FullName; Link=$link} }
  }
}
if($broken.Count -eq 0){ 'NO_BROKEN_LINKS' } else { $broken | ConvertTo-Json -Depth 3 }
```

Result:

```text
NO_BROKEN_LINKS
```

Duplicate heading scan:

```powershell
$files = Get-ChildItem -Recurse docs -File -Filter *.md |
  Where-Object { $_.FullName -notmatch '\\docs\\_archive\\' -and $_.FullName -notmatch '\\docs\\_audit\\' }
Select-String -Path ($files.FullName) -Pattern '^#{1,3} ' |
  ForEach-Object { $_.Line.Trim() } |
  Group-Object |
  Where-Object { $_.Count -gt 1 } |
  Sort-Object Count -Descending |
  Select-Object Count,Name
```

Observed repeated headings were generic structural sections only: `## Evidence`, `## References`, `## Steps`, and `## Merge`. No duplicate canonical CLI/config/file-contract tables remain in active docs.

Coverage spot check:

```powershell
rg -n "Package/CLI|Full pipeline|Family YAML|NuGet fetch|DllReflector|Plugin namespace|Discovery sweep|API delta|Fixture registry|Scenario planner|LLM preflight|Dotnet validation|Gate verdicts|Live GitHub|Monthly GitHub|Build/test CI|Taskcard|Denominator" docs/reference docs/guides docs/operations docs/architecture docs/development docs/overview README.md
```

## Docs Root Hygiene

Root files before:

- `docs/monthly-runbook.md`
- `docs/verifier-integration.md`

Root orphan handling:

| Orphan | Action |
|---|---|
| `docs/monthly-runbook.md` | Moved to `docs/_archive/root-orphans/monthly-runbook.md`; merged into `docs/operations/monthly-maintenance.md`. |
| `docs/verifier-integration.md` | Moved to `docs/_archive/root-orphans/verifier-integration.md`; merged into `docs/reference/validation-and-reviewer.md`. |

Root files after:

- `docs/README.md`

Gate B passed.

## Known Gaps

- Archived docs intentionally may contain stale links or historical claims. Active docs link to current canonical pages instead.
- References are code-derived from the audit and should be periodically refreshed from code/schemas, especially `docs/reference/cli.md` and `docs/reference/config.md`.
- No full docs-specific automated link checker was added; the PowerShell link check above was run for active markdown docs.
