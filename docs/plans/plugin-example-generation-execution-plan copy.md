# Plugin Example Generation — Execution-Ready Plan

**Version:** 1.0.0
**Date:** 2026-04-27
**Status:** READY FOR EXECUTION (Wave 1)
**Repo:** https://github.com/babar-raza/lowcode-example-generator
**Plan Author:** Planning Agent (Claude)
**Current-State Evidence:** `docs/discovery/current-state.md`

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

**Conclusion:** This is a complete greenfield. All modules must be built from scratch. No legacy code exists to audit, preserve, or discard. No conflicting structure constrains the build.

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

---

## 6. Architecture

```
NuGet Package
     │
     ▼
nuget_fetcher ──► nupkg_extractor ──► reflection_catalog ──► plugin_detector
                                              │
                                        api_delta_engine
                                              │
                        ┌─────────────────────┼──────────────────────┐
                        │                     │                      │
               fixture_registry       example_miner           scenario_planner
                        │                     │                      │
                        └─────────────────────┼──────────────────────┘
                                              │
                                         llm_router
                                              │
                                      [prompt packet]
                                              │
                                       generator
                                              │
                               ┌──────────────┼──────────────┐
                               │              │              │
                         dotnet restore  dotnet build   dotnet run
                               │              │              │
                         output_validator     │              │
                               │              │              │
                        verifier_bridge (example-reviewer)
                               │
                           publisher
                               │
                          GitHub PR
```

---

## 7. Repository Structure Decision

**This repo (`lowcode-example-generator`) = the pipeline repo.**

**Separate repo (`aspose-plugins-examples-dotnet`) = the published examples repo.**

### Pipeline Repo Structure (this repo)

