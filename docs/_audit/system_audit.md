# System Audit

Generated: 2026-05-11
Mode: documentation alignment audit. Codebase is the source of truth. Documentation was used only for inventory and coverage mapping.

## Product/System Purpose

The repository implements a Python package and CLI named `plugin-examples` for generating, validating, and publishing C# examples for Aspose .NET plugin/LowCode APIs. Evidence:

- Package name and console script: `pyproject.toml` (`project.name = "plugin-examples"`, `project.scripts.plugin-examples = "plugin_examples.__main__:main"`).
- CLI description: `src/plugin_examples/__main__.py` defines `Aspose .NET Plugin Example Generation Pipeline`.
- Pipeline orchestration: `src/plugin_examples/runner.py` has `run_pipeline(...)` and stage functions for config loading, NuGet fetch, extraction, reflection, detection, scenario planning, generation, validation, reviewer integration, and publishing.
- The .NET reflector executable is a C# project under `tools/DllReflector/DllReflector.csproj`; CI builds it in `.github/workflows/build-and-test.yml`.

## Component Map

| Component | Responsibility | Code evidence |
|---|---|---|
| CLI entry point | Defines commands, flags, metrics flags, and live publishing/merge safety checks | `src/plugin_examples/__main__.py`, especially `main()` and `_add_metrics_flags()` |
| Pipeline runner | Executes ordered stages, writes `pilot-report.json`, computes gate verdicts, promotes evidence | `src/plugin_examples/runner.py`, `STAGE_DEFINITIONS`, `HARD_STOP_STAGES`, `run_pipeline()` |
| Family config | Loads YAML family configs, rejects disabled configs, validates against schema, builds dataclasses | `src/plugin_examples/family_config/loader.py`, `validator.py`, `models.py`; schema `pipeline/schemas/family-config.schema.json` |
| NuGet fetch/dependency resolution | Resolves latest stable or pinned packages, downloads `.nupkg`, computes SHA, resolves transitive dependencies | `src/plugin_examples/nuget_fetcher/fetcher.py`, `dependency_resolver.py`, `cache.py` |
| Package extraction/framework selection | Extracts package DLL/XML and dependency DLLs, selects target framework by configured preference | `src/plugin_examples/nupkg_extractor/extractor.py`, `framework_selector.py` |
| Reflection catalog | Runs DllReflector and normalizes/validates API catalog JSON | `src/plugin_examples/reflection_catalog/reflector.py`, `catalog_builder.py`, `schema_validator.py`; `tools/DllReflector/Program.cs` |
| Plugin detection/source-of-truth proof | Detects configured namespace patterns and writes product inventory/source-of-truth proof; asserts eligibility | `src/plugin_examples/plugin_detector/detector.py`, `proof_reporter.py` |
| API delta and impact | Computes API changes and maps impact to example needs | `src/plugin_examples/api_delta/delta_engine.py`, `impact_mapper.py` |
| Fixture registry/factory | Inventories fixture files from GitHub/local cache and generates minimal fixtures for supported formats | `src/plugin_examples/fixture_registry/registry.py`, `fixture_fetcher.py`, `fixture_factory.py` |
| Existing example mining | Fetches C# examples and validates symbols against current reflected catalog | `src/plugin_examples/example_miner/miner.py`, `symbol_validator.py` |
| Scenario planner | Classifies types, scores entry points, builds scenario catalog, preserves blocked scenarios, validates catalog hash | `src/plugin_examples/scenario_planner/planner.py`, `type_classifier.py`, `entrypoint_scorer.py`, `consumer_mapper.py`, `scenario_catalog.py` |
| LLM router | Runs provider preflight and calls configured providers; supports environment-configured OpenAI-compatible and Ollama endpoints | `src/plugin_examples/llm_router/router.py`, `provider_policy.py`; config `pipeline/configs/llm-routing.yml` |
| Generator | Builds prompt packets, generates/validates code, creates SDK-style projects and manifests | `src/plugin_examples/generator/packet_builder.py`, `code_generator.py`, `project_generator.py`, `manifest_writer.py` |
| Validation/reviewer bridge | Runs `dotnet restore/build/run`, validates outputs semantically, probes and runs external `example-reviewer` | `src/plugin_examples/verifier_bridge/dotnet_runner.py`, `output_validator.py`, `reviewer_preflight.py`, `bridge.py` |
| Gates/lifecycle | Computes global and per-example verdicts, PR candidate manifest, lifecycle records, family backlog, run-to-run comparison | `src/plugin_examples/gates/evaluator.py`, `models.py`, `example_gates.py`, `example_lifecycle.py`, `evidence_completeness.py` |
| Publisher | Builds dry-run package/PR content, live GitHub PR creation, publish readiness, repo access, merge checks, README rendering/auditing | `src/plugin_examples/publisher/*.py` |
| Metrics | Builds metrics payloads, writes metrics evidence, optional POST with duplicate ledger | `src/plugin_examples/metrics/*.py`; config `pipeline/configs/metrics.yml` |
| Discovery/package watcher | Discovery-only sweeps and monthly update reports | `src/plugin_examples/discovery_sweep.py`, `src/plugin_examples/package_watcher/watcher.py` |
| Helper scripts | Pilot wrapper, published build regression, taskcard sync, queue/bundle utilities | `scripts/pilot_run.py`, `scripts/validate_published_examples_build.py`, `scripts/sync_taskcards.py`, others |

