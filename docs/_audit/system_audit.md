# System Audit

Audit mode: codebase is the source of truth. Documentation was used only for inventory and coverage checks.

Last refreshed: 2026-05-26.

## Product/System Purpose

The repository implements a Python package named `plugin-examples` that generates, validates, reviews, and prepares PR publication for Aspose .NET plugin/LowCode example projects.

Evidence:

- Console script: `pyproject.toml` defines `plugin-examples = "plugin_examples.__main__:main"`.
- CLI parser entry: `src/plugin_examples/__main__.py:93-98`.
- Pipeline orchestrator: `src/plugin_examples/runner.py:1537`.
- Run directories and evidence are local `workspace/` outputs: `src/plugin_examples/runner.py:1570-1576`.
- Publishing code is PR-based and guarded by publisher modules: `src/plugin_examples/publisher/publisher.py`, `src/plugin_examples/publisher/github_pr_publisher.py`, `src/plugin_examples/publisher/github_pr_merger.py`.

## Component Map

| Component | Responsibility | Code evidence |
|---|---|---|
| `src/plugin_examples/__main__.py` | CLI entry point, command parsing, command dispatch, command-scoped metrics setup | `src/plugin_examples/__main__.py:93-98`, `src/plugin_examples/__main__.py:103-496` |
| `src/plugin_examples/runner.py` | Gate-driven pipeline orchestration, stage execution, run report, evidence promotion | `src/plugin_examples/runner.py:1510-1537`, `src/plugin_examples/runner.py:1570-1900` |
| `family_config` | YAML family config loading, JSON-schema validation, dataclass model construction | `src/plugin_examples/family_config/loader.py`, `src/plugin_examples/family_config/models.py`, `src/plugin_examples/family_config/validator.py` |
| `nuget_fetcher` | NuGet service access, package download/cache, dependency resolution, lock/manifest writing | `src/plugin_examples/nuget_fetcher/fetcher.py`, `src/plugin_examples/nuget_fetcher/dependency_resolver.py` |
| `nupkg_extractor` | Extracts assemblies/XML from NuGet packages and dependencies | Used by `src/plugin_examples/runner.py:426-444` |
| `reflection_catalog` | Builds reflected API catalog from selected assemblies | Used by `src/plugin_examples/runner.py:448-465` |
| `plugin_detector` | Detects plugin namespaces and writes source-of-truth/product inventory evidence | Used by `src/plugin_examples/runner.py:468-515` |
| `api_delta` | Computes API deltas and impact mapping | Used by `src/plugin_examples/runner.py:517-534` |
| `fixture_registry` | Discovers configured fixtures and writes registry evidence | Used by `src/plugin_examples/runner.py:536-546` |
| `example_miner` | Mines existing example repos for style/fixture signals | Used by `src/plugin_examples/runner.py:548-556` |
| `scenario_planner` | Builds ready/blocked scenarios from catalog, contracts, fixtures, constraints, and feedback | Used by `src/plugin_examples/runner.py:558-683` |
| `llm_router` | Provider preflight, approved-provider checks, LLM calls, retries, metrics hooks | `src/plugin_examples/llm_router/router.py:18`, `src/plugin_examples/llm_router/router.py:173-175`, `src/plugin_examples/llm_router/router.py:229-320`, `src/plugin_examples/llm_router/router.py:362`, `src/plugin_examples/llm_router/router.py:445` |
| `generator` | Builds packets, code, projects, manifests, expected-output files, and generated fixtures | Used by `src/plugin_examples/runner.py:705-872` |
| `verifier_bridge` | Runs dotnet restore/build/run, validates stdout/files, runs external reviewer | Used by `src/plugin_examples/runner.py:874-1261`; modules under `src/plugin_examples/verifier_bridge/` |
| `gates` | Per-example gates, aggregate gates, lifecycle, publication gate, evidence writers | Used by `src/plugin_examples/runner.py:1780-1837`; modules under `src/plugin_examples/gates/` |
| `publisher` | Publish readiness, repo access, permission probes, PR creation, merge, README publishing, release status | `src/plugin_examples/__main__.py:180-456`, modules under `src/plugin_examples/publisher/` |
| `metrics` | Metrics config, command/pipeline sessions, payload validation, evidence, POST ledger | `src/plugin_examples/__main__.py:10-90`, `src/plugin_examples/metrics/config.py:13-167`, `src/plugin_examples/metrics/poster.py:60-152` |
| `package_watcher` | FormImporter package/defect watch command | `src/plugin_examples/__main__.py:401-410`, `src/plugin_examples/package_watcher/formimporter_watch.py` |
| `tools/DllReflector` | .NET reflection helper executable project | `tools/DllReflector/Program.cs`, `tools/DllReflector/DllReflector.csproj` |
| `scripts/sync_taskcards.py` | Regenerates taskcard markdown from JSON evidence | `scripts/sync_taskcards.py:2`, `scripts/sync_taskcards.py:21-22` |

