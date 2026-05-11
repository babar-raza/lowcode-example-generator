# Traceability

Feature list is derived from code surfaces: CLI commands, modules, config files, schemas, tests, and workflows. Documentation coverage is scored from the docs inventory, not from assumed intent.

| Feature | Evidence | Current docs coverage | Gaps |
|---|---|---|---|
| Package/CLI entry point | `pyproject.toml`; `src/plugin_examples/__main__.py` | Partial: `README.md`, scattered runbooks | No concise generated CLI reference under docs; current commands exceed old docs. |
| Full pipeline staged run | `runner.py` `STAGE_DEFINITIONS`, `run_pipeline()` | Partial: large execution plan and discovery docs | Plan includes stale greenfield/current-state claims; needs code-backed canonical workflow doc. |
| Tiered execution | CLI `run --tier`; `runner.py` tier map | Partial/Unknown | No clear operator reference found. |
| Family YAML model | `family_config/loader.py`, `models.py`, schema `family-config.schema.json`, configs under `pipeline/configs/families/` | Partial: plan and some family docs | Needs canonical config reference generated from schema and loader defaults. |
| Disabled/experimental/discovery-only family handling | `loader.py`, `runner._stage_load_config()` | Partial | Needs operator-facing behavior table. |
| NuGet fetch/latest/pinned resolution | `nuget_fetcher/fetcher.py`; tests `test_nuget_fetcher.py` | Partial: plan | Needs current code-backed reference and cache behavior. |
| Dependency resolution | `nuget_fetcher/dependency_resolver.py`; tests | Partial | Needs current data contracts and failure modes. |
| Nupkg extraction/framework selection | `nupkg_extractor/extractor.py`, `framework_selector.py`; tests | Partial | Needs framework-selection reference. |
| DllReflector/API catalog | `reflection_catalog/*.py`; `tools/DllReflector/`; `api-catalog.schema.json`; tests | Partial | Needs schema/catalog contract documentation. |
| Plugin namespace detection | `plugin_detector/detector.py`, `proof_reporter.py`; namespace patterns in family configs | Partial | Needs source-of-truth proof semantics documented from code. |
| Discovery sweep | CLI `discover-lowcode`; `discovery_sweep.py` | Partial: many discovery reports | No single maintained discovery reference. |
| API delta | `api_delta/delta_engine.py`, `impact_mapper.py`; tests | Partial | Needs evidence file contract docs. |
| Fixture registry/cache | `fixture_registry/registry.py`, cache at `~/.cache/plugin-examples/fixture-listings`; tests | Partial: PDF/Words fixture docs | Needs generic fixture reference and cache invalidation notes. |
| Generated fixture factory | `fixture_factory.py`; generated fixture evidence | Partial | Needs supported formats and limitations from code. |
| Existing example miner | `example_miner/miner.py`, `symbol_validator.py`; tests | Partial | Needs symbol validation contract. |
| Scenario planner | `scenario_planner/planner.py`, classifiers/scorers/mappers; tests | Partial: multiple planning docs | Needs one canonical scenario-planning reference; current docs are scattered by sprint/family. |
| Catalog hash enforcement | `planner.validate_catalog_hash`, `runner._write_catalog_hash_evidence`; tests `test_catalog_hash_enforcement.py` | Partial | Needs source-of-truth/cross-run semantics explained. |
| LLM preflight/routing | `llm_router/router.py`, `provider_policy.py`, `pipeline/configs/llm-routing.yml`; tests | Partial: `llm-provider-policy-audit.md` | Needs current provider env vars and approved provider policy consolidated. |
| Template generation | `generator/code_generator.py`, `project_generator.py`, family `template_hints` | Partial | Needs supported method/argument generation constraints. |
| Prompt packet generation | `generator/packet_builder.py`, `scenario-packet.schema.json` | Unknown/Partial | Needs schema + required symbol enforcement docs. |
| Generated project layout | `generator/project_generator.py`; generated `Directory.Packages.props`, `Directory.Build.props`, `global.json` | Partial | Needs output project contract. |
| Dotnet validation | `verifier_bridge/dotnet_runner.py`; tests `test_validation.py` | Partial: verifier docs | Needs restore/build/run result schema and runtime runner behavior. |
| Output semantic validation | `verifier_bridge/output_validator.py` | Partial | Needs supported output formats and failure classes. |
| External example-reviewer | `verifier_bridge/bridge.py`, `reviewer_preflight.py`; env `EXAMPLE_REVIEWER_PATH` | Duplicate/Partial: root orphan and discovery docs | Merge and refresh verifier docs. |
| Gate verdicts | `gates/models.py`, `evaluator.py`, `example_gates.py`; tests | Partial: plan/gate checklist docs | Needs canonical verdict matrix from code. |
| Per-example lifecycle/backlog | `gates/example_lifecycle.py`; tests | Partial: lifecycle docs | Needs persistent backlog contract. |
| Evidence completeness | `gates/evidence_completeness.py`; tests | Partial | Needs required/degraded evidence list. |
| Evidence layout/promotion | `evidence_layout.py`; tests in runner and family-scoped evidence docs | Partial | Needs canonical storage layout and deprecation of latest root alias. |
| Dry-run package publishing | `publisher/publisher.py`, `pr_builder.py`; CLI `publish-pr --dry-run` | Partial: publishing runbooks/results | Needs current dry-run contract. |
| Live GitHub PR creation | `publisher/github_pr_publisher.py`; CLI approval checks | Partial/Duplicate: live PR docs | Needs single live publish runbook. |
| Publish readiness/repo access/permission probes | `publisher/publish_readiness.py`, `repo_access_resolver.py`, `publish_permission_probe.py`; CLI commands | Partial | Needs operator reference. |
| Merge PR workflow | `publisher/github_pr_merger.py`, `merge_approval_gate.py`; CLI `merge-pr` | Partial: merge result/preflight docs | Needs current safety gates and separate approval token docs. |
| Release status | `publisher/release_status.py`; CLI `release-status`; tests | Partial | Needs status file contract. |
| README rendering/audit/publish | `publisher/readme_renderer.py`, `readme_auditor.py`; CLI `render-root-readme`, `publish-readme`; tests | Partial: root README workflow docs | Needs canonical README workflow reference. |
| Agent metrics | `metrics/*.py`, `pipeline/configs/metrics.yml`; tests `test_agent_metrics_*.py`; CLI metrics flags | Partial: `docs/publishing/agent-metrics-runbook.md` | Needs update against current env vars and production gate. |
| Monthly GitHub Actions refresh | `.github/workflows/monthly-package-refresh.yml`; `scripts/validate_published_examples_build.py` | Duplicate/Partial: root orphan and publishing monthly runbook | Merge root orphan into canonical ops runbook and align with workflow. |
| Build/test CI | `.github/workflows/build-and-test.yml` | Partial | Needs contributor quick reference. |
| Taskcard sync | CLI `sync-taskcard-docs`; `scripts/sync_taskcards.py` | Partial: generated matrix doc | Needs source JSON contract. |
| Published example build regression | `scripts/validate_published_examples_build.py`; monthly workflow | Partial | Needs output report schema/location. |
| Denominator model/contracts | `pipeline/configs/denominators/*.json`, `pipeline/contracts/**/*.json`, schemas/tests | Partial: denominator plans | Needs canonical contract reference. |

## Unverified or Partially Verified Feature Claims From Docs

These should not be promoted as current behavior without code re-check:

- Any claim that this repo is greenfield/no tests/no infrastructure is outdated relative to `src/plugin_examples/`, `tests/unit/`, and `.github/workflows/`.
- Any documentation describing more than 17 runnable pipeline gates should be checked against `runner.py` and `gates/models.py`; code has 16 executable stages plus combined source-of-truth gate and post-stage per-example gates.
- Retry/backoff behavior is partially evidenced by LLM config `max_retries`, but consistent implementation across all external integrations was not fully verified in this audit.