## Key Workflows

### Full family pipeline (`plugin-examples run`)

Code evidence: `src/plugin_examples/__main__.py` command `run`; `src/plugin_examples/runner.py` `run_pipeline()`.

1. Load `pipeline/configs/families/{family}.yml` or disabled fallback and reject `experimental` unless `--allow-experimental`; reject `discovery_only` for generation (`_stage_load_config`).
2. Resolve/download NuGet package according to `nuget.package_id`, `version_policy`, `pinned_version`, `allow_prerelease` (`_stage_nuget_fetch`).
3. Resolve dependencies when `nuget.dependency_resolution.enabled` is true (`_stage_dependency_resolution`).
4. Extract package DLL/XML and dependency DLLs using target framework preference (`_stage_extraction`).
5. Build reflected API catalog using DllReflector and namespace filter (`_stage_reflection`).
6. Detect plugin namespaces and write source-of-truth proof/product inventory; assert eligible (`_stage_plugin_detection`).
7. Compute API delta and impact report (`_stage_api_delta`, `_stage_impact_mapping`).
8. Build fixture registry and mine existing examples (`_stage_fixture_registry`, `_stage_example_mining`).
9. Classify types, map consumers, score entry points, validate catalog hash, write scenario/blocked-scenario evidence (`_stage_scenario_planning`).
10. Preflight LLM provider if applicable (`_stage_llm_preflight`).
11. Generate example projects and fixture evidence (`_stage_generation`).
12. Run validation and output validation (`_stage_validation`).
13. Run external reviewer preflight/reviewer (`_stage_reviewer`).
14. Publish dry-run/live package according to gate verdict and CLI mode (`_stage_publisher`).
15. Compute per-example gates, aggregate gates, PR candidate manifest, scenario feedback, lifecycle evidence, and optional run-to-run comparison (`run_pipeline()` post-stage block).
16. Write `workspace/runs/{run_id}/pilot-report.json`; optionally promote run evidence with `--promote-latest`.

Hard-stop stages are `load_config`, `nuget_fetch`, `dependency_resolution`, `extraction`, `reflection`, `plugin_detection`, and `scenario_planning` (`HARD_STOP_STAGES` in `runner.py`).

### Discovery-only workflow (`plugin-examples discover-lowcode`)

Code evidence: CLI parser in `src/plugin_examples/__main__.py`; implementation `src/plugin_examples/discovery_sweep.py`.

Inputs are `--all-families`, `--family`, `--families`, `--allow-experimental`, `--rank`, and `--promote-latest`. The workflow loads family configs, fetches/extracts/reflects packages, detects LowCode/plugin namespaces, writes source-of-truth proof evidence, and writes aggregate discovery evidence under `workspace/verification/latest/`.

### Publish PR workflow (`plugin-examples publish-pr`)

Code evidence: parser and command branch in `src/plugin_examples/__main__.py`; publishing modules in `src/plugin_examples/publisher/`.

Dry-run mode simulates PR creation and writes evidence. Live mode requires `--publish`, `GITHUB_TOKEN`, approval token `APPROVE_LIVE_PR` or `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`, publishable gate verdict, package path existence, repo access readiness, permission readiness, and branch not equal to target branch.

### Merge PR workflow (`plugin-examples merge-pr`)

Code evidence: `src/plugin_examples/__main__.py`, `src/plugin_examples/publisher/merge_approval_gate.py`, `github_pr_merger.py`.

Dry-run verifies merge preconditions. Live mode requires `GITHUB_TOKEN`, separate merge approval token `APPROVE_MERGE_PR` or `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL`, and explicitly rejects reuse of `APPROVE_LIVE_PR`.

