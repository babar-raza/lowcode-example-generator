# lowcode-example-generator

A gate-driven pipeline that generates, validates, and publishes SDK-style C# examples for Aspose .NET plugin APIs
(LowCode and Plugins namespaces). The pipeline reflects a live NuGet package, plans scenarios, calls an LLM to
write code, compiles and runs the generated examples, and — after all gates pass and a human provides an explicit
approval token — opens a pull request to the target examples repository.

This repository is the **pipeline repo only**. Published examples live in separate repositories under
`aspose-cells-net`, `aspose-words-net`, etc.

---

## Summary

| What it does | Reflects Aspose .NET NuGet packages → plans C# example scenarios → generates code via LLM → compiles + runs + validates → publishes via GitHub PR |
|---|---|
| What it will become | A monthly-automated, multi-family example publisher covering Cells, Words, PDF, and more |
| What works today | Cells (9 examples merged), Words 4-type pilot (4 examples merged), PDF classification complete |
| What is unfinished | PDF generation (blocked on 2 taskcards), broader Words expansion (blocked on 4 taskcards) |
| System character | Hybrid: deterministic reflection + gate engine, LLM for code generation, human approval gates for publishing |

---

## Current Status

| Area | Status | Evidence | Notes |
|------|--------|----------|-------|
| Cells generation | Complete | `release-status.json`: 9/9 POST_MERGE_VERIFIED | Version 26.4.0, PR #1 merged |
| Words pilot (4 types) | Complete | `release-status.json`: 4/4 POST_MERGE_VERIFIED | Version 26.4.0, PR #1 merged |
| PDF generation | Blocked | `pdf.yml`: `status: discovery_only` | 2 open taskcards remain |
| Words expansion | Blocked | `words.yml`: `allowed_types` = 4 types | 4 open taskcards remain |
| README backfill (aspose.net links) | Complete | PRs #3 merged for Cells and Words | Correct links on remote main |
| Unit tests | Passing | `.github/workflows/build-and-test.yml` | 27 test files, Python 3.12 + 3.13 |
| Live PR publishing | Complete | `publisher/github_pr_publisher.py` | 8-step GitHub REST API flow |
| PR merge automation | Complete | `publisher/github_pr_merger.py` | Requires separate `APPROVE_MERGE_PR` token |
| Monthly CI | Present | `.github/workflows/monthly-package-refresh.yml` | Cron: 1st of month |
| PDF type classification | Complete | `workspace/verification/latest/pdf-type-role-classification.json` | 25 WORKFLOW_ROOT confirmed |

---

## What This Project Does

The pipeline solves a content-at-scale problem: Aspose releases new and updated .NET NuGet packages monthly,
and each package exposes a set of LowCode API types that deserve working, runnable C# examples. Writing those
examples by hand is slow. This pipeline automates the full lifecycle:

1. **Discover** — resolve the latest NuGet package, extract DLLs, use a metadata-only .NET reflector to build
   an API catalog of every public type and method in the plugin namespaces.
2. **Plan** — classify API types by role (WORKFLOW_ROOT, OPTIONS, PROVIDER_CALLBACK, etc.), select which types
   are ready for example generation, and produce a set of scenarios.
3. **Generate** — build a constrained prompt packet per scenario, call an LLM, extract the generated C# code,
   and write a self-contained .NET console project.
4. **Validate** — run `dotnet restore`, `dotnet build`, and `dotnet run` on each generated project. On build
   failure, attempt up to 2 LLM-driven repairs. On runtime failure, attempt 1 repair if the failure is
   classified as repairable.
5. **Gate** — evaluate 21+ gates in strict order. Hard-stop gates (stages 1–6) block the entire pipeline.
   Later gates determine the per-example and aggregate verdict from a canonical taxonomy.
6. **Publish** — with all gates passing and an explicit `APPROVE_LIVE_PR` human token, open a PR to the target
   examples repo via the GitHub REST API. No direct push to `main`. A separate `APPROVE_MERGE_PR` token is
   required to merge.