```
lowcode-example-generator/
  README.md
  pyproject.toml
  AGENTS.md

  configs/
    families/
      cells.yml
      words.yml
      pdf.yml
    plugin-namespace-patterns.yml
    llm-routing.yml
    verifier.yml
    github-publishing.yml

  src/
    plugin_examples/
      __init__.py
      package_watcher/
        __init__.py
        watcher.py
      nuget_fetcher/
        __init__.py
        fetcher.py
        cache.py
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
      test_nuget_fetcher.py
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
      words.yml
      pdf.yml
    verifier.yml

  fixtures/
    cells/
      xlsx/
        basic-workbook.xlsx
      csv/
        simple-data.csv
    words/
      docx/
        basic-document.docx
    pdf/
      pdf/
        sample.pdf

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
    words/
      lowcode/
        convert-docx-to-pdf/
          ConvertDocxToPdf.csproj
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

User run command:

```bash
dotnet run --project examples/cells/lowcode/convert-xlsx-to-pdf/ConvertXlsxToPdf.csproj
```

---

## 9. Family Config Schema

### Schema file: `schemas/family-config.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FamilyConfig",
  "type": "object",
  "required": ["family", "display_name", "nuget", "plugin_detection", "github", "fixtures", "existing_examples", "generation", "validation", "llm"],
  "properties": {
    "family": { "type": "string" },
    "display_name": { "type": "string" },
    "nuget": {
      "type": "object",
      "required": ["package_id", "version_policy"],
      "properties": {
        "package_id": { "type": "string" },
        "version_policy": { "enum": ["latest-stable", "pinned"] },
        "pinned_version": { "type": ["string", "null"] },
        "target_framework_preference": {
          "type": "array",
          "items": { "type": "string" },
          "minItems": 1
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
        "require_example_reviewer": { "type": "boolean" }
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

### Pilot config: `configs/families/cells.yml`

```yaml
family: cells
display_name: Aspose.Cells for .NET

nuget:
  package_id: Aspose.Cells
  version_policy: latest-stable
  pinned_version: null
  target_framework_preference:
    - net8.0
    - netstandard2.0
    - net48

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

llm:
  provider_order:
    - llm_professionalize
    - ollama
```

---

## 10. Pipeline Stages

| # | Stage | Module | Gate(s) |
|---|---|---|---|
| 1 | Package watcher | `package_watcher` | — |
| 2 | NuGet fetch | `nuget_fetcher` | Gate 1 |
| 3 | `.nupkg` extract | `nupkg_extractor` | Gates 2, 3 |
| 4 | Reflection catalog build | `reflection_catalog` | Gate 4 |
| 5 | Plugin namespace detect | `plugin_detector` | Gate 5 |
| 6 | API delta calculate | `api_delta` | Gate 6 |
| 7 | Fixture registry | `fixture_registry` | Gate 7 |
| 8 | Existing example mine | `example_miner` | — |
| 9 | Scenario plan | `scenario_planner` | Gate 8 |
| 10 | LLM preflight | `llm_router` | Gate 9 |
| 11 | Generation packet build | `generator.packet_builder` | Gates 10, 11 |
| 12 | Example project generate | `generator.project_generator` | — |
| 13 | Restore | `verifier_bridge.dotnet_runner` | Gate 12 |
| 14 | Build | `verifier_bridge.dotnet_runner` | Gate 13 |
| 15 | Run | `verifier_bridge.dotnet_runner` | Gate 14 |
| 16 | Output validation | `verifier_bridge.output_validator` | Gate 15 |
| 17 | example-reviewer | `verifier_bridge.bridge` | Gate 16 |
| 18 | PR publish | `publisher` | Gates 17, 18 |
| 19 | Reporting | `reporting` | — |

---

## 11. Taskcards

---

### EPIC-01: Repository and Architecture Discovery

---

**Taskcard ID:** TC-01
**Title:** Discover Current Repo State
**Objective:** Establish baseline facts about the repo before any implementation. Block incorrect assumptions from reaching implementation.

**Dependencies:** None

**Inputs:**
- Git repository contents
- `.git/config` for remote URL
- Any existing Python, .NET, YAML, JSON, or Markdown files

**Actions:**
1. Run `glob **/*` to inventory all files.
2. Read `README.md` if present.
3. Read `.git/config` for remote.
4. Answer all 15 mandatory investigation questions with file evidence.
5. Record repo map.
6. Record constraints.
7. Record recommended execution starting point.

**Outputs:**
- `docs/discovery/current-state.md`
- `docs/discovery/repo-map.md`
- `docs/discovery/constraints.md`

**Acceptance Criteria:**
- All 15 questions answered with file evidence or explicit "NOT FOUND".
- No assumptions stated without evidence.
- Recommended target location justified.
- Current capabilities and gaps explicitly documented.

**Verification Commands:**
```bash
# Verify discovery doc exists and is non-empty
test -f docs/discovery/current-state.md && wc -l docs/discovery/current-state.md
```

**Failure Handling:**
- If repo access is denied, stop and report to human.
- If repo has unexpected large structure, extend discovery before proceeding.

**Evidence Files:**
- `docs/discovery/current-state.md`

**Status:** COMPLETE (greenfield confirmed, evidence in current-state.md)

---

### EPIC-02: Family Config System

---

**Taskcard ID:** TC-02
**Title:** Define and Validate Family Config Schema
**Objective:** Create the durable per-family configuration schema and pilot Cells config. Make schema validation executable so the pipeline can reject malformed configs early.

**Dependencies:** TC-01

**Inputs:**
- Discovery findings (TC-01)
- Normalized plan (this document)

**Actions:**
1. Create `schemas/family-config.schema.json` (see Section 9).
2. Create `configs/families/cells.yml` (see Section 9).
3. Create `configs/families/words.yml` placeholder.
4. Create `configs/families/pdf.yml` placeholder.
5. Create `configs/plugin-namespace-patterns.yml` with global pattern registry.
6. Create `configs/llm-routing.yml` with provider order and preflight rules.
7. Create `configs/verifier.yml` with gate configuration.
8. Create `configs/github-publishing.yml` with PR and branch rules.
9. Write `src/plugin_examples/family_config/loader.py` to load and validate configs.
10. Write `tests/unit/test_family_config.py` covering:
    - Valid cells config passes validation.
    - Config missing `plugin_detection.namespace_patterns` fails.
    - Config missing `nuget.package_id` fails.
    - Config with `version_policy: invalid` fails.

**Outputs:**
- `schemas/family-config.schema.json`
- `configs/families/cells.yml`
- `configs/families/words.yml`
- `configs/families/pdf.yml`
- `configs/plugin-namespace-patterns.yml`
- `configs/llm-routing.yml`
- `configs/verifier.yml`
- `configs/github-publishing.yml`
- `src/plugin_examples/family_config/loader.py`
- `tests/unit/test_family_config.py`

**Acceptance Criteria:**
- `python -m pytest tests/unit/test_family_config.py` passes.
- `cells.yml` validates against schema without errors.
- An intentionally invalid config sample fails validation.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_family_config.py -v
python -c "from src.plugin_examples.family_config.loader import load_family_config; load_family_config('configs/families/cells.yml')"
```

**Failure Handling:**
- If schema tool (e.g., `jsonschema`) is unavailable, add to `pyproject.toml` dependencies before re-running.

**Evidence Files:**
- `schemas/family-config.schema.json`
- `configs/families/cells.yml`
- `tests/unit/test_family_config.py`

---

### EPIC-03: NuGet Source of Truth

---

**Taskcard ID:** TC-03
**Title:** Build NuGet Fetcher
**Objective:** Download and cache official NuGet packages for configured families. Record version, hash, and provenance so the pipeline can detect package changes.

**Dependencies:** TC-02

**Inputs:**
- `configs/families/cells.yml`
- NuGet.org v3 API: `https://api.nuget.org/v3/index.json`

**Actions:**
1. Create `src/plugin_examples/nuget_fetcher/fetcher.py`.
   - Accept family config as input.
   - Resolve latest stable version from NuGet v3 registration endpoint.
   - Download `.nupkg` to deterministic cache path: `runs/{run_id}/packages/{family}/{package_id}.{version}.nupkg`.
   - Record SHA-256 hash of the downloaded file.
   - Record source URL.
   - Write `runs/{run_id}/packages/{family}/download-manifest.json`.
2. Create `src/plugin_examples/nuget_fetcher/cache.py`.
   - Check cache before re-download.
   - Return cached path and manifest if hash matches.
3. Write `manifests/package-lock.json` after each successful download.
4. Write `tests/unit/test_nuget_fetcher.py` covering:
   - Version resolution returns a semver string.
   - Download produces a file at expected path.
   - Hash is recorded.
   - Cache hit skips re-download.
   - Nonexistent package raises clear error.

**Outputs:**
- `src/plugin_examples/nuget_fetcher/fetcher.py`
- `src/plugin_examples/nuget_fetcher/cache.py`
- `runs/{run_id}/packages/cells/download-manifest.json`
- `manifests/package-lock.json`

**Acceptance Criteria:**
- Running fetcher for `Aspose.Cells` produces a `.nupkg` file at the expected path.
- `download-manifest.json` contains `package_id`, `version`, `sha256`, `source_url`, `cached_path`.
- Re-run uses cache (no HTTP request).
- `tests/unit/test_nuget_fetcher.py` passes (mock HTTP calls).

**Verification Commands:**
```bash
python -m pytest tests/unit/test_nuget_fetcher.py -v
python -c "from src.plugin_examples.nuget_fetcher.fetcher import fetch_package; fetch_package('configs/families/cells.yml', run_id='test-01')"
```

**Failure Handling:**
- If NuGet.org is unreachable, fail with clear network error. Do not silently use stale cache.
- If package does not exist, fail with package-not-found error. Do not continue pipeline.

**Evidence Files:**
- `runs/{run_id}/packages/cells/download-manifest.json`
- `manifests/package-lock.json`

---

**Taskcard ID:** TC-04
**Title:** Build NuGet Extractor
**Objective:** Extract DLL and XML documentation files from the downloaded `.nupkg`. Select target framework deterministically from family config preference list.

**Dependencies:** TC-03

**Inputs:**
- `.nupkg` file from TC-03
- `target_framework_preference` from family config

**Actions:**
1. Create `src/plugin_examples/nupkg_extractor/extractor.py`.
   - Unzip `.nupkg` to `runs/{run_id}/extracted/{family}/`.
   - Enumerate `lib/` folders.
   - Select framework using preference list from config (first match wins).
   - Locate `{package_id}.dll` in selected framework folder.
   - Locate `{package_id}.xml` in same folder.
   - If XML not found, write warning to `runs/{run_id}/extracted/{family}/warnings.json`. Do not fail silently.
   - Write `runs/{run_id}/extracted/{family}/extraction-manifest.json`.
2. Create `src/plugin_examples/nupkg_extractor/framework_selector.py`.
   - Implement preference-list framework selection.
   - Return selected framework and reason.
3. Write `tests/unit/test_nupkg_extractor.py` covering:
   - Framework is selected deterministically from preference list.
   - DLL path is recorded.
   - XML path is recorded when present.
   - Warning is written when XML is absent.
   - Missing DLL raises clear error.

**Outputs:**
- `src/plugin_examples/nupkg_extractor/extractor.py`
- `src/plugin_examples/nupkg_extractor/framework_selector.py`
- `runs/{run_id}/extracted/{family}/`
- `runs/{run_id}/extracted/{family}/extraction-manifest.json`

**Acceptance Criteria:**
- Extraction produces `extraction-manifest.json` with `dll_path`, `xml_path` (or null), `selected_framework`, `framework_selection_reason`.
- DLL is present at recorded path.
- `tests/unit/test_nupkg_extractor.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_nupkg_extractor.py -v
ls runs/test-01/extracted/cells/
cat runs/test-01/extracted/cells/extraction-manifest.json
```

**Failure Handling:**
- If no matching framework folder found, fail with explicit "no supported framework found" error. List available frameworks in error.

**Evidence Files:**
- `runs/{run_id}/extracted/{family}/extraction-manifest.json`

---

### EPIC-04: Reflection API Catalog

---

**Taskcard ID:** TC-05
**Title:** Build Reflection Catalog Generator
**Objective:** Generate a canonical JSON API catalog from the extracted DLL and XML. This catalog is the exclusive authority for what symbols may appear in generated examples.

**Dependencies:** TC-04

**Inputs:**
- `dll_path` from extraction-manifest.json (TC-04)
- `xml_path` from extraction-manifest.json (TC-04, may be null)

**Actions:**
1. Create `src/plugin_examples/reflection_catalog/reflector.py`.
   - Use `pythonnet` (`clr`) or a subprocess call to a small .NET reflector tool to load the DLL.
   - **Alternative (preferred for greenfield):** Build a small `dotnet-script` or C# console tool `tools/DllReflector/DllReflector.csproj` that:
     - Accepts DLL path + XML path as args.
     - Outputs JSON to stdout.
   - Reflect: public namespaces, public types (class/struct/enum/interface), public constructors, public methods (with signatures), public properties, public enums and values, `[Obsolete]` markers, assembly version, target framework.
   - Merge XML documentation summaries where available.
   - Mark all obsolete symbols.
2. Create `src/plugin_examples/reflection_catalog/catalog_builder.py`.
   - Build the structured catalog JSON from raw reflector output.
   - Validate against `schemas/api-catalog.schema.json`.
   - Write to `manifests/api-catalogs/{family}/{version}.json`.
3. Create `src/plugin_examples/reflection_catalog/schema_validator.py`.
   - Validate catalog JSON against schema.
   - Fail clearly on invalid catalog.
4. Create `schemas/api-catalog.schema.json`.
5. Create `tools/DllReflector/` .NET console project (if using .NET reflector approach).
6. Write `tests/unit/test_reflection_catalog.py` covering:
   - Catalog includes expected namespaces.
   - Catalog includes expected public types.
   - Obsolete members are marked.
   - Schema validation passes.
   - Catalog rejects invented symbols (cross-check test).

**Outputs:**
- `src/plugin_examples/reflection_catalog/`
- `schemas/api-catalog.schema.json`
- `manifests/api-catalogs/{family}/{version}.json`
- `tools/DllReflector/` (if .NET approach)

**Acceptance Criteria:**
- Catalog for Aspose.Cells includes at least one public namespace.
- Catalog schema validates.
- Catalog JSON is machine-readable with explicit type/member records.
- `tests/unit/test_reflection_catalog.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_reflection_catalog.py -v
cat manifests/api-catalogs/cells/{version}.json | python -m json.tool | head -50
```

**Failure Handling:**
- If DLL cannot be loaded, fail with explicit error. Do not proceed to generation with empty catalog.
- If XML is missing, log warning and continue with signatures only.

**Evidence Files:**
- `manifests/api-catalogs/{family}/{version}.json`

---

**Taskcard ID:** TC-06
**Title:** Build Plugin Namespace Detector
**Objective:** Determine whether a family's NuGet package exposes any configured plugin namespaces. Detection is based exclusively on the reflected DLL catalog — not DocFX, not documentation text.

**Dependencies:** TC-05

**Inputs:**
- `manifests/api-catalogs/{family}/{version}.json`
- `plugin_detection.namespace_patterns` from family config

**Actions:**
1. Create `src/plugin_examples/plugin_detector/detector.py`.
   - Load catalog namespaces.
   - Match against `namespace_patterns` (support glob-style `*` suffix).
   - Record matched namespaces with evidence (catalog path, catalog version).
   - Record non-matched patterns with reason.
   - Write `manifests/product-inventory.json` with eligible and skipped products.
2. Write `tests/unit/test_plugin_detector.py` covering:
   - Product with matching namespace is marked eligible.
   - Product without matching namespace is marked skipped.
   - DocFX-only namespace (not in catalog) is not accepted.
   - Detection evidence includes catalog path.

**Outputs:**
- `src/plugin_examples/plugin_detector/detector.py`
- `manifests/product-inventory.json`

**Acceptance Criteria:**
- If `Aspose.Cells.LowCode` is in the reflected catalog, Cells is marked eligible.
- If no configured namespace is found, product is marked skipped with reason.
- Evidence path to catalog is always included.
- `tests/unit/test_plugin_detector.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_plugin_detector.py -v
cat manifests/product-inventory.json | python -m json.tool
```

**Failure Handling:**
- If catalog is empty or missing, fail with explicit error. Do not mark product as skipped silently.

**Evidence Files:**
- `manifests/product-inventory.json`

---

### EPIC-05: API Delta and Monthly Change Model

---

**Taskcard ID:** TC-07
**Title:** Build API Delta Engine
**Objective:** Compare the current package API catalog against the previously accepted catalog to identify added, removed, and changed symbols. Map changes to impacted existing examples to drive delta-based regeneration.

**Dependencies:** TC-05, TC-06

**Inputs:**
- `manifests/api-catalogs/{family}/{version}.json` (current)
- `manifests/api-catalogs/{family}/{previous_version}.json` (previous, if exists)
- `manifests/example-index.json` (existing examples and their claimed symbols)

**Actions:**
1. Create `src/plugin_examples/api_delta/delta_engine.py`.
   - Compare namespaces, types, methods, properties, signatures.
   - Classify each symbol as: `added`, `removed`, `changed`, `unchanged`.
   - Detect signature changes (param count, param type, return type).
   - Detect obsolete additions.
2. Create `src/plugin_examples/api_delta/impact_mapper.py`.
   - Load example manifests.
   - Map impacted symbols to examples that claim them.
   - Mark examples as: `needs_regeneration`, `needs_repair`, `unaffected`.
3. Write delta report to `verification/latest/api-delta-report.json`.
4. Write impact report to `verification/latest/example-impact-report.json`.
5. Write `tests/unit/test_api_delta.py`.

**Outputs:**
- `src/plugin_examples/api_delta/`
- `verification/latest/api-delta-report.json`
- `verification/latest/example-impact-report.json`

**Acceptance Criteria:**
- Added symbols appear in `added` list.
- Removed symbols appear in `removed` list with last-seen version.
- Changed signatures appear in `changed` list with old and new signature.
- Impacted examples are identified correctly.
- Unchanged examples are not flagged for regeneration.
- On first run (no previous catalog), all symbols are treated as `added`.
- `tests/unit/test_api_delta.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_api_delta.py -v
cat verification/latest/api-delta-report.json | python -m json.tool
```

**Failure Handling:**
- If previous catalog is missing (first run), treat all current symbols as new. Log as "initial run, full catalog".

**Evidence Files:**
- `verification/latest/api-delta-report.json`
- `verification/latest/example-impact-report.json`

---

### EPIC-06: Fixture and Existing Example Registry

---

**Taskcard ID:** TC-08
**Title:** Build Fixture Registry
**Objective:** Discover, index, and normalize fixture files from all configured sources. Every executable example must have a registered fixture or an approved self-generated input strategy.

**Dependencies:** TC-02

**Inputs:**
- `fixtures.sources` from family config
- GitHub API (for remote fixture discovery)

**Actions:**
1. Create `src/plugin_examples/fixture_registry/registry.py`.
   - For each source in `fixtures.sources`:
     - If `type: github`, fetch file listing from GitHub API.
     - If `type: local`, scan local path.
   - Index each fixture: family, format (extension), path, repo, branch, provenance.
   - Classify suitability: `suitable`, `too_large`, `binary_unknown`, `format_mismatch`.
   - Write `manifests/fixture-registry.json`.
2. Create `src/plugin_examples/fixture_registry/fixture_fetcher.py`.
   - Download fixture files to `runs/{run_id}/fixtures/{family}/`.
   - Record download provenance in fixture-registry.
3. Write `tests/unit/test_fixture_registry.py`.

**Outputs:**
- `src/plugin_examples/fixture_registry/`
- `manifests/fixture-registry.json`
- `runs/{run_id}/fixtures/{family}/`

**Acceptance Criteria:**
- Registry includes at least one `.xlsx` fixture for Cells pilot.
- Every fixture has provenance (repo, branch, path, or local path).
- Missing-fixture scenarios are blocked with explicit reason — not silently skipped.
- `tests/unit/test_fixture_registry.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_fixture_registry.py -v
cat manifests/fixture-registry.json | python -m json.tool | head -30
```

**Failure Handling:**
- If GitHub API is rate-limited, fail with clear message. Do not silently use empty fixture list.
- If no suitable fixture found for a scenario format, block that scenario with explicit reason.

**Evidence Files:**
- `manifests/fixture-registry.json`

---

**Taskcard ID:** TC-09
**Title:** Mine Existing Examples
**Objective:** Index existing Aspose .NET examples from official repos. Validate their used symbols against the current reflection catalog. Classify as reusable, stale, or irrelevant.

**Dependencies:** TC-05, TC-08

**Inputs:**
- `existing_examples.sources` from family config
- `manifests/api-catalogs/{family}/{version}.json`

**Actions:**
1. Create `src/plugin_examples/example_miner/miner.py`.
   - Fetch C# example files from configured GitHub sources.
   - Detect LowCode/Plugin namespace usage (import statements, class instantiation patterns).
   - Extract fixture references (file paths in code).
   - Extract output format patterns.
2. Create `src/plugin_examples/example_miner/symbol_validator.py`.
   - For each mined example, extract used types and methods.
   - Cross-check against current API catalog.
   - Classify: `reusable` (all symbols valid), `stale` (some symbols missing or changed), `irrelevant` (no plugin namespace usage).
3. Write `manifests/existing-examples-index.json`.
4. Write `verification/latest/stale-existing-examples.json`.
5. Write `tests/unit/test_example_miner.py`.

**Outputs:**
- `src/plugin_examples/example_miner/`
- `manifests/existing-examples-index.json`
- `verification/latest/stale-existing-examples.json`

**Acceptance Criteria:**
- All mined examples have classification.
- Stale examples list their missing or changed symbols.
- No example is blindly trusted — all pass through symbol validation.
- `tests/unit/test_example_miner.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_example_miner.py -v
cat manifests/existing-examples-index.json | python -m json.tool | head -30
```

**Failure Handling:**
- If official examples repo is unavailable, log warning and continue with empty mined set. Scenarios may still be generated from catalog alone.

**Evidence Files:**
- `manifests/existing-examples-index.json`
- `verification/latest/stale-existing-examples.json`

---

### EPIC-07: Scenario Planning

---

**Taskcard ID:** TC-10
**Title:** Build Scenario Catalog
**Objective:** Create a machine-readable catalog of plugin example scenarios derived exclusively from the reflected API and confirmed fixtures. Every scenario must have symbols, fixture strategy, expected output, and validation plan before it enters generation.

**Dependencies:** TC-06, TC-08, TC-09

**Inputs:**
- `manifests/api-catalogs/{family}/{version}.json`
- `manifests/fixture-registry.json`
- `manifests/existing-examples-index.json`
- `plugin_detection` results from TC-06

**Actions:**
1. Create `src/plugin_examples/scenario_planner/planner.py`.
   - Identify plugin API entrypoints (top-level LowCode/Plugin static methods or factory classes).
   - Group by: input format, output format, transformation type.
   - For each group, create scenario candidates.
   - Attach: required symbols (from catalog), fixture candidate, expected output format, expected output checks.
   - Assign status: `ready` (all required info present), `blocked` (missing fixture, missing output strategy, or ambiguous API).
2. Create `src/plugin_examples/scenario_planner/scenario_catalog.py`.
   - Write `manifests/scenario-catalog.json`.
   - Write `verification/latest/blocked-scenarios.json` with explicit block reasons.
3. Create `schemas/scenario.schema.json`.
4. Write `tests/unit/test_scenario_planner.py`.

**Outputs:**
- `src/plugin_examples/scenario_planner/`
- `schemas/scenario.schema.json`
- `manifests/scenario-catalog.json`
- `verification/latest/blocked-scenarios.json`

**Acceptance Criteria:**
- For Cells pilot: at least 3 `ready` scenarios if LowCode API is present.
- Every `ready` scenario has: scenario_id, family, namespace, entrypoint, required_symbols, fixture_path, expected_output_format, expected_output_checks, validation_plan.
- Every `blocked` scenario has explicit reason.
- No scenario uses symbols not in the API catalog.
- `tests/unit/test_scenario_planner.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_scenario_planner.py -v
cat manifests/scenario-catalog.json | python -m json.tool | head -50
cat verification/latest/blocked-scenarios.json | python -m json.tool
```

**Failure Handling:**
- If fewer than `min_examples_per_family` ready scenarios exist, write blocked report and halt generation. Report to human.

**Evidence Files:**
- `manifests/scenario-catalog.json`
- `verification/latest/blocked-scenarios.json`

---

### EPIC-08: LLM Generation

---

**Taskcard ID:** TC-11
**Title:** Build LLM Router with Preflight
**Objective:** Implement a reliable LLM provider router supporting `llm.professionalize.com` and local Ollama. All providers must pass preflight before any generation task is attempted.

**Dependencies:** TC-02

**Inputs:**
- `configs/llm-routing.yml`

**Actions:**
1. Create `src/plugin_examples/llm_router/router.py`.
   - Read provider order from config.
   - Attempt providers in order.
   - On preflight failure, fall to next provider.
   - If all providers fail preflight, fail closed — no generation attempts.
2. Create `src/plugin_examples/llm_router/preflight.py`.
   - Check: endpoint reachable (HTTP GET).
   - Check: model available (list models endpoint).
   - Check: simple JSON response works (send `{"test": true}`, expect JSON back).
   - Check: structured output parseable.
   - Check: response within timeout.
   - Record: which checks passed/failed per provider.
3. Create `src/plugin_examples/llm_router/providers/professionalize.py`.
   - OpenAI-compatible client for `llm.professionalize.com`.
   - Read API key from environment variable `LLM_PROFESSIONALIZE_API_KEY`.
4. Create `src/plugin_examples/llm_router/providers/ollama.py`.
   - Ollama client using host from `OLLAMA_HOST` env var (default: `http://localhost:11434`).
5. Write `verification/latest/llm-preflight.json` after each preflight run.
6. Write `tests/unit/test_llm_router.py` covering:
   - Preflight success routes to first provider.
   - First provider failure falls to second.
   - All providers fail → fail closed.
   - Provider choice is recorded.

**Outputs:**
- `src/plugin_examples/llm_router/`
- `verification/latest/llm-preflight.json`

**Acceptance Criteria:**
- Router never calls a provider that failed preflight.
- Provider choice is recorded in preflight manifest.
- If all providers fail, generation halts with explicit error.
- `tests/unit/test_llm_router.py` passes (providers mocked).

**Verification Commands:**
```bash
python -m pytest tests/unit/test_llm_router.py -v
cat verification/latest/llm-preflight.json | python -m json.tool
```

**Failure Handling:**
- On all-provider preflight failure, write `verification/latest/llm-preflight.json` with failure reasons and halt.

**Evidence Files:**
- `verification/latest/llm-preflight.json`

---

**Taskcard ID:** TC-12
**Title:** Build Constrained Prompt Packet Builder
**Objective:** Build the structured context packet sent to the LLM for each generation task. The packet must contain only verified symbols from the reflection catalog. The LLM must not receive permission to invent APIs.

**Dependencies:** TC-10, TC-11

**Inputs:**
- Ready scenario from `manifests/scenario-catalog.json`
- `manifests/api-catalogs/{family}/{version}.json`
- Relevant existing examples (from TC-09, reusable classification only)
- Fixture metadata from `manifests/fixture-registry.json`

**Actions:**
1. Create `src/plugin_examples/generator/packet_builder.py`.
   - For each ready scenario, build a scenario packet.
   - Include: scenario metadata, allowed_symbols (from catalog only), fixture_metadata, style_hints (from reusable existing examples), output_requirements, forbidden_behaviors.
   - Forbidden behaviors to include in packet:
     - Do not use any namespace not in `allowed_symbols`.
     - Do not use any method not in `allowed_symbols`.
     - Do not invent overloads.
     - Do not use hardcoded absolute paths.
     - Do not use placeholder comments like `// TODO`.
     - Do not use `Console.ReadLine()` or interactive input.
   - Require structured output: JSON with `program_cs`, `csproj`, `readme`, `manifest`, `expected_output`, `claimed_symbols`.
2. Create `schemas/scenario-packet.schema.json`.
3. Create `schemas/example-manifest.schema.json`.
4. Write `prompts/example-generator.md` — the system prompt template.
5. Write `prompts/example-repair.md` — repair prompt template.
6. Write `tests/unit/test_packet_builder.py`.

**Outputs:**
- `src/plugin_examples/generator/packet_builder.py`
- `schemas/scenario-packet.schema.json`
- `schemas/example-manifest.schema.json`
- `prompts/example-generator.md`
- `prompts/example-repair.md`

**Acceptance Criteria:**
- Packet includes only symbols present in the API catalog.
- Packet rejects any attempt to include unknown symbols.
- LLM output schema requires `claimed_symbols` list.
- `tests/unit/test_packet_builder.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_packet_builder.py -v
python -c "from src.plugin_examples.generator.packet_builder import build_packet; import json; p = build_packet('scenario-id-01'); print(json.dumps(p, indent=2)[:500])"
```

**Failure Handling:**
- If a symbol in the scenario plan is not found in the catalog, reject the scenario and block it. Do not silently drop the symbol.

**Evidence Files:**
- `schemas/scenario-packet.schema.json`
- `schemas/example-manifest.schema.json`

---

**Taskcard ID:** TC-13
**Title:** Generate SDK-Style Console Example Projects
**Objective:** Use the LLM (via router) with the constrained packet to generate one SDK-style .NET console project per ready scenario. Each generated project must be complete, runnable, and free of placeholder code.

**Dependencies:** TC-12

**Inputs:**
- Scenario packets from TC-12
- LLM router from TC-11

**Actions:**
1. Create `src/plugin_examples/generator/code_generator.py`.
   - Send packet to LLM router.
   - Receive structured JSON response.
   - Validate response schema (required fields present).
   - Extract `program_cs`, `csproj`, `readme`, `manifest`, `expected_output`, `claimed_symbols`.
   - Reject response if:
     - Any `claimed_symbol` is not in the API catalog.
     - `program_cs` contains placeholder patterns (`// TODO`, `throw new NotImplementedException()`).
     - `program_cs` contains hardcoded absolute paths.
     - `csproj` references package versions inline (must use `Directory.Packages.props`).
2. Create `src/plugin_examples/generator/project_generator.py`.
   - Write files to `runs/{run_id}/generated/{family}/{namespace-group}/{scenario-slug}/`.
   - Generate `.csproj` from template.
   - Write `Program.cs`.
   - Write `README.md`.
   - Write `example.manifest.json`.
   - Write `expected-output.json`.
3. Create `src/plugin_examples/generator/manifest_writer.py`.
   - Maintain `manifests/example-index.json` with all generated examples and their claimed symbols.
4. Write `tests/unit/test_generator.py`.

**Outputs:**
- `src/plugin_examples/generator/`
- `runs/{run_id}/generated/{family}/{namespace-group}/{scenario-slug}/`
- Updated `manifests/example-index.json`

**Acceptance Criteria:**
- Generated `Program.cs` uses `AppContext.BaseDirectory`.
- Generated `Program.cs` checks output file exists and is non-empty.
- No placeholder code.
- All `claimed_symbols` present in API catalog.
- `csproj` uses no inline package versions.
- `tests/unit/test_generator.py` passes.

**Verification Commands:**
```bash
python -m pytest tests/unit/test_generator.py -v
ls runs/test-01/generated/cells/lowcode/
cat runs/test-01/generated/cells/lowcode/convert-xlsx-to-pdf/Program.cs
```

**Failure Handling:**
- If LLM output fails schema validation, retry once with `prompts/example-repair.md`. If second attempt fails, block the scenario with reason and continue.
- If claimed symbol not in catalog, block scenario immediately. Do not retry.

**Evidence Files:**
- `runs/{run_id}/generated/{family}/{namespace-group}/{scenario-slug}/example.manifest.json`
- `manifests/example-index.json`

---

### EPIC-09: Validation and Reviewer Integration

---

**Taskcard ID:** TC-14
**Title:** Build Local Validation Harness
**Objective:** Restore, build, run, and validate outputs for every generated example. Record stdout, stderr, exit codes, and artifact paths. Failures are linked to repair tasks.

**Dependencies:** TC-13

**Inputs:**
- Generated example projects from TC-13
- `expected-output.json` per example

**Actions:**
1. Create `src/plugin_examples/verifier_bridge/dotnet_runner.py`.
   - For each generated example project:
     - Run `dotnet restore {csproj}`.
     - On restore success: run `dotnet build --no-restore {csproj}`.
     - On build success: run `dotnet run --project {csproj}`.
     - Record: exit code, stdout, stderr, runtime duration.
     - Write per-example result to `runs/{run_id}/validation/{scenario-slug}/dotnet-result.json`.
2. Create `src/plugin_examples/verifier_bridge/output_validator.py`.
   - Load `expected-output.json` for the example.
   - Check expected output file exists at expected path.
   - Check output file is non-empty.
   - Check output file extension matches expected format.
   - Optional: attempt format-specific reopen (e.g., for XLSX, check it is a valid ZIP).
   - Write pass/fail to `runs/{run_id}/validation/{scenario-slug}/output-validation.json`.
3. Write `schemas/validation-result.schema.json`.
4. Aggregate all results to `verification/latest/validation-results.json`.
5. In the published examples repo:
   - Create `tests/Aspose.Plugins.Examples.SmokeTests/` project.
   - `ExampleDiscoveryTests.cs`: verify all `example.manifest.json` files are present and valid.
   - `ExampleExecutionTests.cs`: run each example and check exit code.
   - `OutputValidationTests.cs`: verify expected outputs exist and are non-empty.
6. Write `tests/integration/test_cells_pipeline.py` for end-to-end pipeline integration test.

**Outputs:**
- `src/plugin_examples/verifier_bridge/dotnet_runner.py`
- `src/plugin_examples/verifier_bridge/output_validator.py`
- `schemas/validation-result.schema.json`
- `runs/{run_id}/validation/{scenario-slug}/dotnet-result.json`
- `runs/{run_id}/validation/{scenario-slug}/output-validation.json`
- `verification/latest/validation-results.json`

**Acceptance Criteria:**
- Every accepted example: restore exit code 0, build exit code 0, run exit code 0.
- Every accepted example: expected output file exists and is non-empty.
- Validation result JSON matches schema.
- Failed examples are not promoted to PR — they are marked for repair.
- `tests/integration/test_cells_pipeline.py` passes against real Aspose.Cells NuGet package.

**Verification Commands:**
```bash
dotnet restore runs/test-01/generated/cells/lowcode/convert-xlsx-to-pdf/ConvertXlsxToPdf.csproj
dotnet build --no-restore runs/test-01/generated/cells/lowcode/convert-xlsx-to-pdf/ConvertXlsxToPdf.csproj
dotnet run --project runs/test-01/generated/cells/lowcode/convert-xlsx-to-pdf/ConvertXlsxToPdf.csproj
cat verification/latest/validation-results.json | python -m json.tool
python -m pytest tests/integration/test_cells_pipeline.py -v
```

**Failure Handling:**
- On restore failure: record error, skip build and run for this example. Mark for repair.
- On build failure: attempt LLM repair using `prompts/example-repair.md`. One repair attempt. On second failure, mark blocked with reason.
- On run failure: same repair loop.
- On output validation failure: mark blocked with reason.

**Evidence Files:**
- `verification/latest/validation-results.json`
- `runs/{run_id}/validation/{scenario-slug}/dotnet-result.json`

---

**Taskcard ID:** TC-15
**Title:** Integrate example-reviewer as Publishing Gate
**Objective:** Pass every validated example through the `example-reviewer` system before PR creation. This is a mandatory gate — no example publishes without reviewer approval.

**Dependencies:** TC-14

**Inputs:**
- Generated examples (passed TC-14 gates)
- Family config
- `manifests/api-catalogs/{family}/{version}.json`
- `example-reviewer` system at `https://github.com/babar-raza/example-reviewer`

**Actions:**
1. **Investigate** `example-reviewer` integration mode:
   - Check if it exposes a CLI.
   - Check if it exposes a Python API or module.
   - Check if it exposes an HTTP API.
   - Document findings in `docs/verifier-integration.md`.
2. Create `src/plugin_examples/verifier_bridge/bridge.py`.
   - Implement integration using the discovered mode (CLI subprocess preferred for isolation).
   - Pass: example path, family config path, API catalog path, fixture registry path.
   - Capture: reviewer verdict, reviewer errors, reviewer evidence.
3. Write `verification/latest/example-reviewer-results.json`.
4. Block PR creation if any example fails the reviewer gate.
5. Write `docs/verifier-integration.md` documenting integration mode, inputs, outputs, and failure handling.

**Outputs:**
- `src/plugin_examples/verifier_bridge/bridge.py`
- `docs/verifier-integration.md`
- `verification/latest/example-reviewer-results.json`

**Acceptance Criteria:**
- Every published example has a reviewer result entry.
- Reviewer pass is required — reviewer failure blocks PR.
- Integration mode is documented.
- Reviewer errors produce actionable failure messages.

**Verification Commands:**
```bash
# After reviewer integration is implemented:
python -c "from src.plugin_examples.verifier_bridge.bridge import run_reviewer; run_reviewer('runs/test-01/generated/cells/lowcode/convert-xlsx-to-pdf', 'configs/families/cells.yml')"
cat verification/latest/example-reviewer-results.json | python -m json.tool
```

**Failure Handling:**
- If reviewer is unreachable or crashes, fail the gate. Do not skip reviewer and publish anyway.
- If reviewer returns ambiguous result, treat as failure. Log full reviewer output.

**Evidence Files:**
- `docs/verifier-integration.md`
- `verification/latest/example-reviewer-results.json`

---

### EPIC-10: Publishing

---

**Taskcard ID:** TC-16
**Title:** Build GitHub Publisher
**Objective:** Open evidence-backed PRs to `aspose-plugins-examples-dotnet` when all gates pass. No direct push to `main`. PR must include generated examples and full evidence package.

**Dependencies:** TC-15

**Inputs:**
- Validated and reviewer-approved examples
- Full evidence package: validation results, reviewer results, delta report, fixture registry, example index
- `configs/github-publishing.yml`
- `GITHUB_TOKEN` environment variable

**Actions:**
1. Create `src/plugin_examples/publisher/publisher.py`.
   - Create branch: `pipeline/{run_id}/{family}`.
   - Commit generated examples to `examples/{family}/` folder structure.
   - Commit manifests update.
   - Commit verification evidence.
   - Open PR against `main`.
   - Attach PR summary with: run_id, family, examples added/updated, API version, gate results summary.
   - **Never push directly to `main`.**
2. Create `src/plugin_examples/publisher/pr_builder.py`.
   - Build PR body from evidence package.
   - Include checklist of passed gates.
   - Include link to each validation result.
   - Include API delta summary.
3. Implement `--dry-run` mode that writes PR content to `runs/{run_id}/pr-preview/` without making GitHub API calls.
4. Write `verification/latest/publishing-report.json`.
5. Write `tests/unit/test_publisher.py` (with GitHub API mocked).

**Outputs:**
- `src/plugin_examples/publisher/`
- GitHub PR (live) or `runs/{run_id}/pr-preview/` (dry-run)
- `verification/latest/publishing-report.json`

**Acceptance Criteria:**
- PR branch follows naming convention.
- PR body includes gate evidence checklist.
- No direct push to `main` is possible through this module.
- Failed validation blocks PR creation.
- `--dry-run` mode works without `GITHUB_TOKEN`.
- `tests/unit/test_publisher.py` passes (mocked).

**Verification Commands:**
```bash
python -m pytest tests/unit/test_publisher.py -v
# Dry-run:
python -m plugin_examples publish --family cells --run-id test-01 --dry-run
ls runs/test-01/pr-preview/
```

**Failure Handling:**
- If `GITHUB_TOKEN` is missing, fail with clear "credentials required" message. Suggest `--dry-run`.
- If PR already exists for this branch, update it rather than creating a duplicate.

**Evidence Files:**
- `verification/latest/publishing-report.json`
- `runs/{run_id}/pr-preview/pr-body.md` (dry-run)

---

### EPIC-11: Autonomous Monthly Runner

---

**Taskcard ID:** TC-17
**Title:** Implement Monthly Scheduled Pipeline Workflow
**Objective:** Automate the full pipeline on a monthly schedule. Run only delta-based regeneration — no blind full rebuild. Open PR only when all gates pass. Produce failure report when blocked.

**Dependencies:** TC-02 through TC-16 (all)

**Inputs:**
- All family configs
- Previous package-lock.json (for version comparison)
- Previous api-catalog index (for delta)
- `GITHUB_TOKEN`, `LLM_PROFESSIONALIZE_API_KEY` (from CI secrets)

**Actions:**
1. Create `src/plugin_examples/package_watcher/watcher.py`.
   - For each configured family: check current NuGet version vs `manifests/package-lock.json`.
   - Output: list of families with new package versions.
2. Create main pipeline entry point: `src/plugin_examples/__main__.py`.
   - Orchestrate all stages in order.
   - Respect `--family`, `--run-id`, `--dry-run`, `--skip-llm`, `--force-full` flags.
3. Create `.github/workflows/monthly-package-refresh.yml`:
   - Schedule: `cron: '0 6 1 * *'` (1st of each month, 06:00 UTC).
   - Trigger: also `workflow_dispatch` for manual runs.
   - Steps: checkout, setup Python, setup .NET, run pipeline for all families, upload artifacts, report status.
4. Create `.github/workflows/build-and-test.yml`:
   - Trigger: push to any branch, PR to main.
   - Steps: checkout, setup Python, setup .NET, run unit and integration tests.
5. Write `docs/monthly-runbook.md`.

**Outputs:**
- `src/plugin_examples/package_watcher/`
- `src/plugin_examples/__main__.py`
- `.github/workflows/monthly-package-refresh.yml`
- `.github/workflows/build-and-test.yml`
- `docs/monthly-runbook.md`
- `verification/latest/monthly-run-report.json`

**Acceptance Criteria:**
- If no package version changed, pipeline logs "no changes" and exits 0. No PR is created.
- If version changed, delta pipeline runs for affected families only.
- Failed gates produce `verification/latest/monthly-run-report.json` with actionable details.
- Passing run opens PR with full evidence.
- `workflow_dispatch` allows manual full run.

**Verification Commands:**
```bash
# Manual run test:
python -m plugin_examples --family cells --dry-run
cat verification/latest/monthly-run-report.json | python -m json.tool
# CI: push branch and observe build-and-test.yml run
```

**Failure Handling:**
- If pipeline fails mid-run, write partial evidence to `verification/latest/` before exiting.
- CI failure notifies via GitHub Actions default notification.

**Evidence Files:**
- `verification/latest/monthly-run-report.json`
- `.github/workflows/monthly-package-refresh.yml`

---

## 12. Verification Gates

Every accepted example must pass all applicable gates. Gates are ordered and sequential — a gate failure blocks all downstream gates for that example.

| Gate | Name | Pass Condition | Failure Action |
|---|---|---|---|
| Gate 1 | NuGet Package Retrieval | `.nupkg` downloaded, hash recorded | Halt pipeline, report error |
| Gate 2 | `.nupkg` Extraction | `lib/` folder found and extracted | Halt pipeline, report frameworks found |
| Gate 3 | DLL + XML Discovery | DLL found; XML found or warning written | Halt on missing DLL; warn on missing XML |
| Gate 4 | Reflection Catalog Generation | Catalog JSON written and schema-validates | Halt, log catalog error |
| Gate 5 | Plugin Namespace Detection | At least one configured namespace matched in reflected catalog | Mark product skipped, not failed |
| Gate 6 | API Delta Calculation | Delta report written; impact map complete | Halt, log delta error |
| Gate 7 | Fixture Registry Validation | At least one suitable fixture per expected format | Block affected scenarios with reason |
| Gate 8 | Scenario Validity | Scenario has symbols, fixture, output plan, all from catalog | Block scenario, record reason |
| Gate 9 | LLM Provider Preflight | At least one provider passes all preflight checks | Halt generation, log provider failures |
| Gate 10 | LLM Output Schema Validation | Response includes all required fields in correct types | Retry once with repair prompt, then block |
| Gate 11 | Unknown Symbol Rejection | All `claimed_symbols` present in API catalog | Block scenario immediately, no retry |
| Gate 12 | `dotnet restore` | Exit code 0 | Mark example for repair |
| Gate 13 | `dotnet build` | Exit code 0 | Attempt LLM repair, one retry |
| Gate 14 | `dotnet run` | Exit code 0 | Attempt LLM repair, one retry |
| Gate 15 | Output Validation | Expected output exists and is non-empty | Block example, record failure |
| Gate 16 | example-reviewer Validation | Reviewer returns pass verdict | Block example, preserve reviewer output |
| Gate 17 | PR Evidence Package | Evidence JSON files present for all gates | Block PR creation |
| Gate 18 | No Direct Push to Main | PR is branch-based, never direct main push | Hard block in publisher code |

---

## 13. Pilot Strategy

**Pilot product:** Aspose.Cells for .NET (`Aspose.Cells` NuGet package)

**Why Cells:**
- Has a known `Aspose.Cells.LowCode` namespace with conversion APIs.
- Strong conversion example history.
- Straightforward output validation (PDF, HTML, CSV).
- Existing examples and fixture data available in `aspose-cells/Aspose.Cells-for-.NET`.

**Pilot success criteria:**

| # | Criterion | Verified By |
|---|---|---|
| 1 | Family config created | `configs/families/cells.yml` validates |
| 2 | Latest Aspose.Cells NuGet resolved | `download-manifest.json` contains version |
| 3 | Package downloaded and hashed | `.nupkg` at expected path, SHA-256 recorded |
| 4 | DLL + XML extracted | `extraction-manifest.json` has `dll_path` |
| 5 | Reflection catalog generated | `manifests/api-catalogs/cells/{version}.json` present |
| 6 | Plugin namespace detected from reflected DLL | `manifests/product-inventory.json` marks cells eligible |
| 7 | Existing examples indexed | `manifests/existing-examples-index.json` present |
| 8 | Fixtures indexed | `manifests/fixture-registry.json` has at least one `.xlsx` |
| 9 | At least 3 scenarios planned | `manifests/scenario-catalog.json` has 3 ready scenarios |
| 10 | At least 3 examples generated | 3 folders in `runs/{id}/generated/cells/lowcode/` |
| 11 | All generated examples restore | All restore exit codes = 0 |
| 12 | All generated examples build | All build exit codes = 0 |
| 13 | At least 2 examples run with fixtures | At least 2 run exit codes = 0 |
| 14 | Outputs validated | At least 2 expected output files present and non-empty |
| 15 | example-reviewer gate passes | `verification/latest/example-reviewer-results.json` has pass verdicts |
| 16 | PR-ready evidence produced | `verification/latest/` has all required JSON files |
| 17 | Blocked scenarios documented | `verification/latest/blocked-scenarios.json` present |

---

## 14. Monthly Automation Model

```
1st of each month, 06:00 UTC
  │
  ▼
package_watcher: check NuGet versions vs package-lock.json
  │
  ├─ No changes → log "no changes" → exit 0 (no PR)
  │
  └─ Changed families →
        nuget_fetcher → nupkg_extractor → reflection_catalog
          │
          api_delta: compare to previous catalog
            │
            ├─ No impacted examples → log "API unchanged" → exit 0
            │
            └─ Impacted examples →
                  fixture_registry → example_miner → scenario_planner
                    │
                    llm_router (preflight)
                      │
                      generator (for new/changed scenarios only)
                        │
                        verifier_bridge (restore → build → run → output)
                          │
                          example-reviewer gate
                            │
                            ├─ All pass → publisher → GitHub PR
                            │
                            └─ Some fail → blocked-scenarios + failure report
                                          (no partial PR)
```

**Delta rules:**
- If a symbol in an existing example is removed or changed → that example needs_regeneration.
- If a new plugin symbol is added → new scenario may be planned.
- If no catalog changes → skip all generation for that family.
- Never regenerate unaffected examples.

---

## 15. example-reviewer Integration Model

`example-reviewer` is at `https://github.com/babar-raza/example-reviewer` (same owner as this repo).

**Known capabilities (from plan context):**
- Extracts C# examples, compiles and runs them against real NuGet packages.
- Applies deterministic and LLM-based fixes.
- Commits verified corrections.
- Verify → Fix → Verify loop.
- SQLite-backed auditable state.
- Services for: compilation, runtime execution, LLM service, API catalog lookup, fixture resolution, semantic signature, vector similarity, family configs.

**Integration approach:**
1. At TC-15 implementation time, clone and inspect `example-reviewer` to determine integration mode.
2. Priority order: Python module import > CLI subprocess > HTTP API.
3. Pass example path, family config, and API catalog as inputs.
4. Capture verdict as JSON.

**Do not duplicate:** compilation, runtime execution, or LLM fix logic from `example-reviewer`. Reuse it.

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
  checks:
    - endpoint_reachable
    - model_available
    - json_response
    - structured_response_parseable
    - timeout_within_limit
```

**LLM constraints (enforced in packet builder, not in LLM prompt alone):**
- Packet contains only symbols from the reflected API catalog.
- LLM output is schema-validated before any files are written.
- All `claimed_symbols` are cross-checked against the catalog after generation.
- Rejection happens in pipeline code, not in prompt instruction.

---

## 17. CI Model

### `build-and-test.yml` (this pipeline repo)

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

### `monthly-package-refresh.yml` (this pipeline repo)

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
          path: verification/latest/
```

### `build-and-verify.yml` (published examples repo)

Triggers: push to any branch, PR to main, monthly schedule.

```yaml
jobs:
  verify-examples:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '8.0.x' }
      - run: dotnet restore Aspose.Plugins.Examples.sln
      - run: dotnet build --no-restore Aspose.Plugins.Examples.sln
      - run: dotnet test tests/Aspose.Plugins.Examples.SmokeTests/
```

---

## 18. Risks and Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Aspose.Cells.LowCode not in shipped NuGet | Medium | High | Check at Gate 5; mark skipped; try other namespaces; report to human |
| R2 | XML documentation missing from NuGet | Medium | Medium | Log warning at Gate 3; proceed with signatures only; note in PR |
| R3 | `llm.professionalize.com` unreachable | Medium | High | Fallback to Ollama; fail closed if both unavailable |
| R4 | LLM generates invented symbols | High | High | Gate 11 hard-rejects unknown symbols; no retry on this failure |
| R5 | Generated example fails `dotnet build` | High | Medium | One LLM repair attempt; block on second failure |
| R6 | Fixture files unavailable from GitHub | Medium | Medium | Block affected scenarios; proceed with fixture-independent scenarios |
| R7 | `example-reviewer` integration mode unknown | Medium | Medium | Investigate at TC-15; plan for CLI subprocess fallback |
| R8 | Published examples repo does not exist | Low | High | Publisher creates it on first run with bootstrap mode |
| R9 | GitHub rate limits during fixture/example discovery | Medium | Low | Implement exponential backoff; cache responses |
| R10 | NuGet package format changes between versions | Low | High | Validate extraction at Gate 2; fail clearly with directory listing |
| R11 | Monthly run regenerates too many examples | Low | Medium | Delta engine (TC-07) is the hard gate; enforce `max_examples_per_monthly_run` |
| R12 | Reflection tool fails on new .NET target framework | Low | Medium | Framework selector (TC-04) iterates preference list; warn on unknown TFM |

---

## 19. Execution Order

### Wave 1 — Foundation (Prerequisite for everything)

```
TC-01: Discovery (COMPLETE)
TC-02: Family config schema + cells.yml
pyproject.toml, Python project scaffold
schemas/
```

### Wave 2 — Source of Truth Chain

```
TC-03: NuGet fetcher
TC-04: NuGet extractor
TC-05: Reflection catalog generator
TC-06: Plugin namespace detector
```

Wave 2 can be validated end-to-end on Aspose.Cells before proceeding.

### Wave 3 — Data Enrichment

```
TC-07: API delta engine
TC-08: Fixture registry
TC-09: Existing example miner
```

TC-07, TC-08, TC-09 are independent and can run in parallel.

### Wave 4 — Scenario Intelligence

```
TC-10: Scenario planner + catalog
```

Requires Wave 2 and Wave 3 complete.

### Wave 5 — Generation

```
TC-11: LLM router + preflight
TC-12: Constrained prompt packet builder
TC-13: Example project generator
```

TC-11 and TC-12 are independent. TC-13 requires both.

### Wave 6 — Validation

```
TC-14: Local validation harness (restore/build/run/output)
TC-15: example-reviewer integration
```

TC-14 must complete before TC-15.

### Wave 7 — Publishing and Automation

```
TC-16: GitHub publisher
TC-17: Monthly runner + CI workflows
```

TC-16 must complete before TC-17.

---

## 20. Definition of Done

The system is execution-ready when:

```
Given a configured Aspose .NET family,
the system can download the official NuGet package,
extract DLL and XML documentation,
build a reflection-backed API catalog,
detect plugin namespaces from the shipped assembly,
load family-specific fixture and example sources,
plan plugin scenarios only from verified symbols,
generate SDK-style runnable C# console examples,
validate them through restore, build, run, output checks, and example-reviewer,
and open an evidence-backed GitHub PR when all gates pass.
```

All 17 taskcards must have status COMPLETE.
All 18 gates must be enforced in code.
Pilot criteria (Section 13) must all pass with verified evidence.
No direct push to `main` is possible through any code path.

---

## 21. Evidence Outputs

At the end of a successful pipeline run, these files must exist:

```
runs/{run_id}/
  packages/{family}/
    download-manifest.json        ← Gate 1 evidence
  extracted/{family}/
    extraction-manifest.json      ← Gates 2, 3 evidence
  validation/{scenario-slug}/
    dotnet-result.json            ← Gates 12-14 evidence
    output-validation.json        ← Gate 15 evidence
  generated/{family}/{group}/{slug}/
    Program.cs
    {Scenario}.csproj
    README.md
    example.manifest.json
    expected-output.json

manifests/
  package-lock.json
  product-inventory.json          ← Gate 5 evidence
  api-catalogs/{family}/{version}.json   ← Gate 4 evidence
  scenario-catalog.json           ← Gate 8 evidence
  fixture-registry.json           ← Gate 7 evidence
  existing-examples-index.json
  example-index.json

verification/latest/
  api-delta-report.json           ← Gate 6 evidence
  example-impact-report.json
  llm-preflight.json              ← Gate 9 evidence
  validation-results.json         ← Gates 12-15 evidence
  example-reviewer-results.json   ← Gate 16 evidence
  blocked-scenarios.json
  rejected-scenarios.json
  stale-existing-examples.json
  publishing-report.json          ← Gate 17 evidence
  monthly-run-report.json
```

---

## 22. Open Questions

| # | Question | Impact | Resolution Path |
|---|---|---|---|
| OQ-1 | Does `Aspose.Cells` NuGet include `Aspose.Cells.LowCode` namespace? | High — determines pilot eligibility | Resolved by Gate 5 on first TC-03→TC-06 run |
| OQ-2 | What integration mode does `example-reviewer` support? | High — determines TC-15 implementation | Investigate `example-reviewer` repo at TC-15 start |
| OQ-3 | Is `llm.professionalize.com` OpenAI-compatible? What models are available? | High — determines LLM router provider config | Verify by preflight check at TC-11 run |
| OQ-4 | Should `pythonnet` or a .NET subprocess be used for reflection? | Medium — affects TC-05 implementation | Preference: .NET subprocess (DllReflector tool) for isolation |
| OQ-5 | Does `aspose-plugins-examples-dotnet` repo need to be created before first PR? | Medium — affects TC-16 | Publisher should create repo or guide human to create it |
| OQ-6 | What Ollama model should be used as default fallback? | Medium — affects generation quality | Config-driven; recommended: `codellama` or `llama3` |
| OQ-7 | Are Aspose.Cells fixtures available without authentication? | Medium — affects TC-08 | GitHub API for public repo contents requires no auth (rate-limited) |

---

## 23. Blockers

| # | Blocker | Severity | Unblocked By |
|---|---|---|---|
| B1 | `GITHUB_TOKEN` with write access to `aspose-plugins-examples-dotnet` not yet confirmed | Medium | Human provides token; `--dry-run` mode works without it |
| B2 | `LLM_PROFESSIONALIZE_API_KEY` not confirmed available | Medium | Ollama fallback available; human provides key for production |
| B3 | `aspose-plugins-examples-dotnet` repo may not exist yet | Low | Publisher bootstrap mode creates it or human creates it |
| B4 | `example-reviewer` integration mode unknown until repo is inspected | Medium | TC-15 first action is to inspect and document |

---

## 24. Recommended Next Execution Wave

**Wave 1 — Execute now (no secrets required):**

```bash
# 1. Create Python project scaffold
# 2. Create schemas/family-config.schema.json
# 3. Create configs/families/cells.yml
# 4. Implement src/plugin_examples/family_config/loader.py
# 5. Run: python -m pytest tests/unit/test_family_config.py

# Then immediately proceed to Wave 2:
# 6. Implement nuget_fetcher (TC-03)
# 7. Implement nupkg_extractor (TC-04)
# 8. Implement reflection_catalog (TC-05)
# 9. Implement plugin_detector (TC-06)
# 10. Validate full chain against Aspose.Cells
```

**Agent prompt for Wave 1 implementation:**

```
You are implementing Wave 1 of the Aspose .NET Plugin Example Generation Pipeline.

Repository: https://github.com/babar-raza/lowcode-example-generator
Plan: docs/plans/plugin-example-generation-execution-plan.md
Discovery: docs/discovery/current-state.md

This repo is fully greenfield. Your task is to implement TC-02 through TC-06.

Start with:
1. Create pyproject.toml with Python 3.12, dependencies: jsonschema, pyyaml, requests, pytest.
2. Create src/plugin_examples/ package structure.
3. Create schemas/family-config.schema.json (Section 9 of the plan).
4. Create configs/families/cells.yml (Section 9 of the plan).
5. Implement src/plugin_examples/family_config/loader.py.
6. Write tests/unit/test_family_config.py and verify it passes.
7. Implement src/plugin_examples/nuget_fetcher/fetcher.py and cache.py (TC-03).
8. Implement src/plugin_examples/nupkg_extractor/extractor.py and framework_selector.py (TC-04).
9. Implement src/plugin_examples/reflection_catalog/ using a .NET subprocess tool at tools/DllReflector/ (TC-05).
10. Implement src/plugin_examples/plugin_detector/detector.py (TC-06).
11. Run the full TC-03→TC-06 chain against Aspose.Cells and verify evidence files are produced.

Do not implement generation (TC-11 through TC-13) until TC-03→TC-06 chain produces valid evidence for Aspose.Cells.

Verification commands are in the plan under each taskcard.
Evidence files are listed per taskcard.
```

---

*Plan last updated: 2026-04-27. Re-run planning agent after any significant repo changes or discovery that contradicts findings in `docs/discovery/current-state.md`.*
