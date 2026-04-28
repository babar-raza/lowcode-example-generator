# Plugin Example Generation — Execution-Ready Plan

**Version:** 1.2.0
**Date:** 2026-04-27 (patched: 2026-04-28)
**Status:** STRUCTURE MIGRATION COMPLETE — READY FOR WAVE 1A
**Repo:** https://github.com/babar-raza/lowcode-example-generator
**Plan Author:** Planning Agent (Claude)
**Current-State Evidence:** `docs/discovery/current-state.md`
**Run Record:** `workspace/runs/plan-v1.2.0-20260428/run-record.json`

> **v1.1.0 → v1.2.0 Patch Applied.** This plan was further amended to add: (1) production-grade repository structure v2 (Section 27-28), (2) mandatory concurrency safety model with Gate 0 and taskcards TC-00A/B/C (Section 29), (3) migration and rollback plan (TC-00D/E in Section 28), (4) gitignore policy (Section 30), and (5) updated execution order. See Section 25 for the full correction log. Implementation may not begin until structure migration passes.

---

## 1. Objective

Build a continuous agentic pipeline that:

1. Detects plugin-capable Aspose .NET products from shipped NuGet packages.
2. Generates executable C# examples for their LowCode or Plugin APIs.
3. Validates those examples through compiler, runtime, output, and verifier gates.
4. Publishes accepted examples to an official GitHub repository.
5. Runs autonomously each month when NuGet packages are upgraded.

Core principle:

```
The package proves the API.
The compiler proves the code.
The runtime proves the behavior.
The verifier proves publish-readiness.
The LLM only proposes.
```

---

## 2. Scope

- Aspose .NET products distributed via NuGet.
- Products exposing plugin-oriented APIs under configured namespace patterns (e.g., `Aspose.Cells.LowCode`, `Aspose.Cells.Plugins`).
- SDK-style, one-project-per-scenario C# console examples.
- Automated monthly delta-based regeneration.
- PR-based publishing with mandatory evidence package.

**Pilot product:** Aspose.Cells for .NET

---

## 3. Non-Goals

- Generating examples for APIs outside the reflected NuGet catalog.
- Generating GUI, WPF, or web application examples.
- Generating Python, Java, or other language examples.
- Replacing existing Aspose official product examples repos.
- Duplicating the `example-reviewer` compiler/runner logic — integrate with it instead.
- Direct push to `main` in any circumstances.
- Generating examples without a passing fixture strategy.
- Blindly regenerating all examples every month (must be delta-based).
- Processing disabled family configs in any scheduled or manual run.

---

## 4. Current-State Findings

**Full evidence:** `docs/discovery/current-state.md`

Summary:

| Question | Answer |
|---|---|
| Pipeline or generation infrastructure? | NONE — greenfield |
| Family configs? | NONE |
| NuGet extraction or reflection? | NONE |
| example-reviewer integration? | NONE |
| .NET validation scripts? | NONE |
| CI workflows? | NONE |
| Existing reusable code? | NONE |
| Existing tests? | NONE |

**Conclusion:** This is a complete greenfield. All modules must be built from scratch.

**Remote:** `https://github.com/babar-raza/lowcode-example-generator`
**Owner:** `babar-raza` (same owner as `example-reviewer`)

---

## 5. Source-of-Truth Model

### Primary — Official NuGet Package

Authoritative for:

```
Namespaces / Types / Constructors / Methods / Properties
Enums / Overloads / Attributes / Obsolete markers
XML summaries / Package version / Assembly version
Target framework / Plugin namespace presence
```

### Secondary — DocFX Markdown API Reference

Use only for:

```
Human-readable descriptions
Documentation comparison
Drift detection
Extra explanation context
```

DocFX must never override reflection.

### Tertiary — Existing Aspose .NET Example Repos

Use only for:

```
Style hints
Fixture file discovery
Scenario inspiration
Common input/output patterns
```

Every existing example must be validated against the current reflected API before reuse.

### Publishing Gate — Validation Chain

```
dotnet restore → dotnet build → dotnet run → output validation → example-reviewer
```

An example is publish-ready only when all five gates pass.

### Mandatory Pre-Generation Gate — Source-of-Truth Proof

```
workspace/verification/latest/{family}-source-of-truth-proof.json
  must exist and have eligibility_status = "eligible"
  before any scenario planning or LLM generation starts
```

---

## 6. Architecture

```
NuGet Package
     │
     ▼
nuget_fetcher ──► dependency_resolver ──► nupkg_extractor ──► reflection_catalog ──► plugin_detector
                                                                       │
                                                                 api_delta_engine
                                                                       │
                                        ┌──────────────────────────────┼──────────────────────────┐
                                        │                              │                          │
                               fixture_registry               example_miner             scenario_planner
                                        │                              │                          │
                                        └──────────────────────────────┼──────────────────────────┘
                                                                       │
                                              [source-of-truth proof gate]
                                                                       │
                                                                  llm_router
                                                                       │
                                                              [prompt packet]
                                                                       │
                                                               generator
                                                                       │
                                                    [workspace/runs/{run_id}/generated/ only]
                                                                       │
                                         dotnet restore → dotnet build → dotnet run
                                                                       │
                                                             output_validator
                                                                       │
                                                    verifier_bridge (example-reviewer)
                                                                       │
                                                                  publisher
                                                                       │
                                                               GitHub PR
```

---

## 7. Repository Structure Decision (v1 — SUPERSEDED)

> **SUPERSEDED by Section 28 (Repository Structure v2).** The structure below was the v1.1.0 design. It has been replaced because it spreads 13+ folders across the repo root, mixes stable definitions with runtime output, and lacks gitignore policy. Refer to Section 27 for the architecture decision record and Section 28 for the production-grade v2 layout. All new implementation work must use the v2 structure.

**This repo (`lowcode-example-generator`) = the pipeline repo.**

**Separate repo (`aspose-plugins-examples-dotnet`) = the published examples repo.**

### Pipeline Repo Structure (this repo) — v1, DEPRECATED

```
lowcode-example-generator/
  README.md
  pyproject.toml
  AGENTS.md

  configs/
    families/
      cells.yml                         ← active pilot config (enabled: true)
      _templates/
        family-template.yml             ← canonical template for new families
      disabled/
        words.yml                       ← not yet active (enabled: false)
        pdf.yml                         ← not yet active (enabled: false)
    plugin-namespace-patterns.yml
    llm-routing.yml
    verifier.yml
    github-publishing.yml

  src/
    plugin_examples/
      __init__.py
      family_config/                    ← [ADDED v1.1.0]
        __init__.py
        loader.py                       ← load + validate configs; reject disabled configs
        models.py                       ← FamilyConfig dataclass / typed model
        validator.py                    ← jsonschema validation against schema file
      package_watcher/
        __init__.py
        watcher.py
      nuget_fetcher/
        __init__.py
        fetcher.py
        cache.py
        dependency_resolver.py          ← [ADDED v1.1.0] read .nuspec, download deps
      nupkg_extractor/
        __init__.py
        extractor.py
        framework_selector.py
      reflection_catalog/
        __init__.py
        reflector.py                    ← invokes tools/DllReflector subprocess
        catalog_builder.py
        schema_validator.py
      plugin_detector/
        __init__.py
        detector.py
        proof_reporter.py               ← [ADDED v1.1.0] writes source-of-truth proof JSON
      api_delta/
        __init__.py
        delta_engine.py
        impact_mapper.py
      fixture_registry/
        __init__.py
        registry.py
        fixture_fetcher.py
      example_miner/
        __init__.py
        miner.py
        symbol_validator.py
      scenario_planner/
        __init__.py
        planner.py
        scenario_catalog.py
      llm_router/
        __init__.py
        router.py
        preflight.py
        providers/
          __init__.py
          professionalize.py
          ollama.py
      generator/
        __init__.py
        packet_builder.py
        code_generator.py
        project_generator.py
        manifest_writer.py
      verifier_bridge/
        __init__.py
        bridge.py
        dotnet_runner.py
        output_validator.py
      publisher/
        __init__.py
        publisher.py
        pr_builder.py
      reporting/
        __init__.py
        reporter.py
        evidence_packager.py

  tools/
    DllReflector/
      DllReflector.csproj
      Program.cs                        ← metadata-only reflection, no type instantiation

  prompts/
    scenario-planner.md
    example-generator.md
    example-repair.md
    semantic-review.md

  schemas/
    family-config.schema.json
    api-catalog.schema.json
    scenario.schema.json
    example-manifest.schema.json
    validation-result.schema.json
    scenario-packet.schema.json

  runs/
    .gitkeep

  tests/
    unit/
      test_family_config.py             ← [ADDED v1.1.0]
      test_nuget_fetcher.py
      test_dependency_resolver.py       ← [ADDED v1.1.0]
      test_nupkg_extractor.py
      test_reflection_catalog.py
      test_plugin_detector.py
      test_api_delta.py
      test_fixture_registry.py
      test_scenario_planner.py
      test_llm_router.py
      test_generator.py
      test_verifier_bridge.py
      test_publisher.py
    integration/
      test_cells_pipeline.py
    fixtures/
      sample-cells.nupkg  (symlink or test double)
      sample-api-catalog.json

  docs/
    discovery/
      current-state.md
      example-reviewer-integration-surface.md   ← [ADDED by TC-00X]
    plans/
      plugin-example-generation-execution-plan.md
    architecture.md
    family-config.md
    verifier-integration.md
    monthly-runbook.md
    publishing-model.md

  .github/
    workflows/
      monthly-package-refresh.yml
      build-and-test.yml
```

---

## 8. Published Example Structure Decision

Separate repo: `aspose-plugins-examples-dotnet` (to be created by publisher on first run)

```
aspose-plugins-examples-dotnet/
  README.md
  LICENSE
  global.json
  NuGet.config
  Directory.Build.props
  Directory.Packages.props
  Aspose.Plugins.Examples.sln

  .github/
    workflows/
      build-and-verify.yml
      monthly-package-refresh.yml

  configs/
    families/
      cells.yml
    verifier.yml

  fixtures/
    cells/
      xlsx/
        basic-workbook.xlsx
      csv/
        simple-data.csv

  examples/
    cells/
      lowcode/
        convert-xlsx-to-pdf/
          ConvertXlsxToPdf.csproj
          Program.cs
          README.md
          example.manifest.json
          expected-output.json
        convert-xlsx-to-html/
          ConvertXlsxToHtml.csproj
          Program.cs
          README.md
          example.manifest.json
          expected-output.json

  tests/
    Aspose.Plugins.Examples.SmokeTests/
      Aspose.Plugins.Examples.SmokeTests.csproj
      ExampleDiscoveryTests.cs
      ExampleExecutionTests.cs
      OutputValidationTests.cs

  manifests/
    product-inventory.json
    package-lock.json
    api-catalog-index.json
    scenario-catalog.json
    fixture-registry.json
    example-index.json

  verification/
    latest/
      validation-results.json
      example-reviewer-results.json
      rejected-scenarios.json
      api-delta-report.json

  artifacts/
    .gitkeep
```

> Note: `words.yml` and `pdf.yml` are not included in the published examples repo until those families are enabled in the pipeline repo.

User run command:

```bash
dotnet run --project examples/cells/lowcode/convert-xlsx-to-pdf/ConvertXlsxToPdf.csproj
```

---

## 9. Family Config Schema

### Schema file: `pipeline/schemas/family-config.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FamilyConfig",
  "type": "object",
  "required": ["family", "display_name", "enabled", "status", "nuget", "plugin_detection", "github", "fixtures", "existing_examples", "generation", "validation", "llm"],
  "properties": {
    "family": { "type": "string" },
    "display_name": { "type": "string" },
    "enabled": {
      "type": "boolean",
      "description": "If false, this config is never processed by the package watcher or monthly runner."
    },
    "status": {
      "type": "string",
      "enum": ["active", "disabled", "experimental"],
      "description": "active = in production pipeline. disabled = excluded entirely. experimental = runs but does not publish."
    },
    "nuget": {
      "type": "object",
      "required": ["package_id", "version_policy"],
      "properties": {
        "package_id": { "type": "string" },
        "version_policy": { "enum": ["latest-stable", "pinned"] },
        "pinned_version": { "type": ["string", "null"] },
        "allow_prerelease": {
          "type": "boolean",
          "default": false,
          "description": "If false, pre-release NuGet versions are excluded from version resolution."
        },
        "target_framework_preference": {
          "type": "array",
          "items": { "type": "string" },
          "minItems": 1,
          "description": "Ordered preference list. First matching lib/ folder wins. See Section 9 note on Windows runners."
        },
        "dependency_resolution": {
          "type": "object",
          "properties": {
            "enabled": {
              "type": "boolean",
              "default": true,
              "description": "If true, .nuspec dependencies are downloaded and extracted for DllReflector dependency resolution."
            },
            "max_depth": {
              "type": "integer",
              "default": 2,
              "description": "Maximum transitive dependency depth to resolve."
            }
          }
        }
      }
    },
    "plugin_detection": {
      "type": "object",
      "required": ["namespace_patterns"],
      "properties": {
        "namespace_patterns": {
          "type": "array",
          "items": { "type": "string" },
          "minItems": 1
        }
      }
    },
    "github": {
      "type": "object",
      "required": ["official_examples_repo", "published_plugin_examples_repo"],
      "properties": {
        "official_examples_repo": {
          "type": "object",
          "required": ["owner", "repo", "branch"],
          "properties": {
            "owner": { "type": "string" },
            "repo": { "type": "string" },
            "branch": { "type": "string" }
          }
        },
        "published_plugin_examples_repo": {
          "type": "object",
          "required": ["owner", "repo", "branch"],
          "properties": {
            "owner": { "type": "string" },
            "repo": { "type": "string" },
            "branch": { "type": "string" }
          }
        }
      }
    },
    "fixtures": {
      "type": "object",
      "required": ["sources"],
      "properties": {
        "sources": { "type": "array" }
      }
    },
    "existing_examples": {
      "type": "object",
      "required": ["sources"],
      "properties": {
        "sources": { "type": "array" }
      }
    },
    "generation": {
      "type": "object",
      "required": ["min_examples_per_family", "max_examples_per_monthly_run"],
      "properties": {
        "min_examples_per_family": { "type": "integer", "minimum": 1 },
        "max_examples_per_monthly_run": { "type": "integer", "minimum": 1 },
        "allow_new_fixtures": { "type": "boolean" },
        "allow_generated_input_files": { "type": "boolean" }
      }
    },
    "validation": {
      "type": "object",
      "properties": {
        "require_restore": { "type": "boolean" },
        "require_build": { "type": "boolean" },
        "require_run": { "type": "boolean" },
        "require_output_validation": { "type": "boolean" },
        "require_example_reviewer": { "type": "boolean" },
        "runtime_runner": {
          "type": "string",
          "enum": ["linux", "windows", "auto"],
          "default": "auto",
          "description": "auto = linux unless only .NET Framework assemblies are available, in which case windows is required."
        }
      }
    },
    "llm": {
      "type": "object",
      "required": ["provider_order"],
      "properties": {
        "provider_order": {
          "type": "array",
          "items": { "type": "string" },
          "minItems": 1
        }
      }
    }
  }
}
```

### Target Framework Preference Rule

The default preference order is:

```yaml
target_framework_preference:
  - netstandard2.0
  - netstandard2.1
  - net8.0
  - net6.0
  - net48