## Key Workflows

### Family Pipeline: `plugin-examples run`

1. CLI parses `run` flags: `src/plugin_examples/__main__.py:106-159`.
2. `run_pipeline()` creates `workspace/runs/{run_id}` and `workspace/runs/{run_id}/evidence`: `src/plugin_examples/runner.py:1570-1576`.
3. Config is loaded from `pipeline/configs/families/{family}.yml`, with disabled fallback and status gates: `src/plugin_examples/runner.py:299-333`.
4. NuGet package is fetched and cached in the run directory: `src/plugin_examples/runner.py:335-349`.
5. Version drift compares fetched version with denominator source version: `src/plugin_examples/runner.py:351-400`.
6. Dependencies are resolved when enabled: `src/plugin_examples/runner.py:402-424`.
7. Package assemblies/XML are extracted and reflected to `api-catalog.json`: `src/plugin_examples/runner.py:426-465`.
8. Plugin namespaces are detected and source-of-truth evidence is written: `src/plugin_examples/runner.py:468-515`.
9. API delta, impact mapping, fixture registry, example mining, and scenario planning run before generation: `src/plugin_examples/runner.py:517-683`.
10. LLM preflight runs before generation: `src/plugin_examples/runner.py:685-703`.
11. Generation writes projects under `workspace/runs/{run_id}/generated/{family}`: `src/plugin_examples/runner.py:705-872`.
12. Validation restores/builds/runs projects and writes validation evidence: `src/plugin_examples/runner.py:874-1259`.
13. Reviewer and publisher stages run after validation: `src/plugin_examples/runner.py:1261-1420`.
14. Per-example gates, aggregate gates, lifecycle evidence, and `pilot-report.json` are written: `src/plugin_examples/runner.py:1780-1889`.
15. `--promote-latest` copies evidence to `workspace/verification/latest/` and family-scoped locations: `src/plugin_examples/runner.py:1892-1900`.

Stage order is defined in `STAGE_DEFINITIONS`: `src/plugin_examples/runner.py:1510-1529`. Hard-stop stages are `load_config`, `nuget_fetch`, `dependency_resolution`, `extraction`, `reflection`, `plugin_detection`, and `scenario_planning`: `src/plugin_examples/runner.py:1532-1534`.

### Discovery Sweep

The `discover-lowcode` command is declared at `src/plugin_examples/__main__.py:162-176`. Discovery writes all-family evidence to `workspace/verification/latest/all-family-lowcode-discovery.json` and uses per-family discovery run directories under `workspace/runs/`.

### Publishing and Merge

Publishing and merge command surfaces:

- `validate-publish-targets`: `src/plugin_examples/__main__.py:180-191`
- `resolve-repo-access`: `src/plugin_examples/__main__.py:196-207`
- `probe-publish-permissions`: `src/plugin_examples/__main__.py:212-227`
- `publish-pr`: `src/plugin_examples/__main__.py:232-260`
- `merge-pr`: `src/plugin_examples/__main__.py:266-291`
- `release-status`: `src/plugin_examples/__main__.py:296-311`
- `render-root-readme`: `src/plugin_examples/__main__.py:319-334`
- `publish-readme`: `src/plugin_examples/__main__.py:340-355`
- `publish-pr-batch`: `src/plugin_examples/__main__.py:377-396`
- `post-publication-verify`: `src/plugin_examples/__main__.py:415-422`
- `version-drift`: `src/plugin_examples/__main__.py:426-440`
- `target-repo-health`: `src/plugin_examples/__main__.py:444-456`

Live PR creation requires `GITHUB_TOKEN` and approval token `APPROVE_LIVE_PR`. Merge requires separate token `APPROVE_MERGE_PR` and rejects the live-publish token. Evidence: `src/plugin_examples/publisher/approval_gate.py`, `src/plugin_examples/publisher/merge_approval_gate.py`, `src/plugin_examples/__main__.py:1049-1055`, `src/plugin_examples/__main__.py:1275-1315`.

### Taskcard Docs Sync

Taskcard JSON is read from `workspace/verification/latest/open-taskcard-closure-matrix.json` and rendered to `docs/development/open-taskcard-closure-matrix.md`.

Evidence:

- `scripts/sync_taskcards.py:2`
- `scripts/sync_taskcards.py:21-22`
- CLI help path: `src/plugin_examples/__main__.py:363`
- CLI output path: `src/plugin_examples/__main__.py:1507-1508`

### Metrics

Shared metrics flags are added by `_add_metrics_flags()`: `src/plugin_examples/__main__.py:10-23`. Metrics can be enabled by `--metrics` or `AGENT_METRICS_ENABLED=true`: `src/plugin_examples/__main__.py:34-42`.

Metrics evidence files:

- `agent-metrics-llm-calls.jsonl`: `src/plugin_examples/metrics/evidence.py:31`
- `agent-metrics-run-summary.json`: `src/plugin_examples/metrics/evidence.py:41`
- `agent-metrics-payload.json`: `src/plugin_examples/metrics/evidence.py:47`
- `agent-metrics-validation.json`: `src/plugin_examples/metrics/evidence.py:53`
- `agent-metrics-post-result.json`: `src/plugin_examples/metrics/evidence.py:59`

Metrics POST ledger path defaults to `workspace/verification/agent-metrics-post-ledger.jsonl`: `pipeline/configs/metrics.yml:94`, `src/plugin_examples/metrics/config.py:41`.

## Config Reference

### Family Configs

Loaded path:

- `pipeline/configs/families/{family}.yml`: `src/plugin_examples/runner.py:302`
- Disabled fallback path checked by runner: `src/plugin_examples/runner.py:304-307`
- Disabled path/field/status rejected by loader: `src/plugin_examples/family_config/loader.py`
- JSON schema: `pipeline/schemas/family-config.schema.json`
- Schema validation call: `src/plugin_examples/family_config/validator.py`

Typed model keys/defaults:

| Config surface | Evidence |
|---|---|
| `nuget.package_id`, `version_policy`, `pinned_version`, `allow_prerelease`, `target_framework_preference` default `["netstandard2.0"]` | `src/plugin_examples/family_config/models.py:23-33` |
| `nuget.dependency_resolution.enabled` default `true`, `max_depth` default `2`, `extra_packages` default `[]` | `src/plugin_examples/family_config/models.py:15-19` |
| `plugin_detection.namespace_patterns` | `src/plugin_examples/family_config/models.py:36-38` |
| `github.official_examples_repo`, `published_plugin_examples_repo`, `central_repo_allowed` default `false` | `src/plugin_examples/family_config/models.py:41-45` |
| `fixtures.sources`, `existing_examples.sources` | `src/plugin_examples/family_config/models.py:48-65` |
| `generation.min_examples_per_family`, `max_examples_per_monthly_run`, `allow_new_fixtures`, `allow_generated_input_files`, `allowed_types`, `preferred_methods_per_type` | `src/plugin_examples/family_config/models.py:68-75` |
| `validation.require_restore`, `require_build`, `require_run`, `require_output_validation`, `require_example_reviewer`, `runtime_runner` default `auto` | `src/plugin_examples/family_config/models.py:78-85` |
| `llm.provider_order` | `src/plugin_examples/family_config/models.py:88-90` |
| `template_hints` defaults | `src/plugin_examples/family_config/models.py:93-104` |
| `per_type_constraints` default `{}` | `src/plugin_examples/family_config/models.py:116` |

Other config/data inputs:

- `pipeline/configs/denominators/*.json`
- `pipeline/contracts/**/*.json`
- `pipeline/format-authority/manifest.json`
- `pipeline/format-authority/contracts/*.json`
- `pipeline/configs/metrics.yml`
- `pipeline/configs/llm-routing.yml`
- `pipeline/configs/plugin-namespace-patterns.yml`
- `pipeline/configs/verifier.yml`
- `pipeline/configs/github-publishing.yml`

### Environment Variables