---

## Goals

- Generate working, runnable C# examples for every LowCode API entry point that has a stable fixture strategy.
- Keep examples delta-based: only regenerate when the NuGet API changes or examples are stale.
- Publish via PR, not direct push, with all gates documented as evidence JSON files.
- Support multiple Aspose .NET families (Cells, Words, PDF, and future families) from a single pipeline.
- Allow a human operator to approve publishing steps without giving the pipeline unrestricted repo write access.

---

## What Has Been Accomplished

All of the following are verified by source code, tests, or evidence artifacts.

### Cells for .NET (9 examples, fully released)
- 9 examples generated, built, and validated: html-converter, image-converter, json-converter, pdf-converter,
  spreadsheet-converter, spreadsheet-locker, spreadsheet-merger, spreadsheet-splitter, text-converter.
- PR #1 merged at `aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples` (SHA `f6e5515c`).
- Post-merge validation: 9/9 ALL_PASS.
- README backfill PR #3 merged with correct aspose.net links (SHA `56601118`).
- Source: `workspace/verification/latest/release-status.json`, `cells-merge-result.json`.

### Words for .NET (4-type pilot, released)
- 4 examples: converter, watermarker (SetText), splitter (ExtractPages), replacer (Replace).
- Input strategy: programmatic (Document + DocumentBuilder creates input .docx).
- PR #1 merged at `aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples` (SHA `b1877ed7`).
- Post-merge validation: 4/4 ALL_PASS.
- README backfill PR #3 merged (SHA `6556906e`).
- Source: `workspace/verification/latest/release-status.json`, `words-merge-result.json`.

### PDF for .NET (discovery and classification complete)
- API reflected: 88 types cataloged across 8 roles.
- 25 WORKFLOW_ROOT types confirmed (Merger, Splitter, Optimizer, TextExtractor identified as pilot candidates).
- Architecture note: PDF LowCode uses instance-method pattern (`new Merger().Process(options)`) vs. static
  methods in Cells/Words.
- Generation remains blocked (`status: discovery_only` in `pdf.yml`).
- Source: `workspace/verification/latest/pdf-type-role-classification.json`.

### Infrastructure
- 14 CLI commands, 13 pipeline stages, 21+ verification gates.
- 27 unit test files, 759 tests passing.
- CI: Python 3.12 and 3.13 on every push/PR to main.
- Live GitHub PR creation and merge via REST API (token never logged).
- Dual approval token system (publish vs. merge are separate, non-interchangeable).
- Aspose.net link standardization module enforces correct URL pattern across all generated READMEs.
- Monthly CI workflow for automated package refresh.

---

## What Remains

### Required before PDF generation can proceed
1. `followup-pdf-fixture-strategy-review` — validate programmatic PDF creation as the fixture strategy.
2. `followup-pdf-family-repo-target-mapping` — create the target repo
   `aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples` (currently uses central repo fallback in `pdf.yml`).
3. `followup-pdf-controlled-pilot-enablement` — enable 4 pilot types after above blockers are closed
   and human approves.

### Required before broader Words generation can proceed
4. `followup-words-split-criteria-enumeration` — document SplitCriteria enum values (blocks WORDS-005).
5. `followup-words-pair-fixture-strategy` — define paired input fixture strategy (blocks WORDS-006/007).
6. `followup-words-mail-merger-fixture-documentation` — MailMerger fixture DOCX (blocks WORDS-008).
7. `followup-words-docx-semantic-validation` — DOCX semantic validation beyond ZIP/XML checks.

### Infrastructure / observability
8. `followup-family-readiness-ranker-trust` — improve observability of readiness scoring.
9. `followup-readme-symbols-from-catalog` — populate the API column in generated READMEs from catalog data.

### Known inconsistency
- `AGENTS.md` refers to `LLM_PROFESSIONALIZE_API_KEY` but the actual env var is `GPT_OSS_API_KEY`
  (confirmed in `docs/ci/environment-variables.md`). `AGENTS.md` is stale on this point.