```

`netstandard2.0` is listed first because it is the broadest compatibility target and is commonly the best-maintained DLL in multi-target NuGet packages.

**Windows runner rule:** If the framework selector selects `net48` or any other `netXXX` (Windows-only .NET Framework moniker), it must set `validation.runtime_runner = "windows"` in the extraction manifest and the pipeline must route `dotnet run` to a Windows CI runner. This is recorded in `extraction-manifest.json` under `requires_windows_runner: true`.

### Pilot config: `pipeline/configs/families/cells.yml`

```yaml
family: cells
display_name: Aspose.Cells for .NET
enabled: true
status: active

nuget:
  package_id: Aspose.Cells
  version_policy: latest-stable
  pinned_version: null
  allow_prerelease: false
  target_framework_preference:
    - netstandard2.0
    - netstandard2.1
    - net8.0
    - net6.0
    - net48
  dependency_resolution:
    enabled: true
    max_depth: 2

plugin_detection:
  namespace_patterns:
    - Aspose.Cells.LowCode
    - Aspose.Cells.LowCode.*
    - Aspose.Cells.Plugins
    - Aspose.Cells.Plugins.*

github:
  official_examples_repo:
    owner: aspose-cells
    repo: Aspose.Cells-for-.NET
    branch: master

  published_plugin_examples_repo:
    owner: aspose
    repo: aspose-plugins-examples-dotnet
    branch: main

fixtures:
  sources:
    - type: github
      owner: aspose-cells
      repo: Aspose.Cells-for-.NET
      branch: master
      paths:
        - Examples/Data

existing_examples:
  sources:
    - type: github
      owner: aspose-cells
      repo: Aspose.Cells-for-.NET
      branch: master
      paths:
        - Examples/CSharp

generation:
  min_examples_per_family: 3
  max_examples_per_monthly_run: 10
  allow_new_fixtures: true
  allow_generated_input_files: true

validation:
  require_restore: true
  require_build: true
  require_run: true
  require_output_validation: true
  require_example_reviewer: true
  runtime_runner: auto

llm:
  provider_order:
    - llm_professionalize
    - ollama
```

### Disabled configs (placeholder only)

`pipeline/configs/families/disabled/words.yml` and `pipeline/configs/families/disabled/pdf.yml` must each contain:

```yaml
enabled: false
status: disabled
family: words       # (or pdf)
display_name: Aspose.Words for .NET   # (or Aspose.PDF)
# Remaining fields are intentionally incomplete.
# Complete and move to pipeline/configs/families/ when ready to enable.
```

The `family_config/loader.py` must:
- Refuse to load any config where `enabled: false`.
- Refuse to load any config where `status: disabled`.
- Refuse to process any config found under `pipeline/configs/families/disabled/` regardless of field values.
- Log a clear message when a disabled config is skipped: `[SKIP] {path} — disabled`.

### Template config

`pipeline/configs/families/_templates/family-template.yml` contains all fields with placeholder values and comments. It is never loaded by the pipeline.

---

## 10. Pipeline Stages

| # | Stage | Module | Gate(s) |
|---|---|---|---|
| -1 | Concurrency preflight | (agent protocol) | Gate 0 |
| 0 | example-reviewer discovery | (manual/agent) | TC-00X evidence gate |
| 1 | Package watcher | `package_watcher` | — |
| 2 | NuGet fetch | `nuget_fetcher` | Gate 1 |
| 3 | Dependency resolution | `nuget_fetcher.dependency_resolver` | Gate 1b |
| 4 | `.nupkg` extract | `nupkg_extractor` | Gates 2, 3 |
| 5 | Reflection catalog build | `reflection_catalog` | Gate 4 |
| 6 | Plugin namespace detect | `plugin_detector` | Gate 5 |
| 7 | Source-of-truth proof | `plugin_detector.proof_reporter` | Gate 5b |
| 8 | API delta calculate | `api_delta` | Gate 6 |
| 9 | Fixture registry | `fixture_registry` | Gate 7 |
| 10 | Existing example mine | `example_miner` | — |
| 11 | Scenario plan | `scenario_planner` | Gate 8 |
| 12 | LLM preflight | `llm_router` | Gate 9 |
| 13 | Generation packet build | `generator.packet_builder` | Gates 10, 11 |
| 14 | Example project generate | `generator.project_generator` | — |
| 15 | Restore | `verifier_bridge.dotnet_runner` | Gate 12 |
| 16 | Build | `verifier_bridge.dotnet_runner` | Gate 13 |
| 17 | Run | `verifier_bridge.dotnet_runner` | Gate 14 |
| 18 | Output validation | `verifier_bridge.output_validator` | Gate 15 |
| 19 | example-reviewer | `verifier_bridge.bridge` | Gate 16 |
| 20 | PR publish | `publisher` | Gates 17, 18 |
| 21 | Reporting | `reporting` | — |

---

## 11. Taskcards

---

### EPIC-00A: Concurrency Safety and Structure Migration

---

**Taskcard ID:** TC-00A
**Title:** Concurrency Preflight and Run Record
**Objective:** Before any implementation work begins, verify repository ownership, check for parallel agent work, and create a run record that declares intent and file scope. This is Gate 0.

**Dependencies:** None — this is the first taskcard in any execution wave.

**Inputs:**
- Git repository state (status, log, branches, stashes, worktrees)
- Any existing `workspace/runs/*/run-record.json` files

**Actions:**
1. Run and record:
   - `git status` (staged, unstaged, untracked)
   - `git stash list`
   - `git branch -a`
   - `git worktree list`
   - `git log --oneline -5`
   - Check for lock files (`*.lock`, `.git/index.lock`)
   - Check for active run records in `workspace/runs/`
2. Identify all files this task will read or modify.
3. Detect overlap with other active or recent work using this classification:
   - `no_overlap`: proceed freely
   - `adjacent_overlap`: proceed with caution, document why it is safe
   - `direct_overlap`: STOP and report immediately
   - `unknown_ownership`: assume unsafe, STOP unless evidence proves ownership
4. Create `workspace/runs/{run_id}/run-record.json` with:
   - `owner`, `task_name`, `start_time`, `branch`, `worktree`
   - `intended_files`, `intended_directories`, `purpose`, `expected_outputs`
   - `overlap_classification`, `overlap_evidence`, `safety_decision`
   - `rollback_notes`, `verification_commands`
5. Only proceed if overlap classification is `no_overlap` or `adjacent_overlap` with documented rationale.

**Outputs:**
- `workspace/runs/{run_id}/run-record.json`

**Acceptance Criteria:**
- Run record exists with all required fields.
- Overlap classification is explicit and evidence-backed.
- No `direct_overlap` or `unknown_ownership` classification allows proceeding.
- Safety decision is documented before any file writes occur.

**Verification Commands:**
```bash
cat workspace/runs/{run_id}/run-record.json | python -m json.tool
git status
```

**Failure Handling:**
- If `direct_overlap` detected: STOP. Report conflicting files and suspected owner.
- If `unknown_ownership` detected: STOP. Do not guess. Escalate to human.
- Never use `git reset`, `git stash pop`, or auto-merge to resolve detected overlap.

**Evidence Files:**
- `workspace/runs/{run_id}/run-record.json`

---

**Taskcard ID:** TC-00B
**Title:** Midflight Ownership Recheck
**Objective:** Before each major write phase within a task (e.g., before file moves, before test runs, before commit preparation), re-verify that the repository state has not been modified by another agent or human.

**Dependencies:** TC-00A (run record must exist)

**Trigger:** This is not a standalone taskcard. It is a mandatory protocol step embedded in every implementation taskcard. Every taskcard's actions must include a midflight recheck before:
- The first file write
- Any file move or rename
- Running tests
- Preparing a commit

**Actions:**
1. Run `git status` and compare against run record's `intended_files`.
2. Check for new untracked files not in the run record.
3. Check for modified files not in the run record.
4. Verify no new lock files or run records from other agents appeared.
5. If any unexpected state is found:
   - Classify as `adjacent_overlap` or `direct_overlap`.
   - If `direct_overlap`: STOP immediately. Do not write.
   - If `adjacent_overlap`: document why proceeding is safe. Continue.

**Outputs:**
- Inline log entry in the active run record (append to `midflight_checks` array).

**Acceptance Criteria:**
- Every implementation taskcard confirms at least one midflight check was performed.
- No implementation taskcard may commit files without a passing midflight check.

---

**Taskcard ID:** TC-00C
**Title:** Pre-Commit Scope Verification
**Objective:** Before any git commit, verify that only files declared in the run record were modified. Confirm no unrelated work was overwritten, moved, deleted, reformatted, or staged.

**Dependencies:** TC-00A (run record), TC-00B (midflight checks passed)

**Trigger:** This is a mandatory protocol step before every `git add` and `git commit`.

**Actions:**
1. Run `git status` and `git diff --name-status`.
2. Compare modified/added/deleted files against `intended_files` in the run record.
3. For each changed file:
   - If in `intended_files`: PASS.
   - If not in `intended_files` but clearly related (e.g., auto-generated `.pyc`): document and PASS.
   - If not in `intended_files` and unexpected: STOP. Do not commit.
4. Verify no files outside the declared scope were reformatted, moved, or deleted.
5. Produce a final concurrency report at `workspace/runs/{run_id}/concurrency-report.json` with:
   - `touched_files`, `moved_files`, `deleted_files`, `created_files`
   - `detected_overlaps`, `ownership_decisions`, `safety_decisions`
   - `remaining_risks`, `verification_commands_run`, `final_git_status`

**Outputs:**
- `workspace/runs/{run_id}/concurrency-report.json`
- Clean `git status` confirming only expected changes

**Acceptance Criteria:**
- Concurrency report exists with all required fields.
- No unrelated files were changed.
- `final_git_status` in the report matches actual `git status`.

**Verification Commands:**
```bash
git status
git diff --stat
git diff --name-status
cat workspace/runs/{run_id}/concurrency-report.json | python -m json.tool
```

**Failure Handling:**
- If unexpected files are staged: `git reset HEAD <file>` for those files only. Do not reset everything.
- If unexpected modifications exist: investigate ownership before any action. Do not overwrite.

**Evidence Files:**
- `workspace/runs/{run_id}/concurrency-report.json`

---

### EPIC-00: Pre-Implementation Discovery

---

**Taskcard ID:** TC-00X
**Title:** Inspect example-reviewer Integration Surface
**Objective:** Before implementing `verifier_bridge`, establish exactly how `example-reviewer` can be integrated. Document the findings in a durable discovery file so TC-15 has no ambiguity.

**Dependencies:** TC-01 (repo state known)

**Inputs:**
- `https://github.com/babar-raza/example-reviewer`
- GitHub API or `git clone` of the repo

**Actions:**
1. Clone or inspect `https://github.com/babar-raza/example-reviewer`.
2. Inventory the repo: README, source structure, entry points, config files, test files.
3. Determine and document:
   - Does a CLI exist? What is the command signature?
   - Does a Python module API exist? What is the import path?
   - Does an HTTP API exist? What endpoints?
   - What is the expected input format (file paths, JSON, directory structure)?
   - What is the expected output format (stdout, JSON file, exit code)?
   - What config files does it require (family config, API catalog, etc.)?
   - What dependencies does it need (Python packages, .NET SDK, etc.)?
   - What is the best integration mode for TC-15?
   - What gaps exist that must be fixed or worked around before TC-15 can be implemented?
4. Write findings to `docs/discovery/example-reviewer-integration-surface.md`.

**Outputs:**
- `docs/discovery/example-reviewer-integration-surface.md`

**Acceptance Criteria:**
- All 9 questions above are answered with evidence from actual repo files — not from memory or this plan's description.
- Best integration mode is clearly recommended.
- Gaps are listed as blocking or non-blocking.
- TC-15 can begin implementation without further research.

**Verification Commands:**
```bash
test -f docs/discovery/example-reviewer-integration-surface.md
grep -c "integration_mode:" docs/discovery/example-reviewer-integration-surface.md
```

**Failure Handling:**
- If the repo is private or unavailable, record that as a blocker and escalate to human immediately.
- If no CLI and no Python module exist, document the gap and propose a subprocess-based workaround.

**Evidence Files:**
- `docs/discovery/example-reviewer-integration-surface.md`

**Status:** PENDING (must complete before TC-15 begins)

---

### EPIC-01: Repository and Architecture Discovery

---

**Taskcard ID:** TC-01
**Title:** Discover Current Repo State
**Objective:** Establish baseline facts about the repo before any implementation.

**Dependencies:** None

**Inputs:**
- Git repository contents
- `.git/config` for remote URL

**Actions:**
1. Run `glob **/*` to inventory all files.
2. Read `README.md` if present.
3. Read `.git/config` for remote.
4. Answer all 15 mandatory investigation questions with file evidence.
5. Record repo map, constraints, and recommended execution starting point.

**Outputs:**
- `docs/discovery/current-state.md`

**Acceptance Criteria:**
- All 15 questions answered with file evidence or explicit "NOT FOUND".
- No assumptions stated without evidence.

**Verification Commands:**
```bash
test -f docs/discovery/current-state.md && wc -l docs/discovery/current-state.md
```

**Failure Handling:**
- If repo access is denied, stop and report to human.

**Evidence Files:**
- `docs/discovery/current-state.md`

**Status:** COMPLETE (greenfield confirmed, evidence in `docs/discovery/current-state.md`)

---

### EPIC-02: Family Config System

---

**Taskcard ID:** TC-02
**Title:** Define and Validate Family Config Schema and Config Module
**Objective:** Create the durable per-family configuration schema, the active pilot config, the disabled placeholder configs, and the Python family_config module. Make schema validation executable.

**Dependencies:** TC-01

**Inputs:**
- Discovery findings (TC-01)
- Section 9 of this plan

**Actions:**
1. Create `pipeline/schemas/family-config.schema.json` (see Section 9).
2. Create `pipeline/configs/families/cells.yml` with `enabled: true`, `status: active` (see Section 9).
3. Create `pipeline/configs/families/disabled/words.yml` with `enabled: false`, `status: disabled` (minimal placeholder).
4. Create `pipeline/configs/families/disabled/pdf.yml` with `enabled: false`, `status: disabled` (minimal placeholder).
5. Create `pipeline/configs/families/_templates/family-template.yml` with all fields and inline comments.
6. Create `configs/plugin-namespace-patterns.yml` with global pattern registry.
7. Create `configs/llm-routing.yml` with provider order and preflight rules.
8. Create `configs/verifier.yml` with gate configuration.
9. Create `configs/github-publishing.yml` with PR and branch rules.
10. Create `src/plugin_examples/family_config/__init__.py`.
11. Create `src/plugin_examples/family_config/models.py` with a `FamilyConfig` typed dataclass/model.
12. Create `src/plugin_examples/family_config/validator.py` with jsonschema validation.
13. Create `src/plugin_examples/family_config/loader.py`:
    - Load YAML from path.
    - Reject configs where `enabled: false` or `status: disabled`.
    - Reject any config under `pipeline/configs/families/disabled/` path prefix.
    - Log `[SKIP] {path} — disabled` for any rejected config.
    - Validate against schema.
    - Return typed `FamilyConfig` model.
14. Write `tests/unit/test_family_config.py` covering:
    - Valid `cells.yml` passes validation.
    - Config missing `plugin_detection.namespace_patterns` fails.
    - Config missing `nuget.package_id` fails.
    - Config with `version_policy: invalid` fails.
    - Config with `enabled: false` is rejected by loader.
    - Config from `disabled/` path is rejected by loader regardless of `enabled` field.
    - Config missing `enabled` field fails schema validation.
    - Config missing `status` field fails schema validation.

**Outputs:**
- `pipeline/schemas/family-config.schema.json`
- `pipeline/configs/families/cells.yml`
- `pipeline/configs/families/disabled/words.yml`
- `pipeline/configs/families/disabled/pdf.yml`
- `pipeline/configs/families/_templates/family-template.yml`
- `configs/plugin-namespace-patterns.yml`
- `configs/llm-routing.yml`
- `configs/verifier.yml`
- `configs/github-publishing.yml`
- `src/plugin_examples/family_config/__init__.py`
- `src/plugin_examples/family_config/models.py`
- `src/plugin_examples/family_config/validator.py`
- `src/plugin_examples/family_config/loader.py`
- `tests/unit/test_family_config.py`

**Acceptance Criteria:**
- `python -m pytest tests/unit/test_family_config.py` passes all 8+ test cases.
- `cells.yml` validates against schema without errors.
- `disabled/words.yml` is rejected by the loader.
- An intentionally invalid config sample fails schema validation.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_family_config.py -v
python -c "from src.plugin_examples.family_config.loader import load_family_config; cfg = load_family_config('configs/families/cells.yml'); print(cfg.family)"
python -c "from src.plugin_examples.family_config.loader import load_family_config; load_family_config('configs/families/disabled/words.yml')"
# Expected: last command raises DisabledFamilyError
```