### README workflows

Code evidence: `render-root-readme` and `publish-readme` command branches in `src/plugin_examples/__main__.py`; `publisher/readme_renderer.py`; `publisher/readme_auditor.py`.

`render-root-readme` renders and audits a package README into `workspace/pr-dry-run/.../README.md` and writes audit/render evidence. `publish-readme` creates a README-only PR or dry-run evidence after audit and approval checks.

### Monthly CI workflow

Code evidence: `.github/workflows/monthly-package-refresh.yml`.

Scheduled on the first day of each month at 06:00 UTC and manually dispatchable. It installs the package, builds DllReflector, runs `python -m plugin_examples run --family ...`, validates selected evidence tests, then runs published example build regression via `scripts/validate_published_examples_build.py`.

## Config Reference

### Family config files

Location: `pipeline/configs/families/*.yml`; disabled configs under `pipeline/configs/families/disabled/`; template under `_templates/family-template.yml`.

Loaded by `load_family_config()` in `src/plugin_examples/family_config/loader.py`; validated by `validate_family_config()` in `validator.py`; schema: `pipeline/schemas/family-config.schema.json`.

Top-level keys:

| Key | Default/validation | Evidence |
|---|---|---|
| `family` | required string | schema `required` |
| `display_name` | required string | schema `required` |
| `enabled` | required boolean; loader rejects false before full validation | `loader.py` `DisabledFamilyError` |
| `status` | enum `active`, `disabled`, `experimental`, `discovery_only` | schema and `runner._stage_load_config` |
| `nuget.package_id` | required string | schema |
| `nuget.version_policy` | enum `latest-stable`, `pinned` | schema |
| `nuget.pinned_version` | string or null | schema |
| `nuget.allow_prerelease` | default false | schema; family models |
| `nuget.target_framework_preference` | array, min 1 | schema |
| `nuget.dependency_resolution.enabled` | default true | schema |
| `nuget.dependency_resolution.max_depth` | default 2 | schema |
| `nuget.dependency_resolution.extra_packages` | optional array | schema; discovery sweep handles extra packages |
| `plugin_detection.namespace_patterns` | required non-empty array | schema; detector |
| `github.official_examples_repo` | owner/repo/branch required | schema |
| `github.published_plugin_examples_repo` | owner/repo/branch required | schema |
| `github.central_repo_allowed` | default false | schema; publisher central-repo guard |
| `fixtures.sources` | required array | schema; fixture registry |
| `existing_examples.sources` | required array | schema; example miner |
| `generation.min_examples_per_family` | required integer >= 1 | schema |
| `generation.max_examples_per_monthly_run` | required integer >= 1 | schema |
| `generation.allow_new_fixtures` | boolean | schema |
| `generation.allow_generated_input_files` | boolean, model default true | schema; `models.py` |
| `generation.allowed_types` | optional allowlist | schema; planner |
| `generation.preferred_methods_per_type` | optional map | schema; planner |
| `validation.require_restore/build/run/output_validation/example_reviewer` | booleans | schema; runner validation gates |
| `validation.runtime_runner` | enum `linux`, `windows`, `auto`; default `auto` | schema |
| `llm.provider_order` | required non-empty array | schema; LLM router |
| `template_hints.*` | optional defaults for template generation | schema; generator/readme renderer |

Pilot evidence: `pipeline/configs/families/cells.yml` includes `family: cells`, package `Aspose.Cells`, namespace patterns `Aspose.Cells.LowCode*` and `Aspose.Cells.Plugins*`, official examples repo `aspose-cells/Aspose.Cells-for-.NET`, published repo `aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples`, and LLM provider order `llm_professionalize`, `ollama`.

### Other config files

| File | Purpose | Code evidence |
|---|---|---|
| `pipeline/configs/llm-routing.yml` | Provider definitions, preflight prompt, env var names, retry/timeout | loaded/used by `src/plugin_examples/llm_router/router.py` |
| `pipeline/configs/metrics.yml` | Metrics enable/dry-run/strict defaults, family/product mapping, command/job mapping, status mapping, env var names, ledger path | `src/plugin_examples/metrics/config.py` |
| `pipeline/configs/plugin-namespace-patterns.yml` | Global namespace pattern config | present; family configs are used by runner |
| `pipeline/configs/verifier.yml` | Verifier config | present; verifier bridge code uses `EXAMPLE_REVIEWER_PATH` and command execution |
| `pipeline/configs/github-publishing.yml` | Publishing config | present; family configs carry target repos used by publisher |
| `pipeline/configs/denominators/*.json` | Family denominator models | tested by `tests/unit/test_denominator_model.py` |
| `pipeline/contracts/**/*.json` | Scenario contracts for specific examples/families | schemas include `scenario-contract.schema.json`; tests include `test_scenario_contracts.py` |