---

## Architecture

### Pipeline stages (sequential, in `src/plugin_examples/runner.py`)

```
Stage 1:  Load config           (family YAML → FamilyConfig dataclass)
Stage 2:  NuGet fetch           (download latest-stable or pinned package)
Stage 3:  Dependency resolution (transitive deps, deduplicated by assembly identity)
Stage 4:  Extraction            (DLL + XML docs, select target framework)
Stage 5:  Reflection            (DllReflector → API catalog JSON)
Stage 6:  Plugin detection      (namespace pattern match → source-of-truth proof)
─── Stages 1-6 are hard-stop gates. Failure blocks everything downstream. ───
Stage 7:  API delta             (diff catalog vs. prior run; initial_run or change set)
Stage 8:  Fixture registry      (index available test fixtures from external repos)
Stage 9:  Scenario planning     (type-role classification, scenario generation, blocked reasons)
Stage 10: LLM preflight         (provider availability check, select first passing provider)
Stage 11: Generation            (LLM or template → C# code → .NET project)
Stage 12: Validation            (restore → build [+repair] → run [+repair] → output check)
Stage 13: Publishing            (gate evaluation → PR dry-run or live PR)
```

### Component map

```
pipeline/configs/families/        Family YAML configs (cells.yml, words.yml, pdf.yml)
src/plugin_examples/
  __main__.py                     CLI entry point (14 commands)
  runner.py                       Pipeline orchestrator (13 stages, PipelineContext)
  family_config/                  Config loading, schema validation
  nuget_fetcher/                  NuGet package resolution and caching
  nupkg_extractor/                DLL + XML extraction from .nupkg
  reflection_catalog/             API catalog building via DllReflector
  plugin_detector/                Namespace pattern matching and proof generation
  api_delta/                      Catalog diff and impact mapping
  scenario_planner/               Type classification, scenario planning, entrypoint scoring
  fixture_registry/               Fixture indexing (GitHub sourced and generated)
  llm_router/                     Provider preflight, policy enforcement, LLM calls
  generator/                      PromptPacket building, code generation, project generation
  verifier_bridge/                dotnet restore/build/run, output validation, reviewer bridge
  gates/                          Gate evaluation, verdict determination, result writing
  publisher/                      PR building, approval gates, GitHub REST API publisher/merger,
                                  README rendering and auditing, release status, aspose links
tools/DllReflector/               .NET metadata-only reflector (MetadataLoadContext, no code exec)
pipeline/schemas/                 JSON schemas for family configs, API catalog, scenarios, etc.
templates/root-readme/            Jinja2 template for family README generation
.github/workflows/                CI: build-and-test, monthly-package-refresh
workspace/verification/latest/    All evidence JSON files from pipeline runs
workspace/pr-dry-run/             Dry-run PR packages ready for manual publishing
workspace/manifests/              Scenario catalog, example index, fixture registry snapshots
```

### Data flow

```
NuGet package
  → DLL extraction
  → DllReflector (metadata-only .NET tool)
  → API catalog (JSON)
  → Scenario planner (type-role classification, allowed_types filter, preferred_methods_per_type)
  → Scenario list (ready + blocked with explicit reasons)
  → PromptPacket builder (constrained prompt, 46+ rules, approved symbols only)
  → LLM (code generation)
  → C# code extraction (```csharp block, then generic, then raw)
  → .NET project (Program.cs, .csproj, README.md, example.manifest.json, expected-output.json)
  → dotnet restore / build / run (with LLM repair on failure)
  → Output validator (semantic checks: PDF header, XLSX ZIP, JSON parse, etc.)
  → Example reviewer (optional, semantic validation via example-reviewer CLI)
  → Gate evaluator (21+ gates, canonical verdict)
  → Evidence JSON (gate-results, validation-results, pr-candidate-manifest, ...)
  → Publisher (dry-run or live GitHub REST API PR)