| Variable | Code usage |
|---|---|
| `GITHUB_TOKEN` | PR creation/merge/probes and fixture/example repo access: `src/plugin_examples/__main__.py`, publisher modules, fixture/example modules |
| `GH_TOKEN` | Governance storage convention; code gap: `src/plugin_examples/publisher/target_repo_health.py` falls back to `GH_TOKEN` |
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | Live publish approval fallback: `src/plugin_examples/publisher/approval_gate.py` |
| `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | Merge approval fallback: `src/plugin_examples/publisher/merge_approval_gate.py` |
| `GPT_OSS_API_KEY` | LLM auth for professionalize/gpt_oss paths: `src/plugin_examples/llm_router/router.py:173` |
| `GPT_OSS_ENDPOINT` | LLM base URL; code still has non-governed defaults in some branches: `src/plugin_examples/llm_router/router.py:237`, `src/plugin_examples/llm_router/router.py:297`, `src/plugin_examples/llm_router/router.py:319` |
| `GPT_OSS_MODEL` | Model selection: `src/plugin_examples/llm_router/router.py:267`, `src/plugin_examples/llm_router/router.py:299`, `src/plugin_examples/llm_router/router.py:320` |
| `LLM_API_KEY`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `OLLAMA_HOST` | Still visible in router code; not approved by repo governance for live inference |
| `EXAMPLE_REVIEWER_PATH` | External reviewer path: verifier bridge modules |
| `AGENT_METRICS_*` | Metrics config/env overrides: `src/plugin_examples/metrics/config.py:120-167` |

## CLI/API Reference Extracted From Code

Package/module entry:

- `plugin-examples`: `pyproject.toml`
- `python -m plugin_examples`: `src/plugin_examples/__main__.py`

Global flag:

- `--verbose`, `-v`: `src/plugin_examples/__main__.py:98`

Shared metrics flags:

- `--metrics`, `--metrics-post`, `--metrics-job-type`, `--metrics-strict`, `--metrics-force-repost`, `--metrics-config`: `src/plugin_examples/__main__.py:10-23`

Commands:

| Command | Main flags/options | Evidence |
|---|---|---|
| `status` | none | `src/plugin_examples/__main__.py:103` |
| `run` | `--family`, `--dry-run`, `--template-mode`, `--skip-run`, `--require-llm`, `--require-validation`, `--require-reviewer`, `--publish`, `--approval-token`, `--tier`, `--promote-latest`, `--allow-experimental`, `--compare-run`, `--replay-from`, `--reuse-run` | `src/plugin_examples/__main__.py:106-159` |
| `discover-lowcode` | `--all-families`, `--family`, `--families`, `--dry-run`, `--promote-latest`, `--allow-experimental`, `--rank` | `src/plugin_examples/__main__.py:162-176` |
| `validate-publish-targets` | `--families`, `--promote-latest` | `src/plugin_examples/__main__.py:180-191` |
| `resolve-repo-access` | `--families`, `--promote-latest` | `src/plugin_examples/__main__.py:196-207` |
| `probe-publish-permissions` | `--families`, `--dry-run`, `--promote-latest` | `src/plugin_examples/__main__.py:212-227` |
| `publish-pr` | `--family`, `--dry-run`, `--publish`, `--approval-token`, `--package-path`, `--promote-latest` | `src/plugin_examples/__main__.py:232-260` |
| `merge-pr` | `--family`, `--pr-number`, `--dry-run`, `--merge`, `--approval-token`, `--promote-latest` | `src/plugin_examples/__main__.py:266-291` |
| `release-status` | `--families`, `--promote-latest`, `--validate-bundle` | `src/plugin_examples/__main__.py:296-311` |
| `render-root-readme` | `--family`, `--package-path`, `--promote-latest`, `--cumulative` | `src/plugin_examples/__main__.py:319-334` |
| `publish-readme` | `--family`, `--publish`, `--approval-token`, `--promote-latest` | `src/plugin_examples/__main__.py:340-355` |
| `sync-taskcard-docs` | `--promote-latest` compatibility flag | `src/plugin_examples/__main__.py:361-367` |
| `check` | `--family` | `src/plugin_examples/__main__.py:373-374` |
| `publish-pr-batch` | `--family`, `--publish`, `--dry-run`, `--approval-token`, `--promote-latest` | `src/plugin_examples/__main__.py:377-396` |
| `formimporter-watch` | `--run-repro`, `--output` | `src/plugin_examples/__main__.py:401-410` |
| `post-publication-verify` | `--family`, `--output` | `src/plugin_examples/__main__.py:415-422` |
| `version-drift` | `--family`, `--output`, `--json` | `src/plugin_examples/__main__.py:426-440` |
| `target-repo-health` | `--family`, `--output`, `--json` | `src/plugin_examples/__main__.py:444-456` |
| `next-actions` | `--output`, `--markdown`, `--json` | `src/plugin_examples/__main__.py:462-476` |
| `execute-next-actions` | `--evidence-dir`, `--max-cycles`, `--dry-run-remote`, `--json` | `src/plugin_examples/__main__.py:480-496` |

Legacy/direct script entry points:

- `scripts/pilot_run.py`
- `scripts/sync_taskcards.py`
- `scripts/validate_published_examples_build.py`
- `src/plugin_examples/package_watcher/formimporter_watch.py`

## Data Directories and File Contracts

| Path | Contract/evidence |
|---|---|
| `workspace/runs/{run_id}/` | Per-run root: `src/plugin_examples/runner.py:1570-1572` |
| `workspace/runs/{run_id}/evidence/latest/` | Run-scoped evidence directory |
| `workspace/runs/{run_id}/packages/{family}/` | Primary NuGet package cache/download target |
| `workspace/runs/{run_id}/packages/{family}/deps/` | Dependency package cache/download target |
| `workspace/runs/{run_id}/catalog/{family}/api-catalog.json` | Reflected API catalog |
| `workspace/runs/{run_id}/generated/{family}/` | Generated projects |
| `workspace/manifests/` | Promoted package lock/fixture registry/example indexes/scenario catalog |
| `workspace/verification/latest/` | Global aggregate evidence and compatibility aliases |
| `workspace/verification/latest/families/{family}/` | Family-scoped promoted evidence |
| `workspace/pr-dry-run/` | Dry-run PR packages |
| `workspace/verification/agent-metrics-post-ledger.jsonl` | Metrics post ledger |
| `workspace/verification/latest/open-taskcard-closure-matrix.json` | Authoritative taskcard matrix JSON |
| `docs/development/open-taskcard-closure-matrix.md` | Generated taskcard markdown view |
| `pipeline/schemas/*.schema.json` | JSON schemas |
| `pipeline/contracts/**/*.json` | Scenario contracts |
| `reports/` | Generated/historical evidence and reports, not canonical operating docs |

## Observability

Logging:

- Modules use `logging.getLogger(__name__)`, including `runner`, config loader, and LLM router.
- CLI global `--verbose` exists at `src/plugin_examples/__main__.py:98`.

Structured evidence:

- Run reports and evidence are written by `runner.py`.
- Gate files are written by `src/plugin_examples/gates/`.
- Metrics evidence files are written by `src/plugin_examples/metrics/evidence.py`.
- Metrics duplicate POST ledger is managed by `src/plugin_examples/metrics/poster.py`.

Retry/backoff:

- LLM retry delays are `[30, 60]` seconds: `src/plugin_examples/llm_router/router.py:18`.
- LLM transient failures use backoff in provider call paths: `src/plugin_examples/llm_router/router.py:362`, `src/plugin_examples/llm_router/router.py:445`.

## Testing Strategy

Test runner:

- `pyproject.toml` configures `testpaths = ["tests"]` and timeout `30`.
- CI workflow runs unit tests with `PYTHONPATH=src python -m pytest tests/unit -v --timeout=60`.

Test coverage areas visible from test filenames:

- CLI and runner: `test_cli_defaults.py`, `test_runner.py`, `test_runner_contract_evidence.py`
- Config and denominators: `test_family_config.py`, `test_denominator_model.py`
- NuGet/extraction/reflection: `test_nuget_fetcher.py`, `test_dependency_resolver.py`, `test_nupkg_extractor.py`, `test_reflection_catalog.py`
- Scenario planning/contracts: `test_scenario_planner.py`, `test_scenario_contracts.py`, `test_planner_contract_consumption.py`
- Generation/validation/reviewer: `test_llm_generation.py`, `test_codegen_contract_consumption.py`, `test_validation.py`, `test_gate_output_validation.py`, `test_reviewer_repair_loop.py`
- Publishing/GitHub/merge: `test_publishing.py`, `test_publishing_approval_gate.py`, `test_real_github_publisher.py`, `test_merge_governance.py`
- README publishing: `test_readme_renderer.py`, `test_readme_audit_gate.py`, `test_publish_pr_readme_gate.py`
- Metrics: `test_agent_metrics_*.py`, `test_metrics_collector.py`
- Docs path governance: `test_sync_taskcard_docs.py`, `test_ci_runbook_hardening.py`, `test_token_policy.py`, `test_fixture_strategy.py`

## Known Gaps/Risks

1. LLM endpoint governance is not enforced fail-closed in code. Router defaults still include OpenAI/local URLs and `ollama` remains in `_APPROVED_PROVIDER_FAMILIES`: `src/plugin_examples/llm_router/router.py:237`, `src/plugin_examples/llm_router/router.py:247`, `src/plugin_examples/llm_router/router.py:297`, `src/plugin_examples/llm_router/router.py:319`.
2. OpenAI/generic LLM fallbacks remain in code: `src/plugin_examples/llm_router/router.py:173-175`, `src/plugin_examples/llm_router/router.py:309-320`.
3. GitHub token governance says `GH_TOKEN` is operator storage, but one target-repo health path falls back to `GH_TOKEN`: `src/plugin_examples/publisher/target_repo_health.py` (identified in prior audit and still relevant).
4. Historical `_archive/` docs intentionally contain stale paths and prior procedures. They are not canonical, but search results can surface them unless operators start from `docs/README.md`.
5. `check` is still a placeholder command surface: `src/plugin_examples/__main__.py:373-374`.
