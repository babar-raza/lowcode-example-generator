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
2. All publishing is PR-based. Agent holds merge authority when all AMG gates pass.
   Auto-merge executes via `gh pr merge --squash` when `APPROVE_LIVE_MERGE=1` is set in env
   and all artifact/build/README gates have passed. No external human approval is required.
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

## LLM Endpoint Governance

**Authoritative endpoint:** All LLM inference calls MUST use `https://llm.professionalize.com/v1/` exclusively.

- Any other LLM endpoint (OpenAI direct, Azure OpenAI, Ollama, Anthropic, etc.) is **out of bounds** and MUST NOT be used.
- Only models served at `llm.professionalize.com` are permitted. Do not hardcode or configure any other base URL.
- The environment variable `GPT_OSS_ENDPOINT` MUST be set to `https://llm.professionalize.com/v1/`. If it is absent or points elsewhere, the pipeline MUST abort before generation with a clear error message.
- The environment variable `GPT_OSS_MODEL` selects the model. Only model names available on `llm.professionalize.com` are valid. Never use `gpt-4o-mini` or any model name that is not confirmed to be served by that endpoint.
- The environment variable `GPT_OSS_API_KEY` carries the API key for `llm.professionalize.com`. No key from any other provider may be substituted.

**Agent rule:** If `GPT_OSS_ENDPOINT` is unset, empty, or does not match `https://llm.professionalize.com/v1/`, treat it as a hard blocker — record the error in evidence and halt. Do not fall back to any alternative endpoint.

## Credentials Required

| Secret | Purpose | How to set |
|---|---|---|
| `GH_TOKEN` | Operator storage for GitHub classic PAT (`ghp_*`, `repo` scope). Never read by pipeline directly — map to `GITHUB_TOKEN` before each live command. | Windows system env: `[Environment]::SetEnvironmentVariable("GH_TOKEN", "ghp_...", "User")` |
| `GITHUB_TOKEN` | Read by the pipeline for PR creation, merge, repo probes. Always populated from `GH_TOKEN` at command time: `$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")` | Set in current PowerShell session only. |
| `GPT_OSS_ENDPOINT` | LLM base URL — **must be** `https://llm.professionalize.com/v1/`. Any other value is rejected. | Set in current PowerShell session or Windows system env. |
| `GPT_OSS_MODEL` | Model name served by `llm.professionalize.com`. | Set in current PowerShell session or Windows system env. |
| `GPT_OSS_API_KEY` | API key for `llm.professionalize.com`. | Windows system env (never log or print). |

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
- **LLM endpoint is non-negotiable:** Never configure, suggest, or fall back to any LLM endpoint other than `https://llm.professionalize.com/v1/`. If `GPT_OSS_ENDPOINT` is missing or wrong, halt and report — do not substitute another provider.
- **Auto-merge authority:** Agent has full merge authority. When all AMG gates pass and `APPROVE_LIVE_MERGE=1` is set, execute `gh pr merge --squash` without waiting for external human approval. If `APPROVE_LIVE_MERGE` is absent, record `CREDENTIAL_BLOCKED` in evidence and proceed to the next PR — do not halt the sprint.
- **Branch deletion:** After merge, evaluate BDG gates. If `APPROVE_DELETE_BRANCH=1` is set and all BDG checks pass, delete the branch. If absent or any BDG check fails, record `BRANCH_DELETE_SKIPPED_POLICY` and continue — this is not an error.
- **Publication repo allowlist:** Target repos for merge operations must be in the `APPROVED_PUBLICATION_REPOS` allowlist (see `merge_approval_gate.py`). Attempting to merge to a fixture source repo is `REVIEW_POLICY_BLOCKED`. Never merge to a fixture source repo.
- **Fixture source repos are read-only:** Repos used for fixture discovery (e.g., `aspose-barcode/Aspose.BarCode-for-.NET`) must never be written to. The allowlist in `merge_approval_gate.py` enforces this separation.

## Multi-Agent Framework

The project includes a multi-agent coordination framework at `src/plugin_examples/agents/`:

| Component | File | Purpose |
|-----------|------|---------|
| Agent ABC | `base.py` | Abstract agent with `execute(context)` and `AgentCapability` enum |
| Registry | `registry.py` | Discovers and instantiates agents by capability |
| Dispatcher | `dispatcher.py` | Coordinates multiple agents over shared context |
| SharedContext | `context.py` | Thread-safe state sharing between agents |
| Protocol | `protocol.py` | A6-level coordination protocol with `MessageBus` |

**Builtin agents:** ConservationCheckAgent (validation), VersionDriftAgent (monitoring), BlockerRecheckAgent (remediation).

**Coordination model (A6):** The planner loop dispatches agents by capability, collects structured results from SharedContext, and makes phase-transition decisions. Agents do not self-schedule or modify the dispatch sequence.

## Discovery

Current-state findings: `docs/_archive/discovery/current-state.md`