```

### Key design decisions

- **No direct push to main.** All publishing is PR-based via GitHub REST API.
- **Dual approval tokens.** `APPROVE_LIVE_PR` (PR creation) and `APPROVE_MERGE_PR` (merge) are separate
  tokens. The merge gate explicitly rejects `APPROVE_LIVE_PR` to prevent token reuse.
- **Source of truth is the NuGet package.** The reflected API catalog — not DocFX markdown, not existing
  examples — is the authoritative list of available symbols. Generated code may only use symbols confirmed
  in the catalog.
- **Blocked scenarios are preserved.** Scenarios that cannot be generated (missing fixture, unsupported type,
  unresolvable input format) are written to evidence with an explicit `blocked_reason`. Nothing is silently
  dropped.
- **DllReflector uses MetadataLoadContext exclusively.** No code execution, no `Activator.CreateInstance`,
  no static constructor invocation. The reflector is purely metadata inspection.

---

## Deterministic vs LLM-Driven Behavior

### Fully deterministic
- NuGet resolution, DLL extraction, .NET reflection (DllReflector)
- Type-role classification logic (rules-based)
- Scenario planning: which scenarios are ready vs. blocked, and why
- Gate evaluation: gate order, hard-stop gates, verdict taxonomy
- PromptPacket construction: all constraints, approved symbols list, fixture references
- Output validation: file-type semantic checks (PDF, XLSX, JSON, HTML headers)
- Approval gate enforcement: token matching, merge-vs-publish separation
- GitHub REST API interactions (PR creation, merge) — deterministic given inputs
- Evidence JSON writing
- README rendering (Jinja2 template)
- Aspose.net link construction and validation

### LLM-driven
- **Code generation:** The LLM writes the C# `Program.cs` content for each scenario.
- **Build repair:** On compile failure (up to 2 attempts), the LLM is given the error output and asked
  to fix the code. The repair is re-compiled to verify.
- **Runtime repair:** On classified runtime failures (up to 1 attempt), the LLM is given the failure
  classification and asked to fix the code. The repair is re-run to verify.

### Safeguards against bad LLM output
- **Symbol validation before prompting:** `packet_builder.py` verifies every `required_symbol` exists in the
  reflected catalog. Unknown symbols raise `UnknownSymbolError` before the LLM is called.
- **46+ hard constraints in every prompt:** No `Console.ReadKey`/`ReadLine`, no `TODO`, no
  `NotImplementedException`, output files must be validated, input must not be hardcoded paths, etc.
- **Compiler as arbiter:** Generated code that does not compile is never published, regardless of what the
  LLM claims. The compiler's verdict is final after the repair budget is exhausted.
- **Runtime as arbiter:** Generated code that exits with a non-zero status or produces no output is blocked.
- **Output semantic validation:** Beyond exit codes, actual output files are inspected (PDF magic bytes,
  XLSX ZIP structure, etc.).
- **Example reviewer gate:** An optional external reviewer CLI performs semantic quality checks.
- **Canonical verdict taxonomy:** There are 16 possible pipeline verdicts. Only `PR_DRY_RUN_READY` or higher
  allows a PR to be created. Only `FULL_E2E_PASSED` represents a merged, post-merge-validated example.
- **No LLM output is cached or trusted across runs.** Every run re-generates and re-validates.

---

## Features

| # | Feature | Status | Module(s) |
|---|---------|--------|-----------|
| 1 | NuGet API discovery and reflection | Complete | `nuget_fetcher/`, `nupkg_extractor/`, `reflection_catalog/`, `plugin_detector/`, `tools/DllReflector/` |
| 2 | Type-role classification | Complete | `scenario_planner/type_classifier.py` |
| 3 | Scenario planning with allowed_types and preferred_methods_per_type | Complete | `scenario_planner/planner.py` |
| 4 | LLM code generation with constrained prompt packets | Complete | `generator/code_generator.py`, `generator/packet_builder.py` |
| 5 | Build-repair cycle (up to 2 compile + 1 runtime repair) | Complete | `runner.py`, `verifier_bridge/dotnet_runner.py` |
| 6 | Gate engine (21+ gates, canonical verdict taxonomy) | Complete | `gates/evaluator.py`, `gates/example_gates.py` |
| 7 | Live PR publishing (8-step GitHub REST API) | Complete | `publisher/github_pr_publisher.py` |
| 8 | PR merge (4-step GitHub REST API, separate approval) | Complete | `publisher/github_pr_merger.py` |
| 9 | README generation via Jinja2 template | Complete | `publisher/readme_renderer.py`, `templates/root-readme/` |
| 10 | README link auditing (aspose.net enforcement) | Complete | `publisher/readme_auditor.py`, `publisher/aspose_links.py` |
| 11 | Release status reporting | Complete | `publisher/release_status.py` |
| 12 | Discovery sweep (no-LLM reflection scan for all families) | Complete | `src/plugin_examples/discovery_sweep.py` |
| 13 | API delta tracking (change detection vs. prior run) | Complete | `api_delta/` |
| 14 | Fixture registry (GitHub sourced and programmatic) | Complete | `fixture_registry/registry.py`, `fixture_registry/fixture_factory.py` |
| 15 | Monthly CI automation | Present | `.github/workflows/monthly-package-refresh.yml` |
| 16 | Publish permission probe (read-only GitHub API check) | Complete | `publisher/publish_permission_probe.py` |
| 17 | Repo access resolver | Complete | `publisher/repo_access_resolver.py` |
| 18 | Publish readiness check | Complete | `publisher/publish_readiness.py` |

---

## Setup

### Prerequisites

- Python 3.12 or 3.13
- .NET SDK 9.x (the project targets `net8.0`; `global.json` uses `rollForward: latestMajor` to accept 9.x)
- Git (to clone this repo and the example-reviewer repo)
- A GitHub classic PAT with `repo` scope (for fixture fetching and live publishing)
- Access to an `llm_professionalize`-compatible endpoint or a running Ollama instance (for code generation)

### Clone and install

```bash
git clone https://github.com/babar-raza/lowcode-example-generator
cd lowcode-example-generator

