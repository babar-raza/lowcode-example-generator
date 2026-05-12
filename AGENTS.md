# AGENTS.md — Pipeline Governance

This file governs how automated agents and human contributors interact with this repository.

## Repository Purpose

This repository is the **pipeline repo** for the Aspose .NET Plugin Example Generation Pipeline.

It generates, validates, and publishes SDK-style C# examples for Aspose .NET plugin APIs (e.g., LowCode, Plugins namespaces).

**This repo does NOT contain published examples.** Published examples live in a separate repo: `aspose-plugins-examples-dotnet`.

## Plan

The active governance and architecture decision summary is at:

```
docs/architecture/decisions.md
```

Read it before implementing anything.

## Source of Truth Hierarchy

1. **Official NuGet package** — primary authority for all API symbols.
2. **DocFX markdown API reference** — secondary, for descriptions only.
3. **Existing Aspose .NET example repos** — style hints and fixture discovery only.

The LLM proposes. The compiler, runtime, output validator, and example-reviewer approve.

## Core Rules

1. No generated example may use any symbol absent from the reflected NuGet API catalog.
2. No direct push to `main`. All publishing is PR-based with evidence.
3. Monthly runs must be delta-based. Do not regenerate unchanged examples.
4. Blocked scenarios must be preserved with explicit reasons. Never silently drop them.
5. All verification gates must pass before a PR is created.

## Gate Order

```
NuGet fetch → extract → reflect → detect → delta → fixtures → scenarios →
LLM preflight → generate → restore → build → run → output validation →
example-reviewer → PR
```

## Verification Gates (summary)

Gates 0-18 (21 total) are documented in Sections 12 and 29 of the execution plan.

## Credentials Required

| Secret | Purpose | How to set |
|---|---|---|
| `GH_TOKEN` | Operator storage for GitHub classic PAT (`ghp_*`, `repo` scope). Never read by pipeline directly — map to `GITHUB_TOKEN` before each live command. | Windows system env: `[Environment]::SetEnvironmentVariable("GH_TOKEN", "ghp_...", "User")` |
| `GITHUB_TOKEN` | Read by the pipeline for PR creation, merge, repo probes. Always populated from `GH_TOKEN` at command time: `$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")` | Set in current PowerShell session only. |
| `LLM_PROFESSIONALIZE_API_KEY` | LLM generation | GitHub Actions secret |
| `OLLAMA_HOST` | Ollama fallback endpoint | GitHub Actions variable (optional) |

**Fine-grained PAT warning:** Fine-grained PATs with a personal account resource owner cannot write to org-owned repos via the Git Data API. Always use a classic PAT with `repo` scope stored in `GH_TOKEN`.

Use `--dry-run` mode when credentials are unavailable.

## Pilot

Aspose.Cells for .NET — config at `pipeline/configs/families/cells.yml`.

## Agent Rules

- Do not implement anything that bypasses a verification gate.
- Do not push directly to `main` from any automated workflow.
- Do not trust DocFX markdown as the source of truth for API symbols.
- Do not proceed to generation if the reflection catalog is empty.
- Do not create PRs if any mandatory gate has failed.
- Always record evidence before exiting — even on partial failure.
- When running live publish or merge commands, always read `GH_TOKEN` from Windows system env and map to `GITHUB_TOKEN` in the current process — never assume `GITHUB_TOKEN` is already set.

## Discovery

Current-state findings: `docs/discovery/current-state.md`