**Failure Handling:**
- If `jsonschema` is unavailable, add to `pyproject.toml` before re-running.

**Evidence Files:**
- `pipeline/schemas/family-config.schema.json`
- `pipeline/configs/families/cells.yml`
- `tests/unit/test_family_config.py`

---

### EPIC-03: NuGet Source of Truth

---

**Taskcard ID:** TC-03
**Title:** Build NuGet Fetcher with Dependency Resolution
**Objective:** Download and cache official NuGet packages and their declared dependencies. Record version, hash, and provenance for all packages. Dependency DLLs are required by the DllReflector to load the primary DLL without errors.

**Dependencies:** TC-02

**Inputs:**
- `pipeline/configs/families/cells.yml`
- NuGet.org v3 API: `https://api.nuget.org/v3/index.json`

**Actions:**
1. Create `src/plugin_examples/nuget_fetcher/fetcher.py`.
   - Accept family config as input.
   - Respect `allow_prerelease: false` — filter out pre-release versions.
   - Resolve latest stable (or pinned) version from NuGet v3 registration endpoint.
   - Download `.nupkg` to: `workspace/runs/{run_id}/packages/{family}/{package_id}.{version}.nupkg`.
   - Record SHA-256 hash of downloaded file.
   - Record source URL.
   - Write `workspace/runs/{run_id}/packages/{family}/download-manifest.json`.
2. Create `src/plugin_examples/nuget_fetcher/cache.py`.
   - Check cache by path + hash before re-download.
   - Return cached path and manifest if hash matches.
3. Create `src/plugin_examples/nuget_fetcher/dependency_resolver.py`.
   - Read `.nuspec` from the downloaded `.nupkg` (it is inside the zip).
   - Extract `<dependencies>` for the selected target framework group.
   - For each dependency: check if it's already in cache; if not, download it.
   - Download to: `workspace/runs/{run_id}/packages/{family}/deps/{dep_package_id}.{dep_version}.nupkg`.
   - Record each dependency: `package_id`, `version`, `sha256`, `source_url`, `cached_path`.
   - Respect `nuget.dependency_resolution.max_depth` to limit transitive recursion.
   - Write `workspace/runs/{run_id}/packages/{family}/dependency-manifest.json`.
4. Update `workspace/manifests/package-lock.json` to include both primary and dependency records.
5. Write `tests/unit/test_nuget_fetcher.py` covering:
   - Version resolution returns a semver string.
   - Pre-release versions are excluded when `allow_prerelease: false`.
   - Download produces a file at expected path.
   - Hash is recorded.
   - Cache hit skips re-download.
   - Nonexistent package raises clear error.
6. Write `tests/unit/test_dependency_resolver.py` covering:
   - `.nuspec` is correctly parsed for the selected framework group.
   - Dependency packages are downloaded and recorded.
   - `dependency-manifest.json` contains all entries.
   - max_depth is respected (depth 1 test and depth 2 test).

**Outputs:**
- `src/plugin_examples/nuget_fetcher/fetcher.py`
- `src/plugin_examples/nuget_fetcher/cache.py`
- `src/plugin_examples/nuget_fetcher/dependency_resolver.py`
- `workspace/runs/{run_id}/packages/cells/download-manifest.json`
- `workspace/runs/{run_id}/packages/cells/dependency-manifest.json`
- `workspace/manifests/package-lock.json`

**Acceptance Criteria:**
- Running fetcher for `Aspose.Cells` produces a `.nupkg` at expected path.
- `download-manifest.json` contains `package_id`, `version`, `sha256`, `source_url`, `cached_path`.
- `dependency-manifest.json` lists all direct dependencies with hashes.
- Pre-release versions are not selected.
- Re-run uses cache.
- Both test files pass.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_nuget_fetcher.py tests/unit/test_dependency_resolver.py -v
python -c "from src.plugin_examples.nuget_fetcher.fetcher import fetch_package; fetch_package('configs/families/cells.yml', run_id='test-01')"
cat runs/test-01/packages/cells/dependency-manifest.json | python -m json.tool
```

**Failure Handling:**
- NuGet.org unreachable → clear network error, no silent fallback to stale cache.
- Package not found → fail with package-not-found error, halt pipeline.
- Dependency download fails → record failure in manifest, log warning. DllReflector will attempt to proceed; if it cannot, it fails at TC-05.

**Evidence Files:**
- `workspace/runs/{run_id}/packages/cells/download-manifest.json`
- `workspace/runs/{run_id}/packages/cells/dependency-manifest.json`
- `workspace/manifests/package-lock.json`

---

**Taskcard ID:** TC-04
**Title:** Build NuGet Extractor with Framework Selector and Dependency Extraction
**Objective:** Extract DLL and XML documentation from the primary `.nupkg`. Extract dependency DLLs into a resolved libs folder that `DllReflector` can use. Select target framework deterministically. Detect when a Windows runner is required.

**Dependencies:** TC-03

**Inputs:**
- `.nupkg` file from TC-03 (primary)
- Dependency `.nupkg` files from TC-03 (deps)
- `target_framework_preference` from family config

**Actions:**
1. Create `src/plugin_examples/nupkg_extractor/extractor.py`.
   - Unzip primary `.nupkg` to `workspace/runs/{run_id}/extracted/{family}/primary/`.
   - Enumerate `lib/` folders.
   - Select framework using preference list (first match wins).
   - Locate `{package_id}.dll` in selected framework folder.
   - Locate `{package_id}.xml` in same folder.
   - If XML not found, write to `workspace/runs/{run_id}/extracted/{family}/warnings.json` — do not fail silently.
   - Write `workspace/runs/{run_id}/extracted/{family}/extraction-manifest.json`.
2. Create `src/plugin_examples/nupkg_extractor/framework_selector.py`.
   - Implement preference-list framework selection.
   - Return: selected framework, selection reason, `requires_windows_runner` boolean.
   - **Windows runner rule:** If selected framework is `net48` or any `netXXX` (Windows-only .NET Framework TFM), set `requires_windows_runner: true`.
   - Record `requires_windows_runner` in `extraction-manifest.json`.
3. Add dependency extraction to `extractor.py`:
   - For each dependency `.nupkg` in `workspace/runs/{run_id}/packages/{family}/deps/`:
     - Unzip to `workspace/runs/{run_id}/extracted/{family}/deps/{dep_id}/`.
     - Select same target framework (or best match).
     - Locate `{dep_id}.dll`.
     - Record dep DLL path.
   - Collect all dep DLL paths into `workspace/runs/{run_id}/extracted/{family}/resolved-libs/`.
   - Write all dep paths to `extraction-manifest.json` under `dependency_dll_paths`.
4. Write `tests/unit/test_nupkg_extractor.py` covering:
   - Framework is selected deterministically from preference list.
   - `netstandard2.0` takes priority over `net8.0` when both available.
   - `net48` selection sets `requires_windows_runner: true`.
   - DLL path is recorded.
   - XML path is recorded when present.
   - Warning is written when XML is absent.
   - Missing DLL raises clear error.
   - Dependency DLL paths are collected.

**Outputs:**
- `src/plugin_examples/nupkg_extractor/extractor.py`
- `src/plugin_examples/nupkg_extractor/framework_selector.py`
- `workspace/runs/{run_id}/extracted/{family}/primary/`
- `workspace/runs/{run_id}/extracted/{family}/deps/`
- `workspace/runs/{run_id}/extracted/{family}/resolved-libs/`
- `workspace/runs/{run_id}/extracted/{family}/extraction-manifest.json`

**Acceptance Criteria:**
- `extraction-manifest.json` contains: `dll_path`, `xml_path` (or null), `selected_framework`, `framework_selection_reason`, `requires_windows_runner`, `dependency_dll_paths`.
- `netstandard2.0` is preferred over `net8.0` when both are present.
- `requires_windows_runner` is `true` when `net48` or other Windows-only TFM is selected.
- `tests/unit/test_nupkg_extractor.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_nupkg_extractor.py -v
cat runs/test-01/extracted/cells/extraction-manifest.json | python -m json.tool
```

**Failure Handling:**
- No matching framework → fail with explicit "no supported framework found" error listing available frameworks.

**Evidence Files:**
- `workspace/runs/{run_id}/extracted/{family}/extraction-manifest.json`

---

### EPIC-04: Reflection API Catalog

---

**Taskcard ID:** TC-05
**Title:** Build Reflection Catalog Generator with Metadata-Only DllReflector
**Objective:** Generate a canonical JSON API catalog from the extracted DLL and XML. The DllReflector tool must use metadata-only loading — it must never execute Aspose code, never instantiate Aspose types, and never trigger static constructors.

**Dependencies:** TC-04

**Inputs:**
- `dll_path` from `extraction-manifest.json` (TC-04)
- `xml_path` from `extraction-manifest.json` (TC-04, may be null)
- `dependency_dll_paths` from `extraction-manifest.json` (TC-04)

**Actions:**
1. Create `tools/DllReflector/DllReflector.csproj`:
   - SDK-style console project targeting `net8.0`.
   - Dependencies: `System.Reflection.Metadata`, `Mono.Cecil` (optional alternative), `Microsoft.Extensions.Logging`.
   - **No Aspose package references** — must load the DLL from a path argument.
2. Create `tools/DllReflector/Program.cs`:
   - Accept CLI args: `--dll <path>` `--xml <path>` `--deps <dep1.dll,dep2.dll,...>` `--output <path>`.
   - Use **`System.Reflection.MetadataLoadContext`** (preferred) or `Mono.Cecil` for metadata-only loading.
   - **Strict design rules:**
     - Do not load DLL into the runtime AppDomain.
     - Do not call `Assembly.Load()` or `Assembly.LoadFrom()`.
     - Do not use `Activator.CreateInstance()`.
     - Do not invoke any method on any loaded type.
     - Do not allow static constructors to execute.
     - Use `MetadataLoadContext` with a `PathAssemblyResolver` that includes the `dependency_dll_paths` and the .NET trusted platform assemblies.
   - Reflect: public namespaces, public types (class/struct/enum/interface), public constructors (signatures), public methods (name, signatures, return type), public properties (name, type), public enums and values, `[Obsolete]` markers, assembly version, target framework moniker.
   - Merge XML documentation summaries by `<member name="...">` matching.
   - Output JSON to `--output` path.
3. Create `src/plugin_examples/reflection_catalog/reflector.py`:
   - Build the `tools/DllReflector` project if not built (`dotnet build`).
   - Invoke `tools/DllReflector/bin/Release/net8.0/DllReflector` as a subprocess.
   - Pass DLL path, XML path, dependency DLL paths, and output path.
   - Capture stdout/stderr and exit code.
   - Fail explicitly if exit code != 0.
4. Create `src/plugin_examples/reflection_catalog/catalog_builder.py`:
   - Load reflector JSON output.
   - Build structured catalog with explicit namespace, type, and member records.
   - Validate against `pipeline/schemas/api-catalog.schema.json`.
   - Write to `workspace/manifests/api-catalogs/{family}/{version}.json`.
5. Create `src/plugin_examples/reflection_catalog/schema_validator.py`.
6. Create `pipeline/schemas/api-catalog.schema.json`.
7. Write `tests/unit/test_reflection_catalog.py`.

**Outputs:**
- `tools/DllReflector/DllReflector.csproj`
- `tools/DllReflector/Program.cs`
- `src/plugin_examples/reflection_catalog/`
- `pipeline/schemas/api-catalog.schema.json`
- `workspace/manifests/api-catalogs/{family}/{version}.json`

**Acceptance Criteria:**
- DllReflector uses `MetadataLoadContext` or `Mono.Cecil` — no `Assembly.Load()`.
- DllReflector resolves dependencies from `dependency_dll_paths` and trusted platform assemblies.
- No Aspose type is ever instantiated.
- Catalog for Aspose.Cells includes at least one public namespace.
- Catalog schema validates.
- `tests/unit/test_reflection_catalog.py` passes.

**Verification Commands:**
```bash
dotnet build tools/DllReflector/DllReflector.csproj -c Release
python -m pytest tests/unit/test_reflection_catalog.py -v
cat workspace/manifests/api-catalogs/cells/{version}.json | python -m json.tool | head -50
```

**Failure Handling:**
- If DLL cannot be loaded, fail with explicit error. Do not proceed to generation with empty catalog.
- If XML is missing, log warning and continue with signatures only.
- If a dependency DLL cannot be resolved by the MetadataLoadContext, log which dependency is missing — it may indicate a missing dep in `dependency-manifest.json`.

**Evidence Files:**
- `workspace/manifests/api-catalogs/{family}/{version}.json`

---

**Taskcard ID:** TC-06
**Title:** Build Plugin Namespace Detector and Source-of-Truth Proof Reporter
**Objective:** Detect eligible plugin namespaces from the reflection catalog. Produce a mandatory source-of-truth proof report. No scenario planning or generation may start until the proof report shows `eligibility_status: eligible`.

**Dependencies:** TC-05

**Inputs:**
- `workspace/manifests/api-catalogs/{family}/{version}.json`
- `plugin_detection.namespace_patterns` from family config
- `extraction-manifest.json` (for dll_path, xml_path, dependency counts, framework)
- `download-manifest.json` (for package_id, version, sha256)

**Actions:**
1. Create `src/plugin_examples/plugin_detector/detector.py`:
   - Load catalog namespaces.
   - Match against `namespace_patterns` (support glob-style `*` suffix).
   - Record matched namespaces with evidence (catalog path, catalog version).
   - Record non-matched patterns with reason.
   - Write `workspace/manifests/product-inventory.json`.
2. Create `src/plugin_examples/plugin_detector/proof_reporter.py`:
   - Collect all required source-of-truth evidence from prior manifests.
   - Write `workspace/verification/latest/{family}-source-of-truth-proof.json` with exactly this structure:

   ```json
   {
     "package_id": "Aspose.Cells",
     "resolved_version": "24.x.x",
     "nupkg_sha256": "...",
     "selected_target_framework": "netstandard2.0",
     "dll_path": "runs/.../Aspose.Cells.dll",
     "xml_path": "runs/.../Aspose.Cells.xml",
     "xml_warning": null,
     "dependency_count": 3,
     "dependency_paths": ["..."],
     "api_catalog_path": "manifests/api-catalogs/cells/24.x.x.json",
     "namespace_count": 42,
     "matched_plugin_namespaces": ["Aspose.Cells.LowCode"],
     "public_plugin_type_count": 12,
     "public_plugin_method_count": 47,
     "eligibility_status": "eligible",
     "eligibility_reason": "Matched namespace: Aspose.Cells.LowCode"
   }
   ```

   - If no plugin namespaces matched: set `eligibility_status: "not_eligible"` with reason.
   - The pipeline must check this file before proceeding to TC-07 through TC-13.
3. Add gate enforcement in the main pipeline orchestrator:
   - After TC-06, read `workspace/verification/latest/{family}-source-of-truth-proof.json`.
   - If `eligibility_status != "eligible"`, halt pipeline for that family. Log clearly. Do not proceed to scenario planning.
4. Write `tests/unit/test_plugin_detector.py`.

**Outputs:**
- `src/plugin_examples/plugin_detector/detector.py`
- `src/plugin_examples/plugin_detector/proof_reporter.py`
- `workspace/manifests/product-inventory.json`
- `workspace/verification/latest/cells-source-of-truth-proof.json`

**Acceptance Criteria:**
- `cells-source-of-truth-proof.json` contains all required fields.
- `eligibility_status` is `eligible` when `Aspose.Cells.LowCode` is in the reflected catalog.
- `eligibility_status` is `not_eligible` when no pattern matches — pipeline halts cleanly.
- `public_plugin_type_count` and `public_plugin_method_count` reflect only the matched plugin namespaces.
- Pipeline cannot proceed to TC-07+ without this file having `eligibility_status: eligible`.
- `tests/unit/test_plugin_detector.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_plugin_detector.py -v
cat workspace/verification/latest/cells-source-of-truth-proof.json | python -m json.tool
# Expected: eligibility_status = "eligible"
```

**Failure Handling:**
- If catalog is empty, fail with explicit error.
- If `eligibility_status: not_eligible`, write proof report and halt — do not continue to generation.

**Evidence Files:**
- `workspace/verification/latest/cells-source-of-truth-proof.json`
- `workspace/manifests/product-inventory.json`

---

### EPIC-05: API Delta and Monthly Change Model

---

**Taskcard ID:** TC-07
**Title:** Build API Delta Engine

**Dependencies:** TC-05, TC-06 (proof report must be eligible)

**Inputs:**
- `workspace/manifests/api-catalogs/{family}/{version}.json` (current)
- `workspace/manifests/api-catalogs/{family}/{previous_version}.json` (previous, if exists)
- `workspace/manifests/example-index.json`

**Actions:**
1. Create `src/plugin_examples/api_delta/delta_engine.py`:
   - Compare namespaces, types, methods, properties, signatures.
   - Classify each symbol as: `added`, `removed`, `changed`, `unchanged`.
   - Detect signature changes (param count, param type, return type).
   - Detect obsolete additions.
2. Create `src/plugin_examples/api_delta/impact_mapper.py`:
   - Load example manifests.
   - Map impacted symbols to examples that claim them.
   - Mark examples as: `needs_regeneration`, `needs_repair`, `unaffected`.
3. Write delta report to `workspace/verification/latest/api-delta-report.json`.
4. Write impact report to `workspace/verification/latest/example-impact-report.json`.
5. Write `tests/unit/test_api_delta.py`.

**Outputs:**
- `src/plugin_examples/api_delta/`
- `workspace/verification/latest/api-delta-report.json`
- `workspace/verification/latest/example-impact-report.json`

**Acceptance Criteria:**
- Added/removed/changed symbols are classified correctly.
- Impacted examples are identified.
- Unchanged examples are not flagged.
- On first run, all symbols are `added`.
- `tests/unit/test_api_delta.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_api_delta.py -v
cat workspace/verification/latest/api-delta-report.json | python -m json.tool
```

**Failure Handling:**
- Missing previous catalog → treat as initial run. Log as "initial run, full catalog".

**Evidence Files:**
- `workspace/verification/latest/api-delta-report.json`
- `workspace/verification/latest/example-impact-report.json`

---

### EPIC-06: Fixture and Existing Example Registry

---

**Taskcard ID:** TC-08
**Title:** Build Fixture Registry

**Dependencies:** TC-02

**Inputs:**
- `fixtures.sources` from family config
- GitHub API

**Actions:**
1. Create `src/plugin_examples/fixture_registry/registry.py`.
2. Create `src/plugin_examples/fixture_registry/fixture_fetcher.py`.
3. Write `workspace/manifests/fixture-registry.json`.
4. Write `tests/unit/test_fixture_registry.py`.

**Outputs:**
- `src/plugin_examples/fixture_registry/`
- `workspace/manifests/fixture-registry.json`
- `workspace/runs/{run_id}/fixtures/{family}/`

**Acceptance Criteria:**
- Registry includes at least one `.xlsx` for Cells pilot.
- Every fixture has provenance.
- Missing-fixture scenarios are blocked with reason.
- Tests pass.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_fixture_registry.py -v
cat workspace/manifests/fixture-registry.json | python -m json.tool | head -30
```

