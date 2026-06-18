# System Audit

Audit date: 2026-05-30

Mode: code-first documentation alignment. The codebase is the source of truth for this audit. Documentation files were used only for inventory and coverage checks.

## Product/System Purpose

This repository implements the `plugin-examples` Python package and CLI for generating, validating, reviewing, and publishing SDK-style C# examples for Aspose .NET plugin/LowCode APIs.

Code evidence:

- `pyproject.toml` defines package `plugin-examples`, Python `>=3.12`, dependencies `jsonschema`, `Jinja2`, `pyyaml`, `requests`, and console script `plugin-examples = plugin_examples.__main__:main`.
- `src/plugin_examples/__main__.py` defines the CLI description as `Aspose .NET Plugin Example Generation Pipeline`.
- `src/plugin_examples/runner.py` defines `run_pipeline(...)` and a stage chain from config load through publisher.
- `tools/DllReflector/Program.cs` and `tools/DllReflector/DllReflector.csproj` are the .NET reflection utility used by `src/plugin_examples/reflection_catalog/reflector.py`.

Unverified or conflicting with governance:

- The repo governance requires all LLM calls to use only `https://llm.professionalize.com/v1/`. Current code does not fully enforce that contract: `src/plugin_examples/llm_router/router.py` approves provider families `{"llm_professionalize", "ollama"}`, returns an Ollama base URL for `ollama`, and contains OpenAI/gpt_oss call branches and defaults. This is an evidenced policy/code mismatch.

## Component Map