# Create a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\pip install -e ".[dev]"

# Linux/macOS
.venv/bin/pip install -e ".[dev]"
```

### Build the DllReflector tool

```bash
dotnet build tools/DllReflector/DllReflector.csproj -c Release
```

The pipeline expects the compiled binary under `tools/DllReflector/bin/Release/`.

### Example reviewer (optional, required for `--require-reviewer`)

```bash
# Clone the reviewer repo alongside this one
git clone https://github.com/babar-raza/example-reviewer ../example-reviewer
cd ../example-reviewer
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"   # Windows
# Requires openai>=1.69.0

export EXAMPLE_REVIEWER_PATH="$(pwd)"
```

---

## Environment Variables

| Variable | Required for | Value |
|----------|-------------|-------|
| `GPT_OSS_ENDPOINT` | LLM code generation | `https://llm.professionalize.com/v1/` (or your endpoint) |
| `GPT_OSS_API_KEY` | LLM authentication | API key — never logged |
| `GPT_OSS_MODEL` | LLM model selection | Optional; default is `recommended`. Never use `gpt-4o-mini`. |
| `GITHUB_TOKEN` | PR creation, merge, fixture fetch | Classic PAT, `repo` scope. Never logged. |
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | Live PR creation | Must equal exactly `APPROVE_LIVE_PR` |
| `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | Live PR merge | Must equal exactly `APPROVE_MERGE_PR` |
| `EXAMPLE_REVIEWER_PATH` | `--require-reviewer` mode | Path to checked-out example-reviewer repo |
| `PYTHONPATH` | All pipeline commands | Set to `src` |

**Important:** `APPROVE_LIVE_PR` and `APPROVE_MERGE_PR` are human operator phrases, not secrets. They must NOT be stored as CI secrets — they must be provided interactively at the time of publishing.

---

## Usage

All commands use `python -m plugin_examples` with `PYTHONPATH=src`. On Windows, prefix with
`.venv\Scripts\python.exe`. All commands default to `--dry-run` mode and write no evidence unless
`--promote-latest` is specified.

### Run the full pipeline (dry-run, no LLM)

```bash
PYTHONPATH=src python -m plugin_examples run --family cells --tier 5 --promote-latest
```

### Run the full pipeline with LLM generation

```bash
PYTHONPATH=src \
  GPT_OSS_ENDPOINT="https://..." \
  GPT_OSS_API_KEY="..." \
  EXAMPLE_REVIEWER_PATH="/path/to/example-reviewer" \
  python -m plugin_examples run --family cells --tier 5 --require-llm --require-validation --require-reviewer --promote-latest