**Failure Handling:**
- GitHub API rate-limited → fail with clear message.
- No suitable fixture → block affected scenarios with reason.

**Evidence Files:**
- `workspace/manifests/fixture-registry.json`

---

**Taskcard ID:** TC-09
**Title:** Mine Existing Examples

**Dependencies:** TC-05, TC-08

**Inputs:**
- `existing_examples.sources` from family config
- `workspace/manifests/api-catalogs/{family}/{version}.json`

**Actions:**
1. Create `src/plugin_examples/example_miner/miner.py`.
2. Create `src/plugin_examples/example_miner/symbol_validator.py`.
3. Write `workspace/manifests/existing-examples-index.json`.
4. Write `workspace/verification/latest/stale-existing-examples.json`.
5. Write `tests/unit/test_example_miner.py`.

**Outputs:**
- `src/plugin_examples/example_miner/`
- `workspace/manifests/existing-examples-index.json`
- `workspace/verification/latest/stale-existing-examples.json`

**Acceptance Criteria:**
- All mined examples have classification (`reusable`, `stale`, `irrelevant`).
- Stale examples list their missing/changed symbols.
- No example trusted without symbol validation.
- Tests pass.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_example_miner.py -v
cat workspace/manifests/existing-examples-index.json | python -m json.tool | head -30
```

**Failure Handling:**
- Official examples repo unavailable → log warning, continue with empty mined set.

**Evidence Files:**
- `workspace/manifests/existing-examples-index.json`
- `workspace/verification/latest/stale-existing-examples.json`

---

### EPIC-07: Scenario Planning

---

**Taskcard ID:** TC-10
**Title:** Build Scenario Catalog
**Objective:** Create generation candidates from reflected plugin APIs and confirmed fixtures. Every scenario must have verified symbols, a fixture strategy, and an expected output plan before entering generation. Unclear API semantics must block the scenario, not guess it.

**Dependencies:** TC-06 (proof report must be eligible), TC-07, TC-08, TC-09

**Pre-condition (hard gate):**
- `workspace/verification/latest/{family}-source-of-truth-proof.json` must exist.
- `eligibility_status` must equal `"eligible"`.
- If this file is missing or status is not `eligible`, TC-10 must not run.

**Inputs:**
- `workspace/manifests/api-catalogs/{family}/{version}.json`
- `workspace/manifests/fixture-registry.json`
- `workspace/manifests/existing-examples-index.json`
- `workspace/verification/latest/{family}-source-of-truth-proof.json`

**Actions:**
1. Create `src/plugin_examples/scenario_planner/planner.py`:
   - Load the source-of-truth proof — fail immediately if not eligible.
   - Identify plugin API entrypoints (top-level LowCode/Plugin static methods or factory classes) from the **reflected catalog only** — not from class name pattern matching or documentation text.
   - Use reflected XML doc summaries and reusable existing examples as supplemental input to understand parameter semantics.
   - Group by input format + output format + transformation type.
   - For each group, create scenario candidates with: `required_symbols`, fixture candidate, expected output format, expected output checks.
   - Assign status:
     - `ready`: all required info is present, symbols verified, fixture identified, output format clear.
     - `blocked_no_fixture`: scenario is valid but no registered fixture matches the required input format.
     - `blocked_unclear_semantics`: API surface identified but parameter behavior or required input structure is ambiguous. **Do not let the LLM invent intent from class names alone.**
     - `blocked_missing_symbol`: scenario references a symbol not in the API catalog.
     - `blocked_other`: explicit reason required.
   - **All blocked scenarios must persist in `workspace/verification/latest/blocked-scenarios.json`. They must never be silently dropped.**
2. Create `src/plugin_examples/scenario_planner/scenario_catalog.py`:
   - Write `workspace/manifests/scenario-catalog.json`.
   - Write `workspace/verification/latest/blocked-scenarios.json`.
3. Create `pipeline/schemas/scenario.schema.json`.
4. Write `tests/unit/test_scenario_planner.py`.

**Outputs:**
- `src/plugin_examples/scenario_planner/`
- `pipeline/schemas/scenario.schema.json`
- `workspace/manifests/scenario-catalog.json`
- `workspace/verification/latest/blocked-scenarios.json`

**Acceptance Criteria:**
- Planner halts cleanly if source-of-truth proof is missing or not eligible.
- For Cells pilot: at least 3 `ready` scenarios if LowCode API is present.
- Every `ready` scenario has: `scenario_id`, `family`, `namespace`, `entrypoint`, `required_symbols`, `fixture_path`, `expected_output_format`, `expected_output_checks`, `validation_plan`.
- Every `blocked` scenario has explicit `block_reason` from the allowed statuses.
- No scenario uses symbols absent from the API catalog.
- `blocked_unclear_semantics` is used when method purpose cannot be determined from signatures and XML docs alone.
- `tests/unit/test_scenario_planner.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_scenario_planner.py -v
cat workspace/manifests/scenario-catalog.json | python -m json.tool | head -50
cat workspace/verification/latest/blocked-scenarios.json | python -m json.tool
```

**Failure Handling:**
- If fewer than `min_examples_per_family` ready scenarios exist, write blocked report and halt generation. Report to human.
- If source-of-truth proof is missing, write explicit error and halt — do not generate.

**Evidence Files:**
- `workspace/manifests/scenario-catalog.json`
- `workspace/verification/latest/blocked-scenarios.json`

---

### EPIC-08: LLM Generation

---

**Taskcard ID:** TC-11
**Title:** Build LLM Router with Preflight

**Dependencies:** TC-02

**Inputs:**
- `configs/llm-routing.yml`

**Actions:**
1. Create `src/plugin_examples/llm_router/router.py`.
2. Create `src/plugin_examples/llm_router/preflight.py`.
3. Create `src/plugin_examples/llm_router/providers/professionalize.py` (OpenAI-compatible, uses `LLM_PROFESSIONALIZE_API_KEY` env var).
4. Create `src/plugin_examples/llm_router/providers/ollama.py` (uses `OLLAMA_HOST` env var, default `http://localhost:11434`).
5. Write `workspace/verification/latest/llm-preflight.json` after each preflight run.
6. Write `tests/unit/test_llm_router.py`.

**Preflight checks (per provider):**
- endpoint_reachable
- model_available
- json_response
- structured_response_parseable
- timeout_within_limit

**Outputs:**
- `src/plugin_examples/llm_router/`
- `workspace/verification/latest/llm-preflight.json`

**Acceptance Criteria:**
- Router never calls a provider that failed preflight.
- All-provider failure → fail closed with explicit error.
- Provider choice is recorded.
- Tests pass (mocked providers).

**Verification Commands:**
```bash
python -m pytest tests/unit/test_llm_router.py -v
cat workspace/verification/latest/llm-preflight.json | python -m json.tool
```

**Failure Handling:**
- All providers fail → write llm-preflight.json with failure reasons and halt.

**Evidence Files:**
- `workspace/verification/latest/llm-preflight.json`

---

**Taskcard ID:** TC-12
**Title:** Build Constrained Prompt Packet Builder

**Dependencies:** TC-10, TC-11

**Inputs:**
- Ready scenarios from `workspace/manifests/scenario-catalog.json`
- `workspace/manifests/api-catalogs/{family}/{version}.json`
- Reusable existing examples (from TC-09)
- `workspace/manifests/fixture-registry.json`

**Actions:**
1. Create `src/plugin_examples/generator/packet_builder.py`:
   - Build scenario packet from: scenario metadata, `allowed_symbols` (from catalog only), fixture metadata, style_hints (reusable existing examples only), output requirements, forbidden behaviors.
   - Forbidden behaviors in packet:
     - Do not use any namespace not in `allowed_symbols`.
     - Do not use any method not in `allowed_symbols`.
     - Do not invent overloads.
     - Do not use hardcoded absolute paths.
     - Do not include `// TODO` or `throw new NotImplementedException()`.
     - Do not use `Console.ReadLine()`.
     - Do not reference package versions inline in `.csproj`.
   - Required structured output fields: `program_cs`, `csproj`, `readme`, `manifest`, `expected_output`, `claimed_symbols`.
2. Create `pipeline/schemas/scenario-packet.schema.json`.
3. Create `pipeline/schemas/example-manifest.schema.json`.
4. Write `pipeline/prompts/example-generator.md`.
5. Write `pipeline/prompts/example-repair.md`.
6. Write `tests/unit/test_packet_builder.py`.

**Outputs:**
- `src/plugin_examples/generator/packet_builder.py`
- `pipeline/schemas/scenario-packet.schema.json`
- `pipeline/schemas/example-manifest.schema.json`
- `pipeline/prompts/example-generator.md`
- `pipeline/prompts/example-repair.md`

**Acceptance Criteria:**
- Packet only contains symbols present in API catalog.
- Unknown symbol → packet rejected before LLM call.
- Required output schema enforces `claimed_symbols`.
- Tests pass.

**Failure Handling:**
- Symbol not in catalog → block scenario, do not retry.

**Evidence Files:**
- `pipeline/schemas/scenario-packet.schema.json`
- `pipeline/schemas/example-manifest.schema.json`

---

**Taskcard ID:** TC-13
**Title:** Generate SDK-Style Console Example Projects

**Dependencies:** TC-12

**Generated File Governance:**
The generator may only write to these directories:
- `workspace/runs/{run_id}/generated/`
- `workspace/runs/{run_id}/validation/`
- `workspace/verification/latest/`
- `workspace/manifests/`

The generator must never write directly to the published examples repo or any other directory. Writing to the published repo happens only through the publisher (TC-16) after all gates pass.

**Actions:**
1. Create `src/plugin_examples/generator/code_generator.py`:
   - Send packet to LLM router.
   - Validate response schema.
   - Reject if any `claimed_symbol` not in API catalog.
   - Reject if `program_cs` contains placeholder patterns.
   - Reject if `program_cs` contains hardcoded absolute paths.
   - Reject if `.csproj` contains inline package versions.
2. Create `src/plugin_examples/generator/project_generator.py`:
   - Write to `workspace/runs/{run_id}/generated/{family}/{namespace-group}/{scenario-slug}/` only.
   - Generate: `.csproj`, `Program.cs`, `README.md`, `example.manifest.json`, `expected-output.json`.
3. Create `src/plugin_examples/generator/manifest_writer.py`:
   - Maintain `workspace/manifests/example-index.json`.