| Component | Responsibility | Code evidence |
|---|---|---|
| CLI | Defines top-level command parser, command flags, env checks, and command dispatch. | `src/plugin_examples/__main__.py`, `pyproject.toml` |
| Pipeline orchestrator | Runs ordered stages, manages run/evidence dirs, hard stops, replay, gate evaluation, promotion. | `src/plugin_examples/runner.py` (`PipelineContext`, `StageResult`, `STAGE_DEFINITIONS`, `run_pipeline`) |
| Family config | Loads YAML configs into typed dataclasses and validates against JSON schema. | `src/plugin_examples/family_config/models.py`, `src/plugin_examples/family_config/loader.py`, `src/plugin_examples/family_config/validator.py`, `pipeline/schemas/family-config.schema.json` |
| NuGet fetch/dependency resolution | Resolves packages, caches packages, writes package-lock/dependency manifests. | `src/plugin_examples/nuget_fetcher/fetcher.py`, `src/plugin_examples/nuget_fetcher/cache.py`, `src/plugin_examples/nuget_fetcher/dependency_resolver.py` |
| Nupkg extraction | Selects framework DLLs and extracts primary/dependency assemblies. | `src/plugin_examples/nupkg_extractor/extractor.py`, `src/plugin_examples/nupkg_extractor/framework_selector.py` |
| Reflection catalog | Builds API catalog from NuGet DLL and XML docs. | `src/plugin_examples/reflection_catalog/catalog_builder.py`, `src/plugin_examples/reflection_catalog/reflector.py`, `pipeline/schemas/api-catalog.schema.json`, `tools/DllReflector/Program.cs` |
| Plugin detector | Detects namespaces/types matching configured plugin namespace patterns and writes source-of-truth proof. | `src/plugin_examples/plugin_detector/detector.py`, `src/plugin_examples/plugin_detector/proof_reporter.py` |
| API delta and impact | Computes catalog deltas and impacted examples. | `src/plugin_examples/api_delta/delta_engine.py`, `src/plugin_examples/api_delta/impact_mapper.py` |
| Fixture registry | Discovers/creates input fixtures and writes fixture evidence. | `src/plugin_examples/fixture_registry/registry.py`, `src/plugin_examples/fixture_registry/fixture_factory.py` |
| Existing example miner | Mines official examples for style hints and stale reports. | `src/plugin_examples/example_miner/miner.py`, `src/plugin_examples/example_miner/symbol_validator.py` |
| Scenario planner | Classifies API types, builds scenarios, applies denominator/completeness rules. | `src/plugin_examples/scenario_planner/planner.py`, `scenario_catalog.py`, `type_classifier.py`, `entrypoint_scorer.py`, `consumer_mapper.py` |
| LLM router | Runs provider preflight and generation calls, writes LLM preflight evidence. | `src/plugin_examples/llm_router/router.py`, `pipeline/configs/llm-routing.yml` |
| Generator | Builds prompt packets and produces C# `Program.cs` examples through LLM or deterministic templates. | `src/plugin_examples/generator/packet_builder.py`, `src/plugin_examples/generator/code_generator.py` |
| Verification bridge | Runs `dotnet restore`, `dotnet build`, optional `dotnet run`, output validation, reviewer preflight/results. | `src/plugin_examples/verifier_bridge/dotnet_runner.py`, `output_validator.py`, `reviewer_preflight.py`, `bridge.py` |
| Gates | Evaluates stage, example, completeness, lifecycle, and publication gates. | `src/plugin_examples/gates/evaluator.py`, `example_gates.py`, `example_lifecycle.py`, `completeness_gate.py`, `publication_gate.py` |
| Publisher | Builds package/PR metadata, checks approvals/tokens/repo access, creates PRs and merges. | `src/plugin_examples/publisher/publisher.py`, `github_pr_publisher.py`, `github_pr_merger.py`, `approval_gate.py`, `merge_approval_gate.py`, `batch_publisher.py` |
| README tooling | Renders and audits generated root README files for target repos. | `src/plugin_examples/publisher/readme_renderer.py`, `readme_inventory.py`, `readme_auditor.py`, `readme_audit_gate.py` |
| Metrics | Collects and optionally posts agent metrics with ledger dedupe. | `src/plugin_examples/metrics/config.py`, `session.py`, `poster.py`, `models.py`, `pipeline/configs/metrics.yml` |
| Planner loop/portfolio actions | Computes next actions and runs safe action loops. | `src/plugin_examples/portfolio_action_planner.py`, `src/plugin_examples/planner_loop.py` |
| Package watcher | Watches versions and FormImporter defect status. | `src/plugin_examples/package_watcher/watcher.py`, `formimporter_watch.py` |
| Evidence validation | Validates sprint/report bundles and evidence contracts. | `src/plugin_examples/evidence_validator.py`, `evidence_contract.py`, `evidence_contract_computer.py` |

## Key Workflows

### Main Family Pipeline

Entry point: `plugin-examples run --family FAMILY`.

Code path:

1. CLI parses `run` flags in `src/plugin_examples/__main__.py`.
2. CLI calls `plugin_examples.runner.run_pipeline(...)`.
3. `run_pipeline` creates `workspace/runs/{run_id}/` and `workspace/runs/{run_id}/evidence/`.
4. `STAGE_DEFINITIONS` in `src/plugin_examples/runner.py` runs these stages in order: `load_config`, `nuget_fetch`, `version_drift_preflight`, `dependency_resolution`, `extraction`, `reflection`, `plugin_detection`, `api_delta`, `impact_mapping`, `fixture_registry`, `example_mining`, `scenario_planning`, `llm_preflight`, `generation`, `validation`, `reviewer`, `publisher`.
5. Hard-stop stages are defined in `HARD_STOP_STAGES`: `load_config`, `nuget_fetch`, `dependency_resolution`, `extraction`, `reflection`, `plugin_detection`, `scenario_planning`.
6. Gate evaluation writes example gates, aggregate gates, scenario feedback, lifecycle evidence, and gate results under the run evidence directory.
7. The run report is written to `workspace/runs/{run_id}/pilot-report.json`.
8. If `--promote-latest` is set, family evidence is promoted via `src/plugin_examples/evidence_layout.py` to `workspace/verification/latest/families/{family}/` and legacy `workspace/verification/latest/`.