```

### Publish a live PR (requires human approval token and GITHUB_TOKEN)

```bash
PYTHONPATH=src \
  GITHUB_TOKEN="ghp_XXXX" \
  python -m plugin_examples publish-pr --family cells --publish --approval-token APPROVE_LIVE_PR
```

### Merge a PR (requires separate human approval token)

```bash
PYTHONPATH=src \
  GITHUB_TOKEN="ghp_XXXX" \
  python -m plugin_examples merge-pr --family cells --pr-number 2 --merge --approval-token APPROVE_MERGE_PR
```

### Discovery sweep (no LLM, no generation — all families)

```bash
PYTHONPATH=src python -m plugin_examples discover-lowcode --all-families --rank --promote-latest
```

### Release status

```bash
PYTHONPATH=src python -m plugin_examples release-status --families cells words --promote-latest
```

### All CLI commands

| Command | Purpose |
|---------|---------|
| `run` | Full pipeline: reflect → plan → generate → validate → publish |
| `discover-lowcode` | Discovery-only sweep (stages 1–6, no LLM) |
| `validate-publish-targets` | Check publish readiness for target repos |
| `resolve-repo-access` | Probe GitHub API read access (read-only) |
| `probe-publish-permissions` | Probe GitHub push permissions (read-only) |
| `publish-pr` | Create a live PR (or simulate with `--dry-run`) |
| `merge-pr` | Merge a PR (or simulate with `--dry-run`) |
| `publish-readme` | Create a README-only backfill PR |
| `render-root-readme` | Render the family README from template (dry-run) |
| `release-status` | Report per-family release state |
| `sync-taskcard-docs` | Write `docs/discovery/open-taskcard-closure-matrix.md` |
| `check` | Check for NuGet package updates |
| `status` | List available pipeline modules |

### `run` command flags

| Flag | Default | Description |
|------|---------|-------------|
| `--family` | required | `cells`, `words`, or `pdf` |
| `--tier` | `5` | Max stage to execute (0=config only, 5=full) |
| `--dry-run` | on | No GitHub mutations |
| `--publish` | off | Enable live PR creation |
| `--approval-token` | — | `APPROVE_LIVE_PR` for live publish |
| `--require-llm` | off | Fail if LLM is unavailable |
| `--require-validation` | off | Fail if validation cannot run |
| `--require-reviewer` | off | Fail if example-reviewer is unavailable |
| `--skip-run` | off | Skip `dotnet run` (build-only mode) |
| `--template-mode` | off | Use template code instead of LLM |
| `--promote-latest` | off | Copy evidence to `workspace/verification/latest/` |
| `--allow-experimental` | off | Include families with `status: experimental` |

---

## Testing and Verification

### Run unit tests

```bash
PYTHONPATH=src python -m pytest tests/unit -v --timeout=60
```

Or with the installed entry point:

```bash
PYTHONPATH=src pytest tests/unit -v --timeout=60
```

### CI

- **Build and test:** `.github/workflows/build-and-test.yml` — runs on every push and PR to `main`.
  - Python 3.12 and 3.13 on `ubuntu-latest`.
  - Runs all unit tests, then a compile check (`python -m compileall src`).
  - Also builds `tools/DllReflector/DllReflector.csproj` on .NET 8.0.
- **Monthly refresh:** `.github/workflows/monthly-package-refresh.yml` — cron on the 1st of each month,
  also triggerable via `workflow_dispatch`.

### Test coverage (27 files, ~759 tests)

| Area | Test file(s) |
|------|-------------|
| Family config loading | `test_family_config.py` |
| Fixture registry and strategy | `test_fixture_registry.py`, `test_fixture_strategy.py` |
| Scenario planning | `test_scenario_planner.py` |
| LLM generation and constraints | `test_llm_generation.py`, `test_code_quality_sprint.py` |
| Build/run validation | `test_validation.py` |
| Runner and repair cycles | `test_runner.py` |
| Publishing and approval gates | `test_publishing.py`, `test_publishing_approval_gate.py` |
| Merge governance | `test_merge_governance.py` |
| Real GitHub publisher | `test_real_github_publisher.py` |
| Release status | `test_release_status.py` |
| README rendering | `test_readme_renderer.py` |
| Aspose.net links | `test_aspose_links.py` |
| PDF deduplication | `test_pdf_assembly_dedup.py` |
| Token policy | `test_token_policy.py` |
| CI runbook hardening | `test_ci_runbook_hardening.py` |
| NuGet fetcher | `test_nuget_fetcher.py` |
| API delta | `test_api_delta.py` |
| Plugin detection | `test_plugin_detector.py` |
| Reflection catalog | `test_reflection_catalog.py` |
| Discovery readiness | `test_discovery_readiness_preservation.py` |
| Words readiness | `test_words_readiness_review.py` |
| Scenario healing | `test_scenario_selection_healing.py` |
| Partial success | `test_partial_success_partitioning.py` |
| False-success contracts | `test_false_success_contracts.py` |
| Sync taskcard docs | `test_sync_taskcard_docs.py` |

---

## Generated Files, Cache, and Evidence

### Evidence artifacts (`workspace/verification/latest/`)

Every pipeline run writes JSON evidence files here when `--promote-latest` is specified.
Key files:

| File | Contents |
|------|----------|
| `release-status.json` | Per-family release state, PR numbers, merge SHAs, post-merge pass counts |
| `scenario-catalog.json` | All scenarios (ready + blocked with reasons) |
| `validation-results.json` | Per-example restore/build/run results with durations |
| `aggregate-gate-results.json` | Overall gate pass/fail counts |
| `pr-candidate-manifest.json` | Examples that passed all gates and are ready for PR |
| `fixture-strategy-plan.json` | Fixture strategy per scenario |
| `repair-attempts.json` | Build and runtime repair logs |
| `llm-preflight.json` | Provider selection, latency, pass/fail for each candidate provider |
| `all-family-lowcode-discovery.json` | Discovery sweep results for all families |
| `open-taskcard-closure-matrix.json` | All taskcards with open/closed status |
| `pdf-type-role-classification.json` | PDF type classification results (25 WORKFLOW_ROOT, etc.) |
| `cells-merge-result.json`, `words-merge-result.json` | Live merge outcomes |
| `cells-post-merge-clean-checkout-validation.json` | Post-merge clean build results |

### Dry-run packages (`workspace/pr-dry-run/`)

When the pipeline reaches `PR_DRY_RUN_READY` verdict, it writes all generated example files here.
These can be reviewed manually or pushed live with `publish-pr --publish`.

### Manifests (`workspace/manifests/`)

- `scenario-catalog.json` — snapshot of scenario planning results
- `example-index.json` — index of generated examples
- `existing-examples-index.json` — examples already in target repos (used for delta detection)
- `fixture-registry.json` — fixture inventory for each family

---

## Known Gaps and Risks

1. **PDF generation is blocked.** `pdf.yml` has `status: discovery_only`. Two taskcards
   (`followup-pdf-fixture-strategy-review` and `followup-pdf-family-repo-target-mapping`) must be resolved
   before generation can proceed. The target repo does not yet exist.

2. **Words expansion is limited.** `words.yml` constrains generation to 4 types via `allowed_types`.
   21 other scenarios are blocked. Four taskcards must be resolved before expanding.

3. **No integration tests.** All 759 tests are unit tests with mocks and test doubles. There is no
   end-to-end smoke test that actually calls the LLM, compiles real code, or creates a real PR.

4. **LLM output quality is not deterministic.** The build-repair cycle handles compile failures, but
   there is no guarantee that LLM code will pass reviewer gates. Poorly generated examples will be blocked
   and need manual intervention.

5. **example-reviewer is a separate repo.** If the reviewer is unavailable or misconfigured, the reviewer
   gate is skipped (unless `--require-reviewer` is set). Examples can reach `PR_DRY_RUN_READY` without
   passing the reviewer gate.

6. **`AGENTS.md` env var names are stale.** `AGENTS.md` references `LLM_PROFESSIONALIZE_API_KEY` but
   the actual env vars are `GPT_OSS_ENDPOINT`, `GPT_OSS_API_KEY`, and `GPT_OSS_MODEL`.
   See `docs/ci/environment-variables.md` for the authoritative list.

7. **Merge requires APPROVE_MERGE_PR.** The merge command exists and is implemented but requires a human
   to provide the `APPROVE_MERGE_PR` token interactively. This is intentional, not a defect.

8. **Windows required for full pipeline execution.** The monthly refresh CI workflow runs on
   `windows-latest` because .NET tooling for certain NuGet operations behaves differently on Linux.
   Unit tests run on `ubuntu-latest`.

---

## Recommended Next Steps

In priority order:

1. Close `followup-pdf-fixture-strategy-review` — confirm programmatic PDF fixture creation works and
   update `pdf.yml` with the strategy.
2. Close `followup-pdf-family-repo-target-mapping` — create the target repo for PDF examples.
3. Enable PDF controlled pilot (`followup-pdf-controlled-pilot-enablement`) — set `allowed_types` in
   `pdf.yml` to the 4 confirmed pilot types (Merger, Splitter, Optimizer, TextExtractor) and run the
   pipeline.
4. Resolve Words expansion taskcards — address split criteria, pair fixtures, MailMerger, and semantic
   validation so broader Words generation can proceed.
5. Update `AGENTS.md` — correct the env var names from `LLM_PROFESSIONALIZE_API_KEY` to `GPT_OSS_API_KEY`.
6. Add an integration smoke test — a lightweight end-to-end test that exercises DllReflector + scenario
   planning on a real (small) NuGet package, without requiring a live LLM.

---

## Maintainer Notes

- **Branch:** `main`. No direct push. All changes via PR.
- **Token policy:** `GITHUB_TOKEN` is read by the pipeline but never logged, serialized, or written to
  evidence files. `GPT_OSS_API_KEY` is equally never logged.
- **Approval tokens are not secrets.** `APPROVE_LIVE_PR` and `APPROVE_MERGE_PR` are human operator phrases
  that authorize destructive actions. Do not store them as CI secrets.
- **Source of truth hierarchy:** NuGet package (primary) → DocFX markdown (descriptions only) →
  existing example repos (style hints and fixture sources only).
- **Gate order is enforced.** Do not bypass any verification gate. The `AGENTS.md` file documents the
  governance rules and must be read before contributing automation.
- **Evidence before exiting.** Even on partial failure, the pipeline writes evidence JSON. If a run
  exits without evidence, something went wrong in the early stages.
- **Stale `AGENTS.md`.** The governance file has correct rules but incorrect env var names. Trust
  `docs/ci/environment-variables.md` for the authoritative env var list.
- **DllReflector safety.** The .NET reflection tool uses `MetadataLoadContext` exclusively. It never
  executes code from the reflected assembly. This is a hard invariant — do not add `Invoke` calls.