4. Write `tests/unit/test_generator.py`.

**Outputs:**
- `src/plugin_examples/generator/`
- `workspace/runs/{run_id}/generated/{family}/{namespace-group}/{scenario-slug}/`
- Updated `workspace/manifests/example-index.json`

**Acceptance Criteria:**
- `Program.cs` uses `AppContext.BaseDirectory`.
- `Program.cs` checks output file exists and is non-empty.
- No placeholder code.
- All `claimed_symbols` in API catalog.
- `.csproj` uses no inline package versions.
- Generator writes only to approved directories.
- Tests pass.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_generator.py -v
ls runs/test-01/generated/cells/lowcode/
cat runs/test-01/generated/cells/lowcode/convert-xlsx-to-pdf/Program.cs
```

**Failure Handling:**
- LLM output fails schema validation → retry once with `pipeline/prompts/example-repair.md`. Second failure → block scenario with reason.
- Claimed symbol not in catalog → block immediately, no retry.

**Evidence Files:**
- `workspace/runs/{run_id}/generated/{family}/{namespace-group}/{scenario-slug}/example.manifest.json`
- `workspace/manifests/example-index.json`

---

### EPIC-09: Validation and Reviewer Integration

---

**Taskcard ID:** TC-14
**Title:** Build Local Validation Harness

**Dependencies:** TC-13

**Inputs:**
- Generated example projects from TC-13
- `expected-output.json` per example
- `requires_windows_runner` from `extraction-manifest.json`

**Actions:**
1. Create `src/plugin_examples/verifier_bridge/dotnet_runner.py`:
   - For each generated example: run restore → build → run.
   - Route to Windows runner if `requires_windows_runner: true`.
   - Record: exit code, stdout, stderr, runtime duration.
   - Write `workspace/runs/{run_id}/validation/{scenario-slug}/dotnet-result.json`.
2. Create `src/plugin_examples/verifier_bridge/output_validator.py`:
   - Check expected output file exists and is non-empty.
   - Check extension matches expected format.
   - Optional: format-specific reopen check.
   - Write `workspace/runs/{run_id}/validation/{scenario-slug}/output-validation.json`.
3. Create `pipeline/schemas/validation-result.schema.json`.
4. Aggregate to `workspace/verification/latest/validation-results.json`.
5. Write `tests/integration/test_cells_pipeline.py` for end-to-end test.

**Outputs:**
- `src/plugin_examples/verifier_bridge/dotnet_runner.py`
- `src/plugin_examples/verifier_bridge/output_validator.py`
- `pipeline/schemas/validation-result.schema.json`
- `workspace/runs/{run_id}/validation/{scenario-slug}/dotnet-result.json`
- `workspace/runs/{run_id}/validation/{scenario-slug}/output-validation.json`
- `workspace/verification/latest/validation-results.json`

**Acceptance Criteria:**
- Every accepted example: restore exit 0, build exit 0, run exit 0.
- Every accepted example: expected output exists and is non-empty.
- Failed examples are not promoted — marked for repair.
- Integration test passes against real Aspose.Cells.

**Verification Commands:**
```bash
dotnet restore runs/test-01/generated/cells/lowcode/convert-xlsx-to-pdf/ConvertXlsxToPdf.csproj
dotnet build --no-restore runs/test-01/generated/cells/lowcode/convert-xlsx-to-pdf/ConvertXlsxToPdf.csproj
dotnet run --project runs/test-01/generated/cells/lowcode/convert-xlsx-to-pdf/ConvertXlsxToPdf.csproj
python -m pytest tests/integration/test_cells_pipeline.py -v
```

**Failure Handling:**
- Restore failure → record, skip build/run, mark for repair.
- Build failure → attempt one LLM repair. Second failure → blocked.
- Run failure → same repair loop.
- Output validation failure → blocked with reason.

**Evidence Files:**
- `workspace/verification/latest/validation-results.json`

---

**Taskcard ID:** TC-15
**Title:** Integrate example-reviewer as Publishing Gate

**Dependencies:** TC-14, TC-00X (integration surface must be documented)

**Pre-condition:** `docs/discovery/example-reviewer-integration-surface.md` must exist and contain a recommended integration mode before this taskcard begins.

**Inputs:**
- Validated examples (passed TC-14)
- `docs/discovery/example-reviewer-integration-surface.md`
- Family config
- `workspace/manifests/api-catalogs/{family}/{version}.json`

**Actions:**
1. Read `docs/discovery/example-reviewer-integration-surface.md`.
2. Implement integration using the recommended mode (prefer CLI subprocess for isolation).
3. Create `src/plugin_examples/verifier_bridge/bridge.py`.
4. Write `workspace/verification/latest/example-reviewer-results.json`.
5. Block PR creation if any example fails reviewer gate.
6. Write `docs/verifier-integration.md`.

**Outputs:**
- `src/plugin_examples/verifier_bridge/bridge.py`
- `docs/verifier-integration.md`
- `workspace/verification/latest/example-reviewer-results.json`

**Acceptance Criteria:**
- Every published example has a reviewer result entry.
- Reviewer pass is required — failure blocks PR.
- Reviewer errors produce actionable failure messages.

**Failure Handling:**
- Reviewer unreachable or crashes → fail gate. Do not skip.
- Ambiguous result → treat as failure.

**Evidence Files:**
- `docs/verifier-integration.md`
- `workspace/verification/latest/example-reviewer-results.json`

---

### EPIC-10: Publishing

---

**Taskcard ID:** TC-16
**Title:** Build GitHub Publisher

**Dependencies:** TC-15

**Actions:**
1. Create `src/plugin_examples/publisher/publisher.py`:
   - Create branch `pipeline/{run_id}/{family}`.
   - Commit generated examples, manifests, verification evidence.
   - Open PR against `main`.
   - **Never push directly to `main`.**
   - Implement `--dry-run` mode: write PR content to `workspace/runs/{run_id}/pr-preview/`.
2. Create `src/plugin_examples/publisher/pr_builder.py`.
3. Write `workspace/verification/latest/publishing-report.json`.
4. Write `tests/unit/test_publisher.py` (GitHub API mocked).

**Outputs:**
- `src/plugin_examples/publisher/`
- GitHub PR (live) or `workspace/runs/{run_id}/pr-preview/` (dry-run)
- `workspace/verification/latest/publishing-report.json`

**Acceptance Criteria:**
- PR branch follows naming convention.
- PR body includes gate evidence checklist.
- No direct `main` push is possible through this module.
- `--dry-run` works without `GITHUB_TOKEN`.
- Tests pass (mocked).

**Verification Commands:**
```bash
python -m pytest tests/unit/test_publisher.py -v
python -m plugin_examples publish --family cells --run-id test-01 --dry-run
ls runs/test-01/pr-preview/
```

**Failure Handling:**
- `GITHUB_TOKEN` missing → fail with "credentials required". Suggest `--dry-run`.
- PR already exists → update, not duplicate.

**Evidence Files:**
- `workspace/verification/latest/publishing-report.json`

---

### EPIC-11: Autonomous Monthly Runner

---

**Taskcard ID:** TC-17
**Title:** Implement Monthly Scheduled Pipeline Workflow

**Dependencies:** TC-02 through TC-16 (all)

**Actions:**
1. Create `src/plugin_examples/package_watcher/watcher.py`:
   - Skip disabled families.
   - Check NuGet version vs `workspace/manifests/package-lock.json`.
2. Create `src/plugin_examples/__main__.py` with flags: `--family`, `--run-id`, `--dry-run`, `--skip-llm`, `--force-full`.
3. Create `.github/workflows/monthly-package-refresh.yml` (schedule: 1st of month, 06:00 UTC).
4. Create `.github/workflows/build-and-test.yml`.
5. Write `docs/monthly-runbook.md`.

**Outputs:**
- `src/plugin_examples/__main__.py`
- `src/plugin_examples/package_watcher/`
- `.github/workflows/monthly-package-refresh.yml`
- `.github/workflows/build-and-test.yml`
- `docs/monthly-runbook.md`
- `workspace/verification/latest/monthly-run-report.json`

**Acceptance Criteria:**
- Disabled families are never processed.
- No package change → exit 0, no PR.
- Changed families → delta pipeline.
- Passing run opens PR.

**Evidence Files:**
- `workspace/verification/latest/monthly-run-report.json`

---

## 12. Verification Gates

| Gate | Name | Pass Condition | Failure Action |
|---|---|---|---|
| Gate 0 | Concurrency and Ownership Safety | Run record exists, overlap classification is `no_overlap` or `adjacent_overlap` with rationale, no `direct_overlap` or `unknown_ownership` | STOP all work. Do not write files. Report overlap to human. |
| Gate 1 | NuGet Package Retrieval | `.nupkg` downloaded, hash recorded, no pre-release if disallowed | Halt, report error |
| Gate 1b | Dependency Resolution | `dependency-manifest.json` written with all direct deps | Log warning if some deps missing; halt if DllReflector fails as a result |
| Gate 2 | `.nupkg` Extraction | `lib/` folder found and extracted | Halt, list available frameworks |
| Gate 3 | DLL + XML Discovery | DLL found; XML found or warning written | Halt on missing DLL; warn on missing XML |
| Gate 4 | Reflection Catalog Generation | Catalog JSON written, schema-validates, no code executed | Halt, log catalog error |
| Gate 5 | Plugin Namespace Detection | At least one configured namespace matched in reflected catalog | Mark not_eligible in proof report; halt |
| Gate 5b | Source-of-Truth Proof | `{family}-source-of-truth-proof.json` exists with `eligibility_status: eligible` | Halt all downstream stages; never proceed to generation |
| Gate 6 | API Delta Calculation | Delta report and impact map written | Halt, log delta error |
| Gate 7 | Fixture Registry Validation | At least one suitable fixture per expected format | Block affected scenarios with reason |
| Gate 8 | Scenario Validity | Scenario has symbols (from catalog), fixture, output plan; unclear semantics → blocked_unclear_semantics | Block scenario, record reason |
| Gate 9 | LLM Provider Preflight | At least one provider passes all preflight checks | Fail closed, log provider failures |
| Gate 10 | LLM Output Schema Validation | Response includes all required fields | Retry once with repair prompt, then block |
| Gate 11 | Unknown Symbol Rejection | All `claimed_symbols` present in API catalog | Block immediately, no retry |
| Gate 12 | `dotnet restore` | Exit code 0 | Mark for repair |
| Gate 13 | `dotnet build` | Exit code 0 | One LLM repair attempt; second failure → blocked |
| Gate 14 | `dotnet run` | Exit code 0 | One LLM repair attempt; second failure → blocked |
| Gate 15 | Output Validation | Expected output exists and is non-empty | Block, record failure |
| Gate 16 | example-reviewer Validation | Reviewer returns pass verdict | Block, preserve reviewer output |
| Gate 17 | PR Evidence Package | All evidence JSON files present | Block PR creation |
| Gate 18 | No Direct Push to Main | PR is branch-based; no direct main push | Hard block in publisher code |

---

## 13. Pilot Strategy

**Pilot product:** Aspose.Cells for .NET (`Aspose.Cells` NuGet package)

**Pilot success criteria:**

| # | Criterion | Verified By |
|---|---|---|
| 1 | Family config created with `enabled: true` | `cells.yml` validates against schema |
| 2 | Latest Aspose.Cells NuGet resolved (no pre-release) | `download-manifest.json` has semver version |
| 3 | Package downloaded and hashed | `.nupkg` at expected path, SHA-256 recorded |
| 4 | Dependency packages resolved and extracted | `dependency-manifest.json` present |
| 5 | DLL + XML extracted | `extraction-manifest.json` has `dll_path` |
| 6 | Framework selected with Windows runner flag if net48 | `selected_framework` in manifest |
| 7 | DllReflector used MetadataLoadContext (no code execution) | Code review + test coverage |
| 8 | Reflection catalog generated | `workspace/manifests/api-catalogs/cells/{version}.json` present |
| 9 | Plugin namespace detected from reflected DLL | `product-inventory.json` marks cells eligible |
| 10 | Source-of-truth proof produced with `eligibility_status: eligible` | `cells-source-of-truth-proof.json` present |
| 11 | Existing examples indexed | `existing-examples-index.json` present |
| 12 | Fixtures indexed (at least one .xlsx) | `fixture-registry.json` has .xlsx entry |
| 13 | At least 3 ready scenarios planned | `scenario-catalog.json` has 3 ready entries |
| 14 | Blocked scenarios documented | `blocked-scenarios.json` present |
| 15 | At least 3 examples generated (in workspace/runs/ only) | 3 folders in `workspace/runs/{id}/generated/cells/lowcode/` |
| 16 | All generated examples restore | All restore exit codes = 0 |
| 17 | All generated examples build | All build exit codes = 0 |
| 18 | At least 2 examples run with fixtures | At least 2 run exit codes = 0 |
| 19 | Outputs validated | At least 2 expected outputs present and non-empty |
| 20 | example-reviewer gate passes | `example-reviewer-results.json` has pass verdicts |
| 21 | PR-ready evidence produced | All `workspace/verification/latest/` JSON files present |

---

## 14. Monthly Automation Model

```
1st of each month, 06:00 UTC
  │
  ▼
package_watcher: skip disabled families
  │
  ├─ No enabled families → exit 0
  │
  └─ Enabled families →
        check NuGet version vs package-lock.json
          │
          ├─ No version change → exit 0 (no PR)
          │
          └─ Version changed →
                nuget_fetcher → dependency_resolver → nupkg_extractor → reflection_catalog
                  │
                  plugin_detector → source-of-truth proof
                    │
                    ├─ not_eligible → write proof, halt for this family
                    │
                    └─ eligible →
                          api_delta → fixture_registry → example_miner → scenario_planner
                            │
                            llm_router preflight
                              │
                              generator (runs/only, delta-based)
                                │
                                dotnet restore → build → run → output validation
                                  │
                                  example-reviewer gate
                                    │
                                    ├─ All pass → publisher → GitHub PR
                                    │
                                    └─ Some fail → blocked-scenarios + failure report
                                                   (no partial PR)
```

---

## 15. example-reviewer Integration Model

`example-reviewer` is at `https://github.com/babar-raza/example-reviewer` (same owner).

**Known capabilities (from plan context):** compile, runtime execution, LLM service, API catalog lookup, fixture resolution, SQLite-backed state, Verify → Fix → Verify loop.

**Integration approach:**
1. TC-00X discovers actual integration surface before TC-15 begins.
2. Priority order: CLI subprocess > Python module > HTTP API.
3. `docs/discovery/example-reviewer-integration-surface.md` is the binding reference for TC-15 implementation.

**Rule:** Do not duplicate compilation, runtime, or LLM fix logic from `example-reviewer`. Integrate.

---

## 16. LLM Routing Model

```yaml
providers:
  llm_professionalize:
    type: openai_compatible
    base_url: https://llm.professionalize.com/v1
    api_key_env: LLM_PROFESSIONALIZE_API_KEY
    timeout_seconds: 60

  ollama:
    type: ollama
    host_env: OLLAMA_HOST
    default_host: http://localhost:11434
    timeout_seconds: 120

task_provider_order:
  scenario_planning: [llm_professionalize, ollama]
  code_generation: [llm_professionalize, ollama]
  code_repair: [llm_professionalize, ollama]
  semantic_review: [llm_professionalize, ollama]

preflight:
  required: true
  fail_closed: true
```