### Discovery-Only Sweep

Entry point: `plugin-examples discover-lowcode`.

Code evidence:

- CLI command and flags are in `src/plugin_examples/__main__.py`.
- Implementation is in `src/plugin_examples/discovery_sweep.py`.
- It writes discovery evidence under `workspace/verification/latest/` and discovery run dirs under `workspace/runs/discovery-{family}-{timestamp}`.

### Publishing

Entry points:

- `plugin-examples publish-pr`
- `plugin-examples publish-pr-batch`
- `plugin-examples publish-readme`
- `plugin-examples merge-pr`

Code evidence:

- CLI command definitions are in `src/plugin_examples/__main__.py`.
- Live publish approval is enforced by `src/plugin_examples/publisher/approval_gate.py`, using token `APPROVE_LIVE_PR` and env fallback `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`.
- Merge approval is enforced by `src/plugin_examples/publisher/merge_approval_gate.py`, using token `APPROVE_MERGE_PR` and env fallback `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL`.
- GitHub PR creation uses `GITHUB_TOKEN` in `src/plugin_examples/publisher/github_pr_publisher.py`.
- GitHub merge uses `GITHUB_TOKEN` in `src/plugin_examples/publisher/github_pr_merger.py`.
- The publisher blocks live publishing when evidence or target config is missing in `src/plugin_examples/publisher/publisher.py`.

### README Rendering/Publishing

Entry points:

- `plugin-examples render-root-readme`
- `plugin-examples publish-readme`

Code evidence:

- Rendering context and template output are in `src/plugin_examples/publisher/readme_renderer.py`.
- Inventory extraction is in `src/plugin_examples/publisher/readme_inventory.py`.
- Audit rules are in `src/plugin_examples/publisher/readme_auditor.py`.
- README publish/audit approvals are in `src/plugin_examples/publisher/readme_audit_gate.py`.

### Metrics

Entry surface:

- Shared CLI flags: `--metrics`, `--metrics-post`, `--metrics-job-type`, `--metrics-strict`, `--metrics-force-repost`, `--metrics-config`.

Code evidence:

- Shared flag helper `_add_metrics_flags` and `_create_metrics_session` are in `src/plugin_examples/__main__.py`.
- Config loader and env overrides are in `src/plugin_examples/metrics/config.py`.
- Metrics config is `pipeline/configs/metrics.yml`.
- Post ledger default is `workspace/verification/agent-metrics-post-ledger.jsonl`.

## Config Reference

### Family Config Files

Location: `pipeline/configs/families/*.yml`.

Current family config files found:

`barcode.yml`, `cad.yml`, `cells.yml`, `diagram.yml`, `drawing.yml`, `email.yml`, `epub.yml`, `finance.yml`, `font.yml`, `gis.yml`, `html.yml`, `imaging.yml`, `note.yml`, `ocr.yml`, `omr.yml`, `page.yml`, `pdf.yml`, `psd.yml`, `slides.yml`, `svg.yml`, `tasks.yml`, `tex.yml`, `threed.yml`, `words.yml`, `zip.yml`.

Validation:

- Schema: `pipeline/schemas/family-config.schema.json`.
- Loader: `src/plugin_examples/family_config/loader.py`.
- Dataclasses/defaults: `src/plugin_examples/family_config/models.py`.
- Disabled families are rejected if the path includes `disabled`, if `enabled` is false, or if `status == disabled`.
- `run_pipeline` blocks `status == experimental` unless `--allow-experimental` is passed.
- `run_pipeline` blocks `status == discovery_only` for generation and tells operators to use `discover-lowcode`.

Core keys and defaults from code/schema:

| Key | Required | Default/behavior | Evidence |
|---|---:|---|---|
| `family` | yes | no default | `FamilyConfig`, schema |
| `display_name` | yes | no default | `FamilyConfig`, schema |
| `enabled` | yes | disabled if false | `load_family_config`, schema |
| `status` | yes | enum `active`, `disabled`, `experimental`, `discovery_only` | schema, `run_pipeline` |
| `nuget.package_id` | yes | no default | `NuGetConfig`, schema |
| `nuget.version_policy` | yes | enum `latest-stable`, `pinned` | schema |
| `nuget.pinned_version` | no | `None` | `NuGetConfig` |
| `nuget.allow_prerelease` | no | `False` | `NuGetConfig`, schema |
| `nuget.target_framework_preference` | no | `["netstandard2.0"]` | `NuGetConfig`, loader |
| `nuget.dependency_resolution.enabled` | no | `True` | `DependencyResolution`, loader |
| `nuget.dependency_resolution.max_depth` | no | `2` | `DependencyResolution`, loader |
| `nuget.dependency_resolution.extra_packages` | no | `[]` | `DependencyResolution`, loader |
| `nuget.dependency_resolution.include_all_tfm_groups` | no | `False` | `DependencyResolution`, loader |
| `plugin_detection.namespace_patterns` | yes | min 1 | schema |
| `github.official_examples_repo` | yes | `owner`, `repo`, `branch` required | schema |
| `github.published_plugin_examples_repo` | yes | `owner`, `repo`, `branch` required | schema |
| `github.central_repo_allowed` | no | `False` | `GitHubConfig`, schema |
| `fixtures.sources` | yes | list | schema, `FixturesConfig` |
| `existing_examples.sources` | yes | list | schema, `ExistingExamplesConfig` |
| `generation.min_examples_per_family` | yes | integer >= 1 | schema |
| `generation.max_examples_per_monthly_run` | yes | integer >= 1 | schema |
| `generation.allow_new_fixtures` | no | `True` | `GenerationConfig` |
| `generation.allow_generated_input_files` | no | `True` | `GenerationConfig` |
| `generation.allowed_types` | no | `[]` | `GenerationConfig`, schema |
| `generation.preferred_methods_per_type` | no | `{}` | `GenerationConfig`, schema |
| `validation.require_restore` | no | `True` | `ValidationConfig` |
| `validation.require_build` | no | `True` | `ValidationConfig` |
| `validation.require_run` | no | `True` | `ValidationConfig` |
| `validation.require_output_validation` | no | `True` | `ValidationConfig` |
| `validation.require_example_reviewer` | no | `True` | `ValidationConfig` |
| `validation.runtime_runner` | no | `auto`, enum `linux/windows/auto` | schema |
| `llm.provider_order` | yes | min 1 | schema |
| `template_hints.*` | no | default filenames/extensions/usings | `TemplateHints`, loader |
| `per_type_constraints` | no | `{}` | `FamilyConfig`, loader |

### Other Configs

| File | Purpose from code | Evidence |
|---|---|---|
| `pipeline/configs/metrics.yml` | Metrics mapping, allowed statuses/job types, env var names, ledger path. | `src/plugin_examples/metrics/config.py` |
| `pipeline/configs/llm-routing.yml` | Optional LLM provider config passed into router preflight. | `src/plugin_examples/runner.py`, `src/plugin_examples/llm_router/router.py` |
| `pipeline/configs/denominators/*.json` | Source version, catalog hash, denominator/completeness authority used during planning and status. | `src/plugin_examples/runner.py`, `src/plugin_examples/gates/completeness_gate.py`, `src/plugin_examples/publisher/release_status.py` |
| `pipeline/format-authority/contracts/*.json` | Format contracts consumed by planner/codegen/evidence. | `src/plugin_examples/format_authority/contracts.py`, `src/plugin_examples/runner.py` |
| `pipeline/prompts/example-generator.md` and `example-repair.md` | Prompt text used by generator packet/revision flow. | `src/plugin_examples/generator/packet_builder.py`, `code_generator.py` |

### Environment Variables