### Environment variables

| Variable | Purpose | Code evidence |
|---|---|---|
| `GITHUB_TOKEN` | Live publish/merge, repo access probes, published build regression | `src/plugin_examples/__main__.py`, `publisher/repo_access_resolver.py`, `scripts/validate_published_examples_build.py` |
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | Approval fallback for live PR creation | `publisher/approval_gate.py`, `__main__.py` |
| `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | Approval fallback for live merge | `publisher/merge_approval_gate.py`, `__main__.py` |
| `EXAMPLE_REVIEWER_PATH` | External reviewer repo/path | `verifier_bridge/reviewer_preflight.py`, `bridge.py` |
| `LLM_API_KEY`, `OPENAI_API_KEY` | LLM/OpenAI-compatible auth fallback | `llm_router/router.py` |
| `LLM_PROFESSIONALIZE_API_KEY`, `LLM_PROFESSIONALIZE_BASE_URL` | Configured provider env vars | `pipeline/configs/llm-routing.yml` |
| `GPT_OSS_API_KEY`, `GPT_OSS_ENDPOINT`, `GPT_OSS_MODEL` | GPT-OSS/OpenAI-compatible route | `llm_router/router.py` |
| `OLLAMA_HOST` | Ollama endpoint | `llm_router/router.py`, `llm-routing.yml` |
| `OPENAI_MODEL` | OpenAI-compatible default model override | `llm_router/router.py` |
| `AGENT_METRICS_ENABLED`, `AGENT_METRICS_DRY_RUN`, `AGENT_METRICS_STRICT`, `AGENT_METRICS_ENDPOINT`, `AGENT_METRICS_TOKEN`, `AGENT_METRICS_PRODUCTION_ENABLED` | Metrics enablement/posting/strictness/endpoint/token/production gating | `metrics/config.py`, `metrics/poster.py` |

## CLI/API Reference

Package script: `plugin-examples`; module invocation also works via `python -m plugin_examples` because `src/plugin_examples/__main__.py` exists.

Global flag: `--verbose` / `-v`.

Shared metrics flags on most commands: `--metrics`, `--metrics-post`, `--metrics-job-type`, `--metrics-strict`, `--metrics-force-repost`, `--metrics-config`.

| Command | Purpose | Key flags |
|---|---|---|
| `status` | Print implemented module list | none |
| `run` | Run full/tiered pipeline for one family | `--family`, `--dry-run`, `--template-mode`, `--skip-run`, `--require-llm`, `--require-validation`, `--require-reviewer`, `--publish`, `--approval-token`, `--tier 0..5`, `--promote-latest`, `--allow-experimental`, `--compare-run` |
| `discover-lowcode` | Discovery-only sweep | `--all-families`, `--family`, `--families`, `--dry-run`, `--promote-latest`, `--allow-experimental`, `--rank` |
| `validate-publish-targets` | Check publish readiness for family configs | `--families`, `--promote-latest` |
| `resolve-repo-access` | Read-only GitHub access probe | `--families`, `--promote-latest` |
| `probe-publish-permissions` | Read-only push permission probe | `--families`, `--dry-run`, `--promote-latest` |
| `publish-pr` | Simulate or create PR for verified package | `--family`, mutually exclusive `--dry-run`/`--publish`, `--approval-token`, `--promote-latest` |
| `merge-pr` | Simulate or perform PR merge | `--family`, `--pr-number`, mutually exclusive `--dry-run`/`--merge`, `--approval-token`, `--promote-latest` |
| `release-status` | Report release state from evidence | `--families`, `--promote-latest` |
| `render-root-readme` | Render/audit root README in package | `--family`, `--package-path`, `--promote-latest` |
| `publish-readme` | Simulate/create README-only PR | `--family`, `--publish`, `--approval-token`, `--promote-latest` |
| `sync-taskcard-docs` | Generate markdown taskcard matrix from JSON | `--promote-latest` no-op consistency flag |
| `check` | Package update check placeholder | `--family` |

Helper script CLIs:

- `scripts/pilot_run.py`: wraps `run_pipeline`; flags include `--family`, `--run-id`, `--dry-run`, `--skip-run/--no-skip-run`, `--build-only`, `--template-mode`, `--require-llm`, `--require-validation`, `--require-reviewer`, `--publish`, `--promote-latest`, `--clean-run-dir`, `--allow-cache-only`, `--tier`.
- `scripts/validate_published_examples_build.py`: validates published examples build; flags include output path and family selection (argparse evidence in file).
- `scripts/sync_taskcards.py`: `--check` verifies generated markdown matches JSON.

## Data Directories and File Contracts

| Path | Contract | Evidence |
|---|---|---|
| `pipeline/configs/families/` | Family YAML configs | loader and schema |
| `pipeline/schemas/` | JSON schemas for family config, API catalog, scenario, scenario packet, validation result, denominators, contracts | `pipeline/schemas/*.json` |
| `pipeline/contracts/{family}/` | Scenario contracts per generated example | `pipeline/contracts/**/*.json`; tested by `test_scenario_contracts.py` |
| `pipeline/prompts/` | Generator and repair prompt templates | files `example-generator.md`, `example-repair.md` |
| `templates/root-readme/` | Root README Jinja template | `publisher/readme_renderer.py` |
| `workspace/runs/{run_id}/` | Run-scoped output; includes `pilot-report.json`, generated projects, catalog, evidence | `runner.py` `run_dir` |
| `workspace/runs/{run_id}/evidence/latest/` | Canonical run-scoped evidence for a run | `runner.py`, `evidence_layout.py` |
| `workspace/verification/latest/families/{family}/` | Family-isolated promoted evidence | `evidence_layout.promote_family_evidence()` |
| `workspace/verification/latest/` | Global aggregate files and backward-compatible family aliases; alias is deprecated in code comments | `evidence_layout.py` |
| `workspace/manifests/` | Promoted manifest-like files | `runner.py` promotion block |
| `workspace/pr-dry-run/` | Dry-run PR package output | `publisher.py`, `__main__.py` publish/readme commands |
| `workspace/queues/` | Completion queue JSON | `scripts/patch_completion_queue.py` |
| `~/.cache/plugin-examples/fixture-listings` | Fixture listing cache | `fixture_registry/registry.py` |
| `workspace/verification/agent-metrics-post-ledger.jsonl` | Metrics duplicate-post ledger | `metrics/config.py`, `metrics/poster.py` |

Representative evidence files written by code include `catalog-hash-validation.json`, `fixture-strategy-plan.json`, `scenario-input-format-map.json`, `llm-fewshot-patterns.json`, `product-inventory.json`, `{family}-source-of-truth-proof.json`, `api-delta-report.json`, `example-impact-report.json`, `fixture-registry.json`, `existing-examples-index.json`, `stale-examples-report.json`, `scenario-catalog.json`, `blocked-scenarios.json`, `llm-preflight.json`, `example-index.json`, `validation-results.json`, `runtime-failure-classifications.json`, `reviewer-preflight.json`, `reviewer-results.json`, `publishing-report.json`, `example-gate-results.json`, `aggregate-gate-results.json`, `pr-candidate-manifest.json`, `scenario-feedback-updates.json`, `gate-results.json`, `example-lifecycle-records.json`, and `run-to-run-comparison.json`.

## Observability

- Python logging is configured in CLI via `logging.basicConfig(level=logging.DEBUG)` when `--verbose` is set, otherwise `INFO`.
- Modules use `logging.getLogger(__name__)` for stage/promotion/fetch messages and warnings (`runner.py`, `discovery_sweep.py`, `family_config/loader.py`, `evidence_layout.py`, fixture registry, etc.).
- User-facing command summaries and errors are printed by `src/plugin_examples/__main__.py`.
- Structured observability is primarily file evidence in `workspace/runs/{run_id}/pilot-report.json` and `workspace/runs/{run_id}/evidence/latest/*.json`.
- Metrics observability is optional and writes `llm-calls.jsonl`, `run-summary.json`, `metrics-payload.json`, validation/post result JSON, and POST ledger via `src/plugin_examples/metrics/evidence.py` and `poster.py`.

## Error Handling and Retry/Backoff

Evidenced behavior:

- Stage failures are captured by `_run_stage()` into `StageResult` with `status="failed"` and `error=str(e)`; hard-stop stages halt subsequent execution.
- Optional stages can degrade instead of failing the whole run: `llm_preflight` unless `require_llm`, `validation` unless `require_validation`, and `reviewer` unless `require_reviewer`.
- Disabled family configs raise `DisabledFamilyError`; experimental and discovery-only families are blocked for full generation unless the correct workflow/flag is used.
- Source-of-truth eligibility is enforced by `assert_source_of_truth_eligible()`.
- Live PR publishing requires approval token, GitHub token, publishable gates, repo access and permission evidence, and branch safety checks.
- Merge has a separate approval token and explicitly rejects PR approval token reuse.
- LLM config contains `max_retries`, but detailed retry implementation was not fully audited beyond code/config presence. Mark current retry/backoff semantics as Partial.

## Testing Strategy

How to run:

- Unit tests: `PYTHONPATH=src python -m pytest tests/unit -v --timeout=60` from `.github/workflows/build-and-test.yml`.
- Compile check: `python -m compileall src`.
- DllReflector build: `dotnet build tools/DllReflector/DllReflector.csproj -c Release`.
- Monthly evidence tests: `python -m pytest tests/unit/test_denominator_model.py tests/unit/test_scenario_contracts.py -q --tb=short`.

Coverage surfaces in tests:

- CLI defaults and runner behavior: `tests/unit/test_cli_defaults.py`, `test_runner.py`.
- Config/schema: `test_family_config.py`, `test_denominator_model.py`, `test_scenario_contracts.py`.
- NuGet/extraction/reflection/detection: `test_nuget_fetcher.py`, `test_dependency_resolver.py`, `test_nupkg_extractor.py`, `test_reflection_catalog.py`, `test_plugin_detector.py`.
- Planning/generation/validation: `test_scenario_planner.py`, `test_fixture_strategy.py`, `test_llm_generation.py`, `test_validation.py`.
- Gates/lifecycle/evidence: `test_gates.py`, `test_example_lifecycle.py`, `test_evidence_completeness.py`, `test_partial_success_partitioning.py`, `test_run_to_run_comparison.py`.
- Publishing/release/readme: `test_publishing.py`, `test_publishing_approval_gate.py`, `test_real_github_publisher.py`, `test_readme_renderer.py`, `test_release_status.py`, `test_merge_governance.py`.
- Metrics: `test_agent_metrics_*.py`.

No integration tests beyond `.gitkeep` were found under `tests/integration/`. Correctness is therefore mostly unit-tested plus CI build/compile/DllReflector checks and monthly workflow validation.

## External Integrations and Boundaries

| Integration | Direction | Boundary evidence |
|---|---|---|
| NuGet v3 | read/download packages | `nuget_fetcher/fetcher.py` |
| GitHub API | read examples/fixtures, repo access probes, live PR/merge | fixture registry, example miner, publisher modules, scripts |
| Aspose official examples repos | fixture discovery and example mining | family config `github.official_examples_repo`, fixture/example sources |
| Published plugin examples repos | PR targets and regression checks | family config `github.published_plugin_examples_repo`, publisher modules |
| DllReflector | local .NET executable for reflection | `reflection_catalog/reflector.py`, `tools/DllReflector/` |
| dotnet CLI | restore/build/run generated projects | `verifier_bridge/dotnet_runner.py` |
| example-reviewer | external validation tool | `EXAMPLE_REVIEWER_PATH`, `verifier_bridge/bridge.py`, `reviewer_preflight.py` |
| LLM providers | code generation via configured providers | `llm_router/router.py`, `pipeline/configs/llm-routing.yml` |
| Agent metrics endpoint | optional POST | `metrics/poster.py`, `pipeline/configs/metrics.yml` |

## Known Gaps/Risks

These are evidenced by code/docs inventory, not inferred features:

1. `docs/README.md` is absent, while the new root hygiene contract reserves docs root for that file only.
2. `docs/monthly-runbook.md` and `docs/verifier-integration.md` are root orphans.
3. `docs/plans/plugin-example-generation-execution-plan copy.md` duplicates the main execution plan.
4. The plan file contains historical current-state claims that conflict with implemented modules in `src/plugin_examples/`; it should not be treated as current code truth.
5. `tests/integration/` contains only `.gitkeep`; integration behavior relies on unit tests, CI workflows, and scripts.
6. `workspace/verification/latest/` remains a backward-compatible alias for family evidence; `evidence_layout.py` warns that family-scoped evidence should prefer `latest/families/{family}/`.
7. Retry/backoff semantics are only partially documented/audited. Config exposes provider retry counts, but the audit did not verify consistent retry/backoff handling across all external calls.
8. Several docs are dated preflight/result reports with no canonical consolidation, increasing scatter for operators and future LLMs.