**LLM constraints (enforced in packet builder code, not in prompts alone):**
- Packet contains only symbols from the reflected API catalog.
- LLM output is schema-validated before any files are written.
- All `claimed_symbols` cross-checked against catalog after generation.
- Rejection is in pipeline code — not in prompt instruction alone.

---

## 17. CI Model

### `build-and-test.yml` (this repo)

Triggers: push to any branch, PR to main.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '8.0.x' }
      - run: pip install -e ".[dev]"
      - run: python -m pytest tests/unit/ -v
      - run: python -m pytest tests/integration/ -v --timeout=300
```

### `monthly-package-refresh.yml` (this repo)

Triggers: schedule (1st of month), workflow_dispatch.

```yaml
jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '8.0.x' }
      - run: pip install -e "."
      - run: python -m plugin_examples --all-families
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          LLM_PROFESSIONALIZE_API_KEY: ${{ secrets.LLM_PROFESSIONALIZE_API_KEY }}
          OLLAMA_HOST: ${{ vars.OLLAMA_HOST }}
      - uses: actions/upload-artifact@v4
        with:
          name: pipeline-evidence
          path: workspace/verification/latest/
```

**Note on Windows runner:** If any family selects a Windows-only TFM (`net48`), the monthly workflow must include a matrix job routing `dotnet run` to `windows-latest`.

---

## 18. Risks and Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Aspose.Cells.LowCode not in shipped NuGet | Medium | High | Check at Gate 5b; write proof report; halt cleanly |
| R2 | XML documentation missing from NuGet | Medium | Medium | Log warning at Gate 3; proceed with signatures only |
| R3 | `llm.professionalize.com` unreachable | Medium | High | Ollama fallback; fail closed if both unavailable |
| R4 | LLM generates invented symbols | High | High | Gate 11 hard-rejects; packet builder pre-filters |
| R5 | Generated example fails `dotnet build` | High | Medium | One LLM repair attempt; block on second failure |
| R6 | Fixture files unavailable | Medium | Medium | Block affected scenarios; proceed with independent ones |
| R7 | `example-reviewer` integration mode unknown | Medium | Medium | TC-00X resolves this before TC-15 |
| R8 | DllReflector triggers Aspose static constructors | Low | High | Enforced MetadataLoadContext design; code review gate |
| R9 | Dependency DLLs missing causes MetadataLoadContext failure | Medium | High | TC-03 dependency_resolver ensures deps are fetched |
| R10 | Only `net48` available → Windows runner required | Medium | Medium | Framework selector sets `requires_windows_runner: true`; CI matrix handles it |
| R11 | `aspose-plugins-examples-dotnet` repo does not exist | Low | High | Publisher creates it or guides human |
| R12 | Words/PDF configs accidentally processed | Low | High | loader.py enforces `enabled` and path checks |
| R13 | Scenario planner invents intent from class names | Medium | High | Gate 8 `blocked_unclear_semantics` status enforced |

---

## 19. Execution Order

### Wave 0A — Concurrency Preflight (MANDATORY before any work)

```
TC-00A: Create run record
  - git status, git log, git stash list, git branch -a, git worktree list
  - Check for lock files and existing run records
  - Classify overlap: no_overlap / adjacent / direct / unknown
  - Write workspace/runs/{run_id}/run-record.json
  - STOP if direct_overlap or unknown_ownership
→ Gate 0 must pass before proceeding
```

### Wave 0B — Repository Structure Migration

```
TC-00D: Structure migration
  - Create .gitignore
  - Create pipeline/ directory (move configs/, schemas/, prompts/)
  - Create workspace/ directory (move runs/, manifests/, verification/)
  - Verify no files lost
  - Run midflight check (TC-00B)
→ Verify: all files accounted for in new paths
→ Verify: git status shows expected renames/moves only
```

### Wave 0C — Compatibility Update

```
TC-00E: Path compatibility
  - Update all path references in plan, AGENTS.md, docs
  - Verify no broken references
  - Run pre-commit scope verification (TC-00C)
→ Verify: grep finds no orphaned old-structure paths in source files
```

### Wave 1A — Project Foundation

```
pyproject.toml (Python 3.12, deps: jsonschema, pyyaml, requests, pytest)
src/plugin_examples/__init__.py (empty)
src/plugin_examples/family_config/ (all four files)
pipeline/schemas/family-config.schema.json
pipeline/configs/families/cells.yml (enabled: true)
pipeline/configs/families/disabled/words.yml (enabled: false)
pipeline/configs/families/disabled/pdf.yml (enabled: false)
pipeline/configs/families/_templates/family-template.yml
tests/unit/test_family_config.py
→ TC-00B midflight check before first write
→ Verify: python -m pytest tests/unit/test_family_config.py -v (must pass)
→ TC-00C pre-commit scope verification
```

### Wave 1B — NuGet Fetch and Cache

```
src/plugin_examples/nuget_fetcher/fetcher.py
src/plugin_examples/nuget_fetcher/cache.py
tests/unit/test_nuget_fetcher.py (mocked HTTP)
→ Verify: tests pass
→ Dry-run: fetch Aspose.Cells, confirm workspace/runs/{id}/packages/cells/download-manifest.json
```

### Wave 1C — Dependency Resolution and Extraction

```
src/plugin_examples/nuget_fetcher/dependency_resolver.py
src/plugin_examples/nupkg_extractor/extractor.py
src/plugin_examples/nupkg_extractor/framework_selector.py
tests/unit/test_dependency_resolver.py
tests/unit/test_nupkg_extractor.py
→ Verify: tests pass
→ Dry-run: extract Aspose.Cells, confirm extraction-manifest.json
  - selected_framework must be netstandard2.0 or netstandard2.1
  - dependency_dll_paths must be populated
```

### Wave 1D — DllReflector and Catalog

```
tools/DllReflector/DllReflector.csproj (MetadataLoadContext, no Aspose refs)
tools/DllReflector/Program.cs
pipeline/schemas/api-catalog.schema.json
src/plugin_examples/reflection_catalog/reflector.py
src/plugin_examples/reflection_catalog/catalog_builder.py
src/plugin_examples/reflection_catalog/schema_validator.py
tests/unit/test_reflection_catalog.py
→ Verify: dotnet build tools/DllReflector/ succeeds
→ Verify: tests pass
→ Dry-run: generate catalog for Aspose.Cells
  - Catalog must include at least one namespace
  - Catalog must validate against schema
```

### Wave 1E — Plugin Detection and Source-of-Truth Proof

```
src/plugin_examples/plugin_detector/detector.py
src/plugin_examples/plugin_detector/proof_reporter.py
tests/unit/test_plugin_detector.py
→ Verify: tests pass
→ Dry-run: detect plugin namespaces for Aspose.Cells
  - workspace/manifests/product-inventory.json must exist
  - workspace/verification/latest/cells-source-of-truth-proof.json must exist
  - eligibility_status must be "eligible"
→ If eligibility_status = "not_eligible": halt. Report to human. Do not proceed.
```

### Wave 2 — Data Enrichment (parallel)

```
TC-00X: example-reviewer discovery
TC-07: API delta engine
TC-08: Fixture registry
TC-09: Existing example miner
```

TC-07, TC-08, TC-09 are independent. TC-00X is independent. All can run in parallel.

### Wave 3 — Scenario Intelligence

```
TC-10: Scenario planner
  Pre-condition: cells-source-of-truth-proof.json exists with eligibility_status: eligible
```

### Wave 4 — LLM Generation

```
TC-11: LLM router (can start in parallel with Wave 2)
TC-12: Packet builder (needs TC-10 and TC-11)
TC-13: Generator (needs TC-12)
  All output to runs/{run_id}/generated/ only
```

### Wave 5 — Validation

```
TC-14: Local validation harness
TC-15: example-reviewer (needs TC-00X complete, then TC-14)
```

### Wave 6 — Publishing and Automation

```
TC-16: GitHub publisher
TC-17: Monthly runner + CI workflows
```

---

## 20. Definition of Done

The system is execution-ready when:

```
Given a configured and enabled Aspose .NET family,
the system can download the official NuGet package (no pre-release),
resolve and extract dependency packages,
extract DLL and XML documentation,
build a reflection-backed API catalog using metadata-only loading (no code execution),
detect plugin namespaces from the shipped assembly,
produce a source-of-truth proof report showing eligibility_status: eligible,
load family-specific fixture and example sources,
plan plugin scenarios only from verified symbols (blocking unclear semantics),
generate SDK-style runnable C# console examples into runs/ only,
validate them through restore, build, run, output checks, and example-reviewer,
and open an evidence-backed GitHub PR when all gates pass.
```

All 17 taskcards (TC-00X through TC-17) must have status COMPLETE.
All 20 gates (including Gate 1b and Gate 5b) must be enforced in code.
Pilot criteria (Section 13, 21 items) must all pass with verified evidence.
No disabled family config may ever be processed.
No direct push to `main` is possible through any code path.

---

## 21. Evidence Outputs

At the end of a successful pipeline run, these files must exist:

```
workspace/runs/{run_id}/
  packages/{family}/
    download-manifest.json            ← Gate 1 evidence
    dependency-manifest.json          ← Gate 1b evidence
  extracted/{family}/
    extraction-manifest.json          ← Gates 2, 3 evidence (includes requires_windows_runner)
    warnings.json                     ← Gate 3 warning evidence (if XML missing)
  validation/{scenario-slug}/
    dotnet-result.json                ← Gates 12-14 evidence
    output-validation.json            ← Gate 15 evidence
  generated/{family}/{group}/{slug}/
    Program.cs
    {Scenario}.csproj
    README.md
    example.manifest.json
    expected-output.json

workspace/manifests/
  package-lock.json
  product-inventory.json              ← Gate 5 evidence
  api-catalogs/{family}/{version}.json  ← Gate 4 evidence
  scenario-catalog.json               ← Gate 8 evidence
  fixture-registry.json               ← Gate 7 evidence
  existing-examples-index.json
  example-index.json

workspace/verification/latest/
  {family}-source-of-truth-proof.json ← Gate 5b evidence (REQUIRED before generation)
  api-delta-report.json               ← Gate 6 evidence
  example-impact-report.json
  llm-preflight.json                  ← Gate 9 evidence
  validation-results.json             ← Gates 12-15 evidence
  example-reviewer-results.json       ← Gate 16 evidence
  blocked-scenarios.json
  rejected-scenarios.json
  stale-existing-examples.json
  publishing-report.json              ← Gate 17 evidence
  monthly-run-report.json

docs/discovery/
  example-reviewer-integration-surface.md  ← TC-00X evidence
```

---

## 22. Open Questions

| # | Question | Impact | Resolution Path |
|---|---|---|---|
| OQ-1 | Does `Aspose.Cells` NuGet include `Aspose.Cells.LowCode` namespace? | High | Resolved by Gate 5b on first Wave 1E run |
| OQ-2 | What integration mode does `example-reviewer` support? | High | Resolved by TC-00X |
| OQ-3 | Is `llm.professionalize.com` OpenAI-compatible? What models? | High | Resolved by preflight check at TC-11 |
| OQ-4 | Does MetadataLoadContext handle all Aspose.Cells dependency resolution? | High | TC-05 Wave 1D dry-run determines this |
| OQ-5 | Does `aspose-plugins-examples-dotnet` repo need to be pre-created? | Medium | Publisher bootstrap mode creates it |
| OQ-6 | What Ollama model as default fallback? | Medium | Config-driven; recommended: `codellama` or `llama3` |
| OQ-7 | What TFM does Aspose.Cells ship? Will `netstandard2.0` be the winner? | High | Wave 1C extraction will answer this |

---

## 23. Blockers

| # | Blocker | Severity | Unblocked By |
|---|---|---|---|
| B1 | `GITHUB_TOKEN` write access to `aspose-plugins-examples-dotnet` | Medium | Human provides; `--dry-run` works without it |
| B2 | `LLM_PROFESSIONALIZE_API_KEY` not confirmed | Medium | Ollama fallback available; human provides for production |
| B3 | `aspose-plugins-examples-dotnet` repo may not exist | Low | Publisher bootstrap or human creates it |
| B4 | `example-reviewer` integration mode unknown | Medium | TC-00X resolves before TC-15 |
| B5 | MetadataLoadContext resolution of Aspose deps unverified | Medium | TC-05 Wave 1D dry-run resolves this |

---

## 24. Recommended Next Execution Wave

**Wave 1A — Execute now (no secrets required):**

```
Agent prompt for Wave 1A:

You are implementing Wave 1A of the Aspose .NET Plugin Example Generation Pipeline.

Repository: https://github.com/babar-raza/lowcode-example-generator
Plan: docs/plans/plugin-example-generation-execution-plan.md (v1.2.0)
Discovery: docs/discovery/current-state.md

This repo is fully greenfield. Your task is to implement TC-02 Wave 1A scope only.
Do not implement Wave 1B through 1E until Wave 1A tests pass.

Tasks:

1. Create pyproject.toml:
   - Python 3.12
   - Dependencies: jsonschema>=4.21, pyyaml>=6.0, requests>=2.31, pytest>=8.0, pytest-timeout
   - Project name: plugin-examples
   - Entry point: plugin_examples.__main__:main

2. Create src/plugin_examples/__init__.py (empty).

3. Create src/plugin_examples/family_config/__init__.py (empty).

4. Create src/plugin_examples/family_config/models.py with a FamilyConfig dataclass
   covering all fields from pipeline/schemas/family-config.schema.json Section 9.

5. Create src/plugin_examples/family_config/validator.py
   that validates a raw dict against pipeline/schemas/family-config.schema.json.

6. Create src/plugin_examples/family_config/loader.py:
   - load_family_config(path: str) -> FamilyConfig
   - Raise DisabledFamilyError if enabled=false or status=disabled.
   - Raise DisabledFamilyError if path contains /disabled/.
   - Log [SKIP] {path} — disabled for rejected configs.
   - Validate against schema before returning model.

7. Create pipeline/schemas/family-config.schema.json (from Section 9 of the plan).

8. Create pipeline/configs/families/cells.yml (from Section 9 of the plan, enabled:true, status:active).

9. Create pipeline/configs/families/disabled/words.yml (enabled:false, status:disabled, minimal).

10. Create pipeline/configs/families/disabled/pdf.yml (enabled:false, status:disabled, minimal).

11. Create pipeline/configs/families/_templates/family-template.yml (full template with comments).

12. Write tests/unit/test_family_config.py with at minimum 8 test cases:
    - cells.yml loads successfully
    - cells.yml family == "cells"
    - cells.yml enabled == True
    - config missing namespace_patterns fails validation
    - config missing package_id fails validation
    - config with version_policy: invalid fails validation
    - disabled/words.yml raises DisabledFamilyError
    - config with enabled:false raises DisabledFamilyError
    - config missing enabled field fails schema validation
    - config missing status field fails schema validation

13. Run: python -m pytest tests/unit/test_family_config.py -v
    All tests must pass before declaring Wave 1A complete.

Do not proceed to Wave 1B (NuGet fetcher) until tests/unit/test_family_config.py passes fully.