| Env var | Code behavior | Evidence |
|---|---|---|
| `GITHUB_TOKEN` | Required for live PR creation/merge and used by repo probes/fixture discovery. | `src/plugin_examples/__main__.py`, `publisher/github_pr_publisher.py`, `publisher/github_pr_merger.py`, `fixture_registry/registry.py` |
| `GH_TOKEN` | Fallback used by target repo health check; governance says operators map this to `GITHUB_TOKEN` before live commands. | `src/plugin_examples/publisher/target_repo_health.py` |
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | Fallback approval token for live publish; must be `APPROVE_LIVE_PR`. | `publisher/approval_gate.py`, `publisher/batch_publisher.py`, `__main__.py` |
| `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | Fallback approval token for merge; must be `APPROVE_MERGE_PR`. | `publisher/merge_approval_gate.py`, `__main__.py` |
| `PLUGIN_EXAMPLES_README_PUSH_APPROVAL` | README audit/push approval env var. | `publisher/readme_audit_gate.py` |
| `PLUGIN_EXAMPLES_README_AUDIT_APPROVAL` | README audit override token. | `publisher/readme_audit_gate.py` |
| `GPT_OSS_ENDPOINT` | Used by LLM router for `llm_professionalize` and `gpt_oss`; defaults vary in code. | `llm_router/router.py` |
| `GPT_OSS_MODEL` | Model name for `llm_professionalize`/`gpt_oss`, default `recommended`. | `llm_router/router.py` |
| `GPT_OSS_API_KEY` | API key for `llm_professionalize`/`gpt_oss`. | `llm_router/router.py` |
| `LLM_API_KEY`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `OLLAMA_HOST` | Still referenced in router code. | `llm_router/router.py` |
| `EXAMPLE_REVIEWER_PATH` | Optional reviewer executable/path discovery. | `verifier_bridge/reviewer_preflight.py`, `verifier_bridge/bridge.py` |
| `AGENT_METRICS_ENABLED` | Enables metrics without CLI flag when `true`. | `__main__.py`, `metrics/config.py` |
| `AGENT_METRICS_TOKEN` | Default metrics post token env var. | `metrics/config.py`, `metrics/poster.py`, `pipeline/configs/metrics.yml` |
| `AGENT_METRICS_ENDPOINT` | Overrides metrics API endpoint. | `metrics/config.py`, `pipeline/configs/metrics.yml` |
| `AGENT_METRICS_DRY_RUN` | If `false`, metrics dry-run is disabled. | `metrics/config.py` |
| `AGENT_METRICS_STRICT` | Enables strict metrics failure handling. | `metrics/config.py` |
| `AGENT_METRICS_PRODUCTION_ENABLED` | Single production metrics gate, true only when exactly `true`. | `metrics/config.py` |

## CLI/API Reference Extracted From Code

Top-level:

- `plugin-examples --verbose|-v`
- `plugin-examples status`

Commands:

| Command | Primary flags/options | Evidence |
|---|---|---|
| `run` | `--family`, `--dry-run`, `--template-mode`, `--skip-run`, `--require-llm`, `--require-validation`, `--require-reviewer`, `--publish`, `--approval-token`, `--tier 0..5`, `--promote-latest`, `--allow-experimental`, `--compare-run`, `--replay-from generation|validation|reviewer|publisher`, `--reuse-run`, metrics flags | `src/plugin_examples/__main__.py` |
| `discover-lowcode` | `--all-families`, `--family`, `--families`, `--dry-run`, `--promote-latest`, `--allow-experimental`, `--rank`, metrics flags | `__main__.py`, `discovery_sweep.py` |
| `validate-publish-targets` | `--families`, `--promote-latest`, metrics flags | `__main__.py`, `publisher/publish_readiness.py` |
| `resolve-repo-access` | `--families`, `--promote-latest`, metrics flags | `__main__.py`, `publisher/repo_access_resolver.py` |
| `probe-publish-permissions` | `--families`, `--dry-run`, `--promote-latest`, metrics flags | `__main__.py`, `publisher/publish_permission_probe.py` |
| `publish-pr` | `--family`, mutually exclusive `--dry-run`/`--publish`, `--approval-token`, `--package-path`, `--promote-latest`, metrics flags | `__main__.py`, `publisher/github_pr_publisher.py` |
| `merge-pr` | `--family`, `--pr-number`, mutually exclusive `--dry-run`/`--merge`, `--approval-token`, `--promote-latest`, metrics flags | `__main__.py`, `publisher/github_pr_merger.py` |
| `release-status` | `--families`, `--promote-latest`, `--validate-bundle`, metrics flags | `__main__.py`, `publisher/release_status.py` |
| `render-root-readme` | `--family`, `--package-path`, `--promote-latest`, `--cumulative`, metrics flags | `__main__.py`, `publisher/readme_renderer.py` |
| `publish-readme` | `--family`, `--publish`, `--approval-token`, `--promote-latest`, metrics flags | `__main__.py`, README publisher block in `__main__.py` |
| `sync-taskcard-docs` | `--promote-latest`, metrics flags | `__main__.py`, `scripts/sync_taskcards.py`, `scripts/write_taskcard_sync.py` |
| `check` | `--family` | `__main__.py` |
| `publish-pr-batch` | `--family`, mutually exclusive `--publish`/`--dry-run`, `--approval-token`, `--promote-latest` | `__main__.py`, `publisher/batch_publisher.py` |
| `formimporter-watch` | `--run-repro`, `--output` | `__main__.py`, `package_watcher/formimporter_watch.py` |
| `post-publication-verify` | `--family`, `--output` | `__main__.py`, `publisher/post_publication_verifier.py` |
| `version-drift` | `--family`, `--output`, `--json` | `__main__.py`, `publisher/version_drift_checker.py` |
| `target-repo-health` | `--family`, `--output`, `--json` | `__main__.py`, `publisher/target_repo_health.py` |
| `next-actions` | `--output`, `--markdown`, `--json` | `__main__.py`, `portfolio_action_planner.py` |
| `execute-next-actions` | `--max-cycles`, `--evidence-dir`, `--dry-run-remote`, `--json` | `__main__.py`, `planner_loop.py` |

Public Python surface:

- `plugin_examples.runner.run_pipeline(...)` is the main programmatic API.
- `plugin_examples.family_config.load_family_config(...)` loads and validates family configs.
- `plugin_examples.verifier_bridge.dotnet_runner.run_dotnet_validation(...)` runs restore/build/run.
- `plugin_examples.gates.evaluator.evaluate_gates(...)` produces `GateVerdict`.
- `plugin_examples.llm_router.router.LLMRouter` handles provider preflight and generation.

## Data Directories and File Contracts

| Path | Role | Code evidence |
|---|---|---|
| `pipeline/configs/families/*.yml` | Family input configs. | `family_config/loader.py`, schema |
| `pipeline/configs/denominators/*.json` | Denominator and catalog hash authority. | `runner.py`, `gates/completeness_gate.py`, `publisher/release_status.py` |
| `pipeline/schemas/*.schema.json` | JSON schemas for family config, catalog, scenario, scenario packet, manifest, denominator, validation result. | `pipeline/schemas/`, validators |
| `pipeline/format-authority/contracts/*.json` | Format contracts for products/families. | `format_authority/contracts.py` |
| `pipeline/prompts/*.md` | Prompt templates. | `generator/packet_builder.py`, `generator/code_generator.py` |
| `workspace/runs/{run_id}/` | Canonical run workspace. | `runner.py` |
| `workspace/runs/{run_id}/evidence/latest/` | Canonical run-scoped evidence files. | `runner.py`, stage writers |
| `workspace/runs/{run_id}/pilot-report.json` | Structured run report. | `runner.py` |
| `workspace/manifests/` | Promoted manifests such as `package-lock.json`, `fixture-registry.json`, `existing-examples-index.json`, `scenario-catalog.json`, `example-index.json`. | `runner.py`, `nuget_fetcher/dependency_resolver.py`, `fixture_registry/registry.py`, `example_miner/miner.py`, `scenario_planner/scenario_catalog.py` |
| `workspace/verification/latest/families/{family}/` | Family-scoped promoted evidence, preferred path. | `evidence_layout.py` |
| `workspace/verification/latest/` | Global and legacy compatibility evidence path. | `runner.py`, `evidence_layout.py` |
| `workspace/pr-dry-run/` | Dry-run publication package area. | `publisher/batch_publisher.py`, `publisher/readme_inventory.py`, `evidence_contract.py` |
| `reports/` | Sprint/system qualification/report bundles and generated-source artifacts. | `scripts/build_*`, `evidence_validator.py`, `reports/*` |

Important evidence filenames written by code include:

- `api-delta.json`
- `impact-report.json`
- `fixture-registry.json`
- `existing-examples-index.json`
- `stale-examples-report.json`
- `scenario-catalog.json`
- `blocked-scenarios.json`
- `catalog-hash-validation.json`
- `fixture-strategy-plan.json`
- `scenario-input-format-map.json`
- `llm-preflight.json`
- `example-index.json`
- `generated-fixtures.json`
- `validation-results.json`
- `output-validation.json`
- `reviewer-preflight.json`
- `reviewer-results.json`
- `publishing-report.json`
- `example-gate-results.json`
- `aggregate-gate-results.json`
- `scenario-feedback.json`
- `pr-candidate-manifest.json`
- `gate-results.json`
- `example-lifecycle.json`

## Observability

Logging:

- Modules create loggers with `logging.getLogger(__name__)`.
- CLI configures logging with `logging.basicConfig(level=logging.DEBUG)` when `--verbose` is passed, otherwise INFO.
- Stage failures are logged in `_run_stage` in `src/plugin_examples/runner.py`.

Metrics:

- Metrics are opt-in by CLI flags or `AGENT_METRICS_ENABLED=true`.
- Metrics evidence dir is created at `workspace/runs/metrics-{command}-{family|global}-{timestamp}/evidence` for non-run command sessions.
- Metrics posting uses `src/plugin_examples/metrics/poster.py`; ledger path defaults to `workspace/verification/agent-metrics-post-ledger.jsonl`.

Evidence:

- Most operational observability is file-based evidence under `workspace/runs/{run_id}/evidence/latest/` and promoted `workspace/verification/latest/`.
- Output validation and runtime failure classification are written by `verifier_bridge/output_validator.py` and `scenario_planner/runtime_feedback.py`.

## Error Handling and Retry/Backoff

Pipeline stage errors:

- `_run_stage` catches exceptions, records `StageResult(status="failed", error=str(e))`, and logs the failure.
- `run_pipeline` hard-stops only stages listed in `HARD_STOP_STAGES`; optional LLM/validation/reviewer failures can degrade depending on flags.

LLM retries:

- `_LLM_RETRY_BACKOFF_SECONDS = [30, 60]`.
- `_LLM_MAX_RETRIES = 2`.
- `_call_ollama` and `_call_openai_compatible` retry on timeout/connection errors and record metrics when a collector is present.

Dotnet runner:

- `run_dotnet_validation` stops after restore failure, then build failure, then run failure.
- `_run_dotnet` handles `subprocess.TimeoutExpired` and `FileNotFoundError`.

Publishing:

- Live publishing requires both `GITHUB_TOKEN` and approval token.
- Dry-run paths are used when live publish is not requested or blocked.
- Central/shared repo publishing is blocked unless `central_repo_allowed` is explicit.

## Testing Strategy

Test runner:

- `pyproject.toml` configures pytest with `testpaths = ["tests"]` and timeout 30.
- There are 101 unit test files under `tests/unit/`.

Command:

```powershell
python -m pytest
```

Focused test surfaces:

| Area | Evidence tests |
|---|---|
| CLI defaults and publish flag semantics | `tests/unit/test_cli_defaults.py` |
| Pipeline stage hard stops, tier limits, report fields, replay/drift | `tests/unit/test_runner.py`, `test_runner_contract_evidence.py`, `test_replay.py`, `test_run_to_run_comparison.py` |
| Family config schema/defaults | `tests/unit/test_family_config.py` |
| LLM router/provider policy/preflight | `tests/unit/test_llm_router_preflight.py`, `test_provider_policy.py`, `test_llm_generation.py` |
| NuGet/extraction/reflection | `test_nuget_fetcher.py`, `test_nupkg_extractor.py`, `test_nupkg_extractor_dll_fallback.py`, `test_reflection_catalog.py` |
| Planner/scenario contracts | `test_scenario_planner.py`, `test_scenario_contracts.py`, `test_planner_contract_consumption.py` |
| Gates/verdicts/lifecycle | `test_gates.py`, `test_gate_contract_validation.py`, `test_example_lifecycle.py`, `test_partial_success_partitioning.py` |
| Validation/output reviewer | `test_validation.py`, `test_gate_output_validation.py`, `test_reviewer_repair_loop.py`, `test_words_readiness_review.py` |
| Publishing/GitHub/readme | `test_publishing.py`, `test_real_github_publisher.py`, `test_publish_pr_readme_gate.py`, `test_readme_*`, `test_merge_governance.py` |
| Metrics | `test_agent_metrics_*.py`, `test_metrics_collector.py` |
| Evidence/contracts | `test_evidence_validator.py`, `test_evidence_contract.py`, `test_evidence_completeness.py` |

No tests were run during this audit; this artifact is an analysis deliverable only.

## Known Gaps/Risks

Each item below is backed by code evidence.

1. **LLM endpoint governance mismatch.** Governance requires only `https://llm.professionalize.com/v1/`; `src/plugin_examples/llm_router/router.py` still permits `ollama`, contains OpenAI/gpt_oss call branches, and has defaults to OpenAI or localhost URLs. Action: align router code, config, tests, and docs with the non-negotiable endpoint contract.
2. **Docs root currently clean, but root-orphan policy needs a standing check.** `Get-ChildItem docs -File` found only `docs/README.md`. There is no code gate found that enforces this root hygiene contract. Action: add a docs hygiene check if policy should be enforced continuously.
3. **CLI docs are at risk of drift.** CLI has many commands/flags in a single `__main__.py`; docs must be generated or checked against argparse definitions to stay current.
4. **Evidence path compatibility can confuse operators.** `src/plugin_examples/evidence_layout.py` writes both family-scoped primary evidence and legacy top-level aliases. Docs need to steer humans and LLMs to `workspace/verification/latest/families/{family}/`.
5. **Many report bundles exist under `reports/` and archived docs.** These are evidence/history, not active docs, but they can be mistaken for current guidance. Docs inventory should classify them as archive/report artifacts.
6. **Main CLI module is large.** `src/plugin_examples/__main__.py` contains argparse setup and substantial command implementation logic; documentation extraction must target code symbols rather than prose summaries.
7. **Generated code validation is partly rule-heavy and family-specific.** `src/plugin_examples/generator/code_generator.py` has extensive hardcoded PDF and constraints validation rules. Docs should avoid claiming generic behavior where code has family-specific checks.
8. **Live publish token handling relies on environment setup.** Code reads `GITHUB_TOKEN`; repo governance says map `GH_TOKEN` to `GITHUB_TOKEN` before live commands. Docs should keep that operational distinction explicit.
9. **Metrics config maps only some families.** `pipeline/configs/metrics.yml` maps `cells`, `words`, and `pdf`; many family configs exist. Docs should not imply all families are metrics-mapped unless code/config is expanded.
10. **Reports and workspace outputs are extensive.** Evidence validators reference many report bundle contracts. Docs need a concise active path guide to prevent operators from using stale sprint artifacts as source of truth.