Evidence files required at Wave 1A completion:
- pipeline/schemas/family-config.schema.json (exists, validates)
- pipeline/configs/families/cells.yml (exists, validated against schema)
- src/plugin_examples/family_config/ (all four files exist)
- tests/unit/test_family_config.py (all tests pass)
```

---

## 25. Wave 0 Patch Summary

This section records every correction made from v1.0.0 to v1.1.0.

| # | Fix | Section(s) Changed | What Changed |
|---|---|---|---|
| F1 | Added `family_config` module | Section 7, TC-02 | Added `family_config/__init__.py`, `models.py`, `validator.py`, `loader.py` to repo structure and TC-02 actions |
| F2 | Added `tests/unit/test_family_config.py` | Section 7, TC-02 | File added to repo structure and TC-02 outputs/acceptance |
| F3 | Replaced fake `words.yml` and `pdf.yml` placeholders | Section 7, Section 9, TC-02 | Active `words.yml` and `pdf.yml` replaced with `pipeline/configs/families/disabled/words.yml`, `disabled/pdf.yml`, and `_templates/family-template.yml` |
| F4 | Added `enabled` field to schema | Section 9 | `enabled: boolean` is now required in schema and cells.yml |
| F5 | Added `status` field to schema | Section 9 | `status: enum ["active","disabled","experimental"]` is now required |
| F6 | Added `validation.runtime_runner` to schema | Section 9 | `runtime_runner: enum ["linux","windows","auto"]` added to validation block |
| F7 | Added `nuget.allow_prerelease` to schema | Section 9 | `allow_prerelease: boolean, default false` added |
| F8 | Added `nuget.dependency_resolution` to schema | Section 9 | `dependency_resolution.enabled` and `max_depth` added |
| F9 | Fixed target framework preference order | Section 9, TC-04 | `netstandard2.0` moved to first position; full new order is ns2.0 → ns2.1 → net8.0 → net6.0 → net48 |
| F10 | Added Windows runner rule for net48 | Section 9, TC-04, Section 12 | Framework selector must set `requires_windows_runner: true` when net48 selected; extraction-manifest and CI must route accordingly |
| F11 | Strengthened DllReflector design | TC-05 | Replaced loose wording with explicit MetadataLoadContext/Mono.Cecil requirement; added five strict design rules (no Load, no Activator, no static constructors, use PathAssemblyResolver with deps) |
| F12 | Added NuGet dependency resolution | TC-03, TC-04 | Added `dependency_resolver.py` module, `dependency-manifest.json`, dependency DLL extraction to resolved-libs, and dependency tests |
| F13 | Split Wave 1 into 1A through 1E | Section 19 | Wave 1A: foundation+schema; 1B: NuGet fetch; 1C: extractor+deps; 1D: DllReflector+catalog; 1E: detector+proof |
| F14 | Added source-of-truth proof report | TC-06, Section 5, Section 10, Section 12, Section 21 | `{family}-source-of-truth-proof.json` required with all specified fields; Gate 5b added; TC-10 pre-condition enforced |
| F15 | Added TC-00X (example-reviewer discovery) | Section 11 EPIC-00 | New taskcard before all implementation taskcards; required before TC-15 |
| F16 | Added generated file governance | TC-13 | Generator may only write to `workspace/runs/{run_id}/generated/`, `workspace/runs/{run_id}/validation/`, `workspace/verification/latest/`, `workspace/manifests/` |
| F17 | Strengthened scenario planner rules | TC-10 | Added `blocked_unclear_semantics` status; rule that LLM must not invent intent from class names alone; blocked scenarios persist requirement |
| F18 | Fixed plan status | Header, Section 26 | Status changed from "READY FOR EXECUTION (Wave 1)" to "READY FOR WAVE 1A" after patch checklist verified |
| F19 | Added Gate 1b | Section 12 | Gate 1b: Dependency Resolution |
| F20 | Added Gate 5b | Section 12 | Gate 5b: Source-of-Truth Proof |
| F21 | Replaced v1 root-cluttered repo structure with v2 grouped layout | Sections 7, 27, 28 | Root folders reduced from 13+ to 11 with clear separation: `pipeline/` (definition), `workspace/` (runtime), `src/` (code), `tools/` (tooling) |
| F22 | Added Concurrency Safety Model | Section 29 | Gate 0, run record schema, concurrency report schema, overlap classification model, hard rules |
| F23 | Added TC-00A (Concurrency Preflight) | Section 11 EPIC-00A | Mandatory before any implementation; creates run record; classifies overlap |
| F24 | Added TC-00B (Midflight Ownership Recheck) | Section 11 EPIC-00A | Embedded protocol in every implementation taskcard; re-checks git state before writes |
| F25 | Added TC-00C (Pre-Commit Scope Verification) | Section 11 EPIC-00A | Mandatory before commit; produces concurrency report; verifies only expected files changed |
| F26 | Added TC-00D (Structure Migration) | Section 28 | Moves placeholder files from v1 layout to v2; creates .gitignore; verification commands |
| F27 | Added TC-00E (Path Compatibility Update) | Section 28 | Updates all path references after migration; grep verification for orphaned old paths |
| F28 | Added Gitignore Policy | Section 30 | `workspace/runs/` gitignored; `workspace/manifests/` and `workspace/verification/` committed; rationale documented |
| F29 | Added Structure Migration Rollback Plan | Section 31 | Safe rollback since no v1 files are committed; user backup preserves v1.1.0 plan |
| F30 | Added Structure Readiness Gate | Section 32 | 12-item checklist must pass before implementation; all items PASS |
| F31 | Added Wave 0A/0B/0C to execution order | Section 19 | Concurrency preflight (0A), structure migration (0B), compatibility update (0C) before Wave 1A |
| F32 | Updated execution order paths | Section 19 | Wave 1A-1E paths now reference `pipeline/schemas/`, `pipeline/configs/`, `workspace/` |
| F33 | Added Gate 0 to verification gates | Section 12 | Gate 0: Concurrency and Ownership Safety — run record, overlap classification, no direct_overlap |
| F34 | Superseded Section 7 | Section 7 | Added SUPERSEDED notice pointing to Sections 27-28; preserved as historical record |

---

## 26. Execution Readiness Checklist

This checklist must pass before the plan is declared ready for implementation.

### v1.1.0 Checks (preserved)

| # | Requirement | Status |
|---|---|---|
| C1 | `family_config` module (loader, models, validator) listed in repo structure | PASS |
| C2 | `tests/unit/test_family_config.py` listed in repo structure and TC-02 | PASS |
| C3 | Config schema includes `enabled` and `status` required fields | PASS |
| C4 | `disabled/` path configs are rejected by loader regardless of field values | PASS |
| C5 | `disabled/words.yml` and `disabled/pdf.yml` are placeholders only, never processed | PASS |
| C6 | `nuget.dependency_resolution` is planned with `dependency_resolver.py` module | PASS |
| C7 | DllReflector uses MetadataLoadContext or Mono.Cecil; no code execution | PASS |
| C8 | DllReflector resolves deps from `dependency_dll_paths` and trusted assemblies | PASS |
| C9 | `{family}-source-of-truth-proof.json` is required before scenario planning | PASS |
| C10 | Gate 5b enforces proof file check before TC-07 through TC-13 | PASS |
| C11 | Wave 1 is split into 1A through 1E with explicit per-wave scope | PASS |
| C12 | TC-00X (example-reviewer discovery) is listed before TC-15 | PASS |
| C13 | TC-00X is a pre-condition for TC-15 | PASS |
| C14 | Generator writes only to `workspace/runs/`, `workspace/verification/latest/`, `workspace/manifests/` | PASS |
| C15 | `blocked_unclear_semantics` status exists in scenario planner | PASS |
| C16 | Blocked scenarios never silently dropped | PASS |
| C17 | `netstandard2.0` is first in TFM preference list | PASS |
| C18 | Windows runner flag set when `net48` selected | PASS |
| C19 | No direct generation allowed before source-of-truth proof | PASS |
| C20 | Plan version is 1.2.0 | PASS |

### v1.2.0 Checks (new)

| # | Requirement | Status |
|---|---|---|
| C21 | Section 27 (ADR) explains why v1 structure was rejected | PASS |
| C22 | Section 28 (Structure v2) provides complete directory tree with rationale | PASS |
| C23 | `pipeline/` groups configs, schemas, prompts under one namespace | PASS |
| C24 | `workspace/` groups runs, manifests, verification under one namespace | PASS |
| C25 | `workspace/runs/` is gitignored; `workspace/manifests/` and `workspace/verification/` are committed | PASS |
| C26 | Gate 0 (Concurrency and Ownership Safety) is in the gates table | PASS |
| C27 | TC-00A (Concurrency Preflight) is defined with run record schema | PASS |
| C28 | TC-00B (Midflight Recheck) is defined as embedded protocol | PASS |
| C29 | TC-00C (Pre-Commit Scope Verification) produces concurrency report | PASS |
| C30 | TC-00D (Structure Migration) has verification commands and rollback plan | PASS |
| C31 | TC-00E (Path Compatibility) has grep-based orphan path checks | PASS |
| C32 | Wave 0A/0B/0C precede Wave 1A in execution order | PASS |
| C33 | No implementation taskcard can run before TC-00A passes | PASS |
| C34 | `.gitignore` policy is defined with committed vs. ignored rationale | PASS |
| C35 | Rollback plan exists for structure migration | PASS |

**Checklist result: ALL 35 ITEMS PASS**

**Plan status: READY FOR STRUCTURE MIGRATION (Wave 0B)**

---

---

## 27. Architecture Decision Record — Repository Structure v2

### ADR-001: Replace v1 Root-Cluttered Layout with Grouped Structure

**Status:** ACCEPTED

**Context:**

The v1.1.0 plan (Section 7) placed 13+ directories at the repository root:

```
README.md  AGENTS.md  pyproject.toml
configs/  schemas/  prompts/  src/  tests/  docs/  tools/
runs/  manifests/  verification/
.github/
```

This layout has these structural problems:

1. **No separation of concerns at the root level.** `configs/`, `schemas/`, and `prompts/` are all pipeline definition assets (stable, checked-in, rarely changing), but they appear as three separate root-level directories alongside unrelated operational folders. A new contributor or agent must read all 13 folders to understand the repo.

2. **Runtime outputs mixed with source artifacts.** `runs/` (ephemeral per-run data), `manifests/` (pipeline state), and `verification/` (evidence) are all operational output, but they sit at the same level as `src/` and `docs/`. There is no visual or structural signal that `runs/` should be gitignored while `workspace/manifests/` should be partially committed.

3. **No gitignore policy.** The v1 plan never defined a `.gitignore`. Without one, every `runs/` directory, every downloaded `.nupkg`, every extracted DLL, and every generated example would appear in `git status`. On a real pipeline run, hundreds of untracked files would pollute the working tree.

4. **Ambiguous ownership boundaries.** When two agents work simultaneously (e.g., one on NuGet fetcher, one on fixture registry), both write to root-level `manifests/` and `runs/`. Without structural grouping, it is harder to detect file-level conflicts.

5. **Documentation and evidence are not separated.** `docs/` (human-authored architecture docs) and `verification/` (machine-generated evidence JSON) have fundamentally different lifetimes and audiences, but both appear at the root level. `docs/` is stable reference material. `workspace/verification/latest/` is regenerated every pipeline run.

**Decision:**

Group the repo into five clear top-level concerns:

| Root folder | Purpose | Committed? |
|---|---|---|
| `src/` | Python pipeline source code | Yes |
| `tests/` | Test code and test fixtures | Yes |
| `docs/` | Human-authored documentation | Yes |
| `tools/` | Reusable .NET tooling (DllReflector) | Yes |
| `pipeline/` | Pipeline definition: configs, schemas, prompts | Yes |
| `workspace/` | Pipeline runtime: runs, manifests, verification evidence | Partially (runs/ gitignored) |
| `.github/` | CI workflows | Yes |

**Consequences:**

- Import paths in Python code reference `pipeline/configs/`, `pipeline/schemas/`, `pipeline/prompts/` instead of root-level paths. This requires the `family_config/loader.py` and other modules to accept a configurable base path or use package resource resolution.
- The `tools/DllReflector/` path is unchanged (it was already under `tools/`).
- All existing `.gitkeep` placeholder files in the old structure must be migrated (TC-00D).
- All path references in the plan, AGENTS.md, and docs must be updated (TC-00E).

---

## 28. Repository Structure v2

### Pipeline Repo (this repo)

```
lowcode-example-generator/
  README.md                              ← project overview
  AGENTS.md                              ← governance rules for agents and humans
  pyproject.toml                         ← Python project definition
  .gitignore                             ← gitignore policy (see Section 30)

  .github/                               ← CI workflows
    workflows/
      build-and-test.yml
      monthly-package-refresh.yml

  src/                                   ← PYTHON SOURCE CODE
    plugin_examples/
      __init__.py
      __main__.py                        ← CLI entry point
      family_config/
        __init__.py
        loader.py
        models.py
        validator.py
      package_watcher/
        __init__.py
        watcher.py
      nuget_fetcher/
        __init__.py
        fetcher.py
        cache.py
        dependency_resolver.py
      nupkg_extractor/
        __init__.py
        extractor.py
        framework_selector.py
      reflection_catalog/
        __init__.py
        reflector.py
        catalog_builder.py
        schema_validator.py
      plugin_detector/
        __init__.py
        detector.py
        proof_reporter.py
      api_delta/
        __init__.py
        delta_engine.py
        impact_mapper.py
      fixture_registry/
        __init__.py
        registry.py
        fixture_fetcher.py
      example_miner/
        __init__.py
        miner.py
        symbol_validator.py
      scenario_planner/
        __init__.py
        planner.py
        scenario_catalog.py
      llm_router/
        __init__.py
        router.py
        preflight.py
        providers/
          __init__.py
          professionalize.py
          ollama.py
      generator/
        __init__.py
        packet_builder.py
        code_generator.py
        project_generator.py
        manifest_writer.py
      verifier_bridge/
        __init__.py
        bridge.py
        dotnet_runner.py
        output_validator.py
      publisher/
        __init__.py
        publisher.py
        pr_builder.py
      reporting/
        __init__.py
        reporter.py
        evidence_packager.py

  tests/                                 ← TEST CODE
    unit/
      test_family_config.py
      test_nuget_fetcher.py
      test_dependency_resolver.py
      test_nupkg_extractor.py
      test_reflection_catalog.py
      test_plugin_detector.py
      test_api_delta.py
      test_fixture_registry.py
      test_scenario_planner.py
      test_llm_router.py
      test_generator.py
      test_verifier_bridge.py
      test_publisher.py
    integration/
      test_cells_pipeline.py
    fixtures/
      sample-api-catalog.json

  docs/                                  ← HUMAN DOCUMENTATION
    plans/
      plugin-example-generation-execution-plan.md
    discovery/
      current-state.md
      example-reviewer-integration-surface.md
    architecture.md
    family-config.md
    verifier-integration.md
    monthly-runbook.md
    publishing-model.md

  tools/                                 ← REUSABLE .NET TOOLING
    DllReflector/
      DllReflector.csproj
      Program.cs

  pipeline/                              ← PIPELINE DEFINITION (stable, checked-in)
    configs/
      families/
        cells.yml
        _templates/
          family-template.yml
        disabled/
          words.yml
          pdf.yml
      llm-routing.yml
      verifier.yml
      github-publishing.yml
      plugin-namespace-patterns.yml
    schemas/
      family-config.schema.json
      api-catalog.schema.json
      scenario.schema.json
      example-manifest.schema.json
      validation-result.schema.json
      scenario-packet.schema.json
    prompts/
      scenario-planner.md
      example-generator.md
      example-repair.md
      semantic-review.md

  workspace/                             ← PIPELINE RUNTIME (operational data)
    runs/                                ← GITIGNORED: per-run ephemeral data
      .gitkeep
      {run_id}/
        run-record.json
        concurrency-report.json
        packages/{family}/
          download-manifest.json
          dependency-manifest.json
          *.nupkg
        extracted/{family}/
          extraction-manifest.json
          primary/
          deps/
          resolved-libs/
        generated/{family}/{group}/{slug}/
          Program.cs
          *.csproj
          README.md
          example.manifest.json
          expected-output.json
        validation/{slug}/
          dotnet-result.json
          output-validation.json
        pr-preview/
    manifests/                           ← COMMITTED: pipeline state
      .gitkeep
      package-lock.json
      product-inventory.json
      api-catalogs/{family}/{version}.json
      scenario-catalog.json
      fixture-registry.json
      existing-examples-index.json
      example-index.json
    verification/                        ← COMMITTED: evidence and proofs
      latest/
        .gitkeep
        {family}-source-of-truth-proof.json
        api-delta-report.json
        example-impact-report.json
        llm-preflight.json
        validation-results.json
        example-reviewer-results.json
        blocked-scenarios.json
        rejected-scenarios.json
        stale-existing-examples.json
        publishing-report.json
        monthly-run-report.json
```

### Root item rationale

| Item | Why it is at root |
|---|---|
| `README.md` | Universal project entry point |
| `AGENTS.md` | Governance — must be visible to all agents |
| `pyproject.toml` | Python build system requires it at root |
| `.gitignore` | Git requires it at root |
| `.github/` | GitHub requires it at root |
| `src/` | Standard Python source layout |
| `tests/` | Standard test layout |
| `docs/` | Standard documentation location |
| `tools/` | Reusable .NET tooling — separate build system, warrants visibility |
| `pipeline/` | Pipeline definition assets — groups configs, schemas, prompts under one namespace |
| `workspace/` | Pipeline runtime outputs — groups runs, manifests, verification under one namespace |

### What was removed from root

| Old root item | New location | Rationale |
|---|---|---|
| `configs/` | `pipeline/configs/` | Grouped with other pipeline definition assets |
| `schemas/` | `pipeline/schemas/` | Grouped with other pipeline definition assets |
| `prompts/` | `pipeline/prompts/` | Grouped with other pipeline definition assets |
| `runs/` | `workspace/runs/` | Grouped with other runtime outputs; gitignored |
| `manifests/` | `workspace/manifests/` | Grouped with other runtime outputs; committed |
| `verification/` | `workspace/verification/` | Grouped with other runtime outputs; committed |

### Structure Migration Taskcards

**Taskcard ID:** TC-00D
**Title:** Execute Repository Structure Migration
**Objective:** Move existing placeholder files from the v1.1.0 layout to the v2 layout. Create `.gitignore`. Verify no files are lost.

**Dependencies:** TC-00A (concurrency preflight passed)

**Actions:**
1. Run TC-00B midflight check.
2. Create `.gitignore` (see Section 30).
3. Create `pipeline/` directory structure:
   - Move `configs/` → `pipeline/configs/`
   - Move `schemas/` → `pipeline/schemas/`
   - Move `prompts/` → `pipeline/prompts/`
4. Create `workspace/` directory structure:
   - Move `runs/` → `workspace/runs/`
   - Move `manifests/` → `workspace/manifests/`
   - Move `verification/` → `workspace/verification/`
5. Remove empty old directories (only if completely empty after move).
6. Verify file count before and after migration matches.
7. Run TC-00B midflight recheck after moves.

**Outputs:**
- All files in new locations
- `.gitignore` at repo root
- No orphaned directories

**Acceptance Criteria:**
- `pipeline/configs/`, `pipeline/schemas/`, `pipeline/prompts/` exist with expected contents.
- `workspace/runs/`, `workspace/manifests/`, `workspace/verification/` exist with expected contents.
- Old root-level `configs/`, `schemas/`, `prompts/`, `runs/`, `manifests/`, `verification/` directories no longer exist.
- File count is identical before and after.
- `git status` shows expected renames only.

**Verification Commands:**
```bash
# Before migration: count files
find . -not -path './.git/*' -type f | wc -l
# After migration: count files — must match
find . -not -path './.git/*' -type f | wc -l
# Verify old dirs are gone
test ! -d configs && test ! -d schemas && test ! -d prompts
test ! -d runs && test ! -d manifests && test ! -d verification
# Verify new dirs exist
test -d pipeline/configs && test -d pipeline/schemas && test -d pipeline/prompts
test -d workspace/runs && test -d workspace/manifests && test -d workspace/verification
```

**Failure Handling:**
- If any file is lost during migration: STOP. Restore from untracked state (files are not committed yet).

**Rollback Plan:**
Since no files are committed yet, rollback is:
1. Move files back from `pipeline/` and `workspace/` to old root locations.
2. Delete `pipeline/` and `workspace/` directories.
3. Delete `.gitignore`.
4. `git status` should return to the pre-migration state.
The user's backup at `docs/plans/plugin-example-generation-execution-plan copy.md` preserves the v1.1.0 plan.

**Evidence Files:**
- `.gitignore`

---

**Taskcard ID:** TC-00E
**Title:** Path Compatibility Update
**Objective:** Update all path references in the plan, AGENTS.md, docs, and any existing source or test files to use the v2 directory layout. Verify no broken references remain.

**Dependencies:** TC-00D (structure migration complete)

**Actions:**
1. Run TC-00B midflight check.
2. Search all `.md`, `.py`, `.yml`, `.json` files for old root-level paths:
   - `configs/` → `pipeline/configs/`
   - `schemas/` → `pipeline/schemas/`
   - `prompts/` → `pipeline/prompts/`
   - `runs/` → `workspace/runs/`
   - `manifests/` → `workspace/manifests/`
   - `verification/` → `workspace/verification/`
3. Update references in:
   - `AGENTS.md`
   - `docs/discovery/current-state.md`
   - Any Python source files under `src/` (if they exist at this point)
   - Any test files under `tests/` (if they exist at this point)
4. Do NOT update the v1 structure tree in Section 7 of the plan (it is preserved as historical record with SUPERSEDED label).
5. Run TC-00B midflight recheck.
6. Run TC-00C pre-commit scope verification.

**Outputs:**
- Updated path references in all affected files.
- No orphaned old-path references (except in Section 7 historical record).

**Acceptance Criteria:**
- `grep -r 'configs/families' . --include='*.md' --include='*.py' --include='*.yml' | grep -v 'pipeline/configs' | grep -v 'Section 7'` returns no results (outside the deprecated section).
- `grep -r 'schemas/' . --include='*.md' --include='*.py' | grep -v 'pipeline/schemas' | grep -v 'Section 7' | grep -v '$schema'` returns no results.
- `grep -r 'runs/' . --include='*.md' --include='*.py' | grep -v 'workspace/runs' | grep -v 'Section 7'` returns no results.

**Verification Commands:**
```bash
# Check for orphaned old paths (excluding Section 7 historical record)
grep -rn 'configs/families\|schemas/\|prompts/\|^runs/\|manifests/\|verification/' \
  --include='*.md' --include='*.py' --include='*.yml' \
  . | grep -v 'pipeline/' | grep -v 'workspace/' | grep -v 'Section 7' | grep -v 'SUPERSEDED' | grep -v '$schema'
```

**Failure Handling:**
- If orphaned paths found: update them. Do not commit until all references are consistent.

**Evidence Files:**
- None (this is a consistency pass, not a new artifact)

---

## 29. Concurrency Safety Model

### Purpose

This model prevents parallel agent or human work from conflicting. It applies at three phases: preflight (TC-00A), midflight (TC-00B), and pre-commit (TC-00C). It is a hard gate — Gate 0 — that must pass before any implementation work begins.

### Protocol Summary

```
PREFLIGHT (TC-00A)
  │
  ├─ Check: git status, branches, stashes, worktrees, lock files, run records
  ├─ Classify: no_overlap / adjacent / direct / unknown
  ├─ Write: workspace/runs/{run_id}/run-record.json
  ├─ Decision: proceed / stop
  │
  └─ Gate 0 passes → proceed to implementation
       │
       ▼
  MIDFLIGHT (TC-00B) — before each major write phase
       │
       ├─ Re-check: git status vs. run record intended_files
       ├─ Detect: new untracked files, modified files outside scope
       ├─ Decision: proceed / stop
       │
       └─ Passes → continue implementation
            │
            ▼
       PRE-COMMIT (TC-00C) — before git add / git commit
            │
            ├─ Verify: only intended_files changed
            ├─ Write: workspace/runs/{run_id}/concurrency-report.json
            ├─ Decision: commit / stop
            │
            └─ Passes → commit is safe
```

### Overlap Classification Model

| Classification | Meaning | Action |
|---|---|---|
| `no_overlap` | No other agent or human is modifying any of the intended files. | Proceed freely. |
| `adjacent_overlap` | Another agent is working on nearby but non-overlapping files (e.g., one agent writes `nuget_fetcher/`, another writes `fixture_registry/`). | Proceed with caution. Document why files are non-overlapping. |
| `direct_overlap` | Another agent or human has modified or is modifying the same files. | STOP immediately. Report the conflict. Do not write. |
| `unknown_ownership` | Files exist that cannot be attributed to this agent or the current task lineage. | Assume unsafe. STOP. Investigate before proceeding. |

### Hard Rules

1. Never use `git reset --hard`, `git stash pop`, `git checkout .`, or `git clean -f` to resolve overlap.
2. Never auto-merge conflicting changes.
3. Never overwrite, rename, move, or delete another agent's files without explicit human approval.
4. Every implementation taskcard must reference the active run record.
5. Every implementation taskcard must perform at least one midflight check.
6. No commit may proceed without a pre-commit scope verification.

### Run Record Schema

```json
{
  "run_id": "string",
  "owner": "string",
  "task_name": "string",
  "start_time": "ISO-8601",
  "branch": "string",
  "worktree": "string",
  "purpose": "string",
  "intended_files": ["string"],
  "intended_directories": ["string"],
  "expected_outputs": ["string"],
  "overlap_classification": "no_overlap | adjacent_overlap | direct_overlap | unknown_ownership",
  "overlap_evidence": "string",
  "safety_decision": "string",
  "rollback_notes": "string",
  "verification_commands": ["string"],
  "midflight_checks": [
    {
      "timestamp": "ISO-8601",
      "git_status_clean": "boolean",
      "unexpected_files": ["string"],
      "decision": "proceed | stop"
    }
  ]
}
```

### Concurrency Report Schema

```json
{
  "run_id": "string",
  "touched_files": ["string"],
  "moved_files": [{"from": "string", "to": "string"}],
  "deleted_files": ["string"],
  "created_files": ["string"],
  "detected_overlaps": ["string"],
  "ownership_decisions": ["string"],
  "safety_decisions": ["string"],
  "remaining_risks": ["string"],
  "verification_commands_run": ["string"],
  "final_git_status": "string"
}
```

---

## 30. Gitignore Policy

### `.gitignore` contents

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.eggs/
*.egg
.venv/
venv/

# .NET
bin/
obj/
*.dll
*.exe
*.pdb
*.nupkg

# IDE
.vscode/
.idea/
*.suo
*.user
*.sln.docuser

# OS
Thumbs.db
.DS_Store

# Pipeline runtime — ephemeral per-run data
workspace/runs/*/
!workspace/runs/.gitkeep

# Downloaded packages (large binaries)
*.nupkg

# Extracted assemblies
workspace/runs/*/extracted/

# Generated examples (pre-validation)
workspace/runs/*/generated/
```

### What is committed vs. gitignored

| Path | Committed? | Rationale |
|---|---|---|
| `src/` | Yes | Source code |
| `tests/` | Yes | Test code |
| `docs/` | Yes | Human documentation |
| `tools/` | Yes (source only) | .NET project source; `bin/`/`obj/` gitignored |
| `pipeline/` | Yes (all) | Stable pipeline definition |
| `workspace/runs/` | No | Ephemeral per-run data (packages, extracted DLLs, generated code, validation results) |
| `workspace/manifests/` | Yes | Pipeline state (package-lock.json, product inventories, catalogs, indexes) |
| `workspace/verification/` | Yes | Evidence and proofs (source-of-truth proofs, delta reports, reviewer results) |
| `.github/` | Yes | CI workflows |

### Rationale for `workspace/runs/` being gitignored

A single pipeline run against one family can produce:
- A `.nupkg` file (10-50 MB)
- Extracted DLLs and dependency DLLs (50-200 MB)
- Generated C# projects (small, but per-scenario)
- Validation stdout/stderr captures
- PR preview files

Committing this data would bloat the repo. The important results are promoted to `workspace/manifests/` (state) and `workspace/verification/` (evidence) by the pipeline code. Raw run data in `workspace/runs/` is disposable after the run completes.

### Rationale for `workspace/manifests/` and `workspace/verification/` being committed

These directories contain the pipeline's durable knowledge:
- `package-lock.json` — enables delta detection between runs
- `product-inventory.json` — records which families are eligible
- `api-catalogs/` — the reflected API that generation depends on
- `{family}-source-of-truth-proof.json` — the mandatory pre-generation gate
- `blocked-scenarios.json` — blocked scenarios must persist across runs

Without committing these, every run would start from scratch with no history.

---

## 31. Structure Migration Rollback Plan

### Trigger

Rollback is triggered if:
1. TC-00D (structure migration) fails verification (file count mismatch).
2. TC-00E (path compatibility) discovers references that cannot be updated safely.
3. Any implementation taskcard discovers that the new structure breaks imports or test discovery.

### Rollback Steps

Since no files from the v1.1.0 structure have been committed to git, rollback is safe:

1. Move files back from `pipeline/` to root-level `configs/`, `schemas/`, `prompts/`.
2. Move files back from `workspace/` to root-level `runs/`, `manifests/`, `verification/`.
3. Delete empty `pipeline/` and `workspace/` directories.
4. Delete `.gitignore` (or revert to a minimal version).
5. Restore the plan from the user's backup at `docs/plans/plugin-example-generation-execution-plan copy.md`.
6. Verify `git status` returns to pre-migration state.

### Prevention

The migration taskcard (TC-00D) requires a file count check before and after. If counts don't match, the migration fails before any old directories are removed.

---

## 32. Structure Readiness Gate

Implementation may not begin (Wave 1A) until all of the following are true:

| # | Requirement | Status |
|---|---|---|
| S1 | Section 27 (ADR) documents why v1 structure was rejected | PASS |
| S2 | Section 28 (Structure v2) provides the production-grade layout | PASS |
| S3 | Section 29 (Concurrency Model) defines Gate 0 and TC-00A/B/C | PASS |
| S4 | Section 30 (Gitignore Policy) defines what is committed vs. ignored | PASS |
| S5 | Section 31 (Rollback Plan) provides safe rollback procedure | PASS |
| S6 | TC-00D (migration taskcard) is defined with verification commands | PASS |
| S7 | TC-00E (compatibility taskcard) is defined with path update rules | PASS |
| S8 | Wave 0A/0B/0C are defined in execution order before Wave 1A | PASS |
| S9 | Gate 0 is in the verification gates table | PASS |
| S10 | Run record schema is defined | PASS |
| S11 | Concurrency report schema is defined | PASS |
| S12 | Plan version is 1.2.0 | PASS |

**Structure readiness: ALL 12 ITEMS PASS**

---

*Plan last updated: 2026-04-28 (v1.2.0 patch — structure redesign + concurrency model). Re-run planning agent after any discovery that contradicts findings or after significant implementation discoveries during Wave 0/1.*
