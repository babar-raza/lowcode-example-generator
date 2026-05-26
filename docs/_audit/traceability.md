# Traceability

Audit mode: feature list is derived from code surfaces only. Documentation coverage is assessed against current active docs, with code as source of truth.

Last refreshed: 2026-05-26.

| Feature/code surface | Evidence | Current docs coverage | Gaps |
|---|---|---|---|
| Package exposes `plugin-examples` CLI | `pyproject.toml`; `src/plugin_examples/__main__.py:93-98` | `docs/reference/cli.md`, `docs/README.md` | None found in active docs. |
| Shared metrics flags | `src/plugin_examples/__main__.py:10-23` | `docs/reference/cli.md`, `docs/reference/metrics.md` | Keep metrics reference aligned with config/poster code. |
| `run` family pipeline | `src/plugin_examples/__main__.py:106-159`; `src/plugin_examples/runner.py:1537-1900` | `docs/guides/run-family-pipeline.md`, `docs/reference/cli.md`, `docs/reference/file-contracts.md` | None found in active docs. |
| Pipeline stage order | `src/plugin_examples/runner.py:1510-1529` | `docs/architecture/pipeline-stages.md`, `docs/reference/gates-and-verdicts.md` | Verify architecture page periodically against `STAGE_DEFINITIONS`. |
| Hard-stop stages | `src/plugin_examples/runner.py:1532-1534`, `src/plugin_examples/runner.py:1734` | `docs/reference/gates-and-verdicts.md`, `docs/architecture/pipeline-stages.md` | Reference should be regenerated when runner changes. |
| Family config loading/schema validation | `src/plugin_examples/family_config/loader.py`; `src/plugin_examples/family_config/validator.py`; `pipeline/schemas/family-config.schema.json` | `docs/reference/config.md`, `docs/guides/add-or-update-family.md` | None found in active docs. |
| Config model defaults | `src/plugin_examples/family_config/models.py:15-116` | `docs/reference/config.md` | None found in active docs. |
| Active family configs | `pipeline/configs/families/*.yml` | `docs/reference/config.md`, `docs/guides/add-or-update-family.md` | Need optional generated family inventory if operators need status matrix. |
| NuGet fetch/cache | `src/plugin_examples/runner.py:335-349`; `src/plugin_examples/nuget_fetcher/fetcher.py` | `docs/reference/file-contracts.md`, `docs/architecture/pipeline-stages.md` | None found in active docs. |
| Dependency resolution | `src/plugin_examples/runner.py:402-424`; `src/plugin_examples/nuget_fetcher/dependency_resolver.py` | `docs/reference/config.md`, `docs/reference/file-contracts.md` | None found in active docs. |
| Extraction/reflection catalog | `src/plugin_examples/runner.py:426-465`; `pipeline/schemas/api-catalog.schema.json` | `docs/reference/file-contracts.md`, `docs/architecture/pipeline-stages.md` | None found in active docs. |
| Plugin namespace detection/source-of-truth proof | `src/plugin_examples/runner.py:468-515` | `docs/reference/file-contracts.md`, `docs/reference/gates-and-verdicts.md` | None found in active docs. |
| Version drift preflight | `src/plugin_examples/runner.py:351-400`; `src/plugin_examples/__main__.py:426-440` | `docs/reference/cli.md`, `docs/operations/monthly-maintenance.md` | Monthly runbook should remain aligned. |
| Denominator model | `pipeline/configs/denominators/*.json`; `tests/unit/test_denominator_model.py` | `docs/reference/config.md`, `docs/reference/schemas-and-contracts.md` | Schema/contract reference should include inventory detail. |
| Scenario contracts | `pipeline/contracts/**/*.json`; `pipeline/schemas/scenario-contract.schema.json` | `docs/reference/schemas-and-contracts.md`, `docs/reference/file-contracts.md` | Contract inventory should be refreshed automatically if possible. |
| Fixture registry | `src/plugin_examples/runner.py:536-546`; `src/plugin_examples/fixture_registry/registry.py` | `docs/reference/file-contracts.md`, `docs/reference/validation-and-reviewer.md` | None found in active docs. |
| Existing example mining | `src/plugin_examples/runner.py:548-556`; `src/plugin_examples/example_miner/miner.py` | `docs/reference/file-contracts.md`, `docs/architecture/pipeline-stages.md` | None found in active docs. |
| Scenario planning | `src/plugin_examples/runner.py:558-683`; `tests/unit/test_scenario_planner.py` | `docs/reference/gates-and-verdicts.md`, `docs/architecture/pipeline-stages.md` | None found in active docs. |
| LLM preflight/router | `src/plugin_examples/runner.py:685-703`; `src/plugin_examples/llm_router/router.py:173-320` | `docs/reference/environment-variables.md`, `docs/guides/generate-and-validate-examples.md` | Code still exposes non-governed fallbacks; docs correctly mark them not approved. |
| LLM retry/backoff | `src/plugin_examples/llm_router/router.py:18`, `src/plugin_examples/llm_router/router.py:362`, `src/plugin_examples/llm_router/router.py:445` | `docs/operations/troubleshooting.md`, `docs/_audit/system_audit.md` | Active troubleshooting page should include current retry timing. |
| Template/project generation | `src/plugin_examples/runner.py:705-872`; `src/plugin_examples/generator/*` | `docs/guides/generate-and-validate-examples.md`, `docs/reference/file-contracts.md` | None found in active docs. |
| Dotnet validation | `src/plugin_examples/runner.py:874-1259`; `src/plugin_examples/verifier_bridge/dotnet_runner.py` | `docs/reference/validation-and-reviewer.md` | None found in active docs. |
| Output validation | `src/plugin_examples/verifier_bridge/output_validator.py` | `docs/reference/validation-and-reviewer.md` | None found in active docs. |
| External reviewer | `src/plugin_examples/verifier_bridge/reviewer_preflight.py`; `src/plugin_examples/verifier_bridge/bridge.py` | `docs/reference/validation-and-reviewer.md`, `docs/reference/environment-variables.md` | None found in active docs. |
| Gate evaluation | `src/plugin_examples/runner.py:1780-1837`; `src/plugin_examples/gates/writer.py` | `docs/reference/gates-and-verdicts.md`, `docs/reference/file-contracts.md` | Reference should be regenerated when gate code changes. |
| Lifecycle/backlog tracking | `src/plugin_examples/gates/example_lifecycle.py`; `src/plugin_examples/runner.py:1837` | `docs/reference/file-contracts.md`, `docs/development/taskcards.md` | None found in active docs. |
| Replay mode | `src/plugin_examples/__main__.py:134-159`; `src/plugin_examples/runner.py:1609-1679` | `docs/reference/cli.md`, `docs/guides/run-family-pipeline.md` | Guide could add a short replay scenario if operators use it often. |
| Run-to-run comparison | `src/plugin_examples/__main__.py:132`; `src/plugin_examples/runner.py:1839-1863` | `docs/reference/cli.md`, `docs/reference/file-contracts.md` | None found in active docs. |
| Evidence promotion | `src/plugin_examples/runner.py:1892-1900`; `src/plugin_examples/evidence_layout.py` | `docs/reference/file-contracts.md`, `docs/guides/run-family-pipeline.md` | None found in active docs. |
| Publish readiness validation | `src/plugin_examples/__main__.py:180-191`; `src/plugin_examples/publisher/publish_readiness.py` | `docs/reference/cli.md`, `docs/reference/publishing-and-github.md`, `docs/operations/live-publishing.md` | None found in active docs. |
| Repo access resolution | `src/plugin_examples/__main__.py:196-207`; `src/plugin_examples/publisher/repo_access_resolver.py` | `docs/reference/cli.md`, `docs/reference/publishing-and-github.md` | None found in active docs. |
| Publish permission probe | `src/plugin_examples/__main__.py:212-227`; `src/plugin_examples/publisher/publish_permission_probe.py` | `docs/reference/cli.md`, `docs/reference/publishing-and-github.md` | None found in active docs. |
| PR publishing | `src/plugin_examples/__main__.py:232-260`; `src/plugin_examples/publisher/github_pr_publisher.py` | `docs/operations/live-publishing.md`, `docs/reference/publishing-and-github.md` | None found in active docs. |
| PR merge | `src/plugin_examples/__main__.py:266-291`; `src/plugin_examples/publisher/github_pr_merger.py` | `docs/operations/post-merge-verification.md`, `docs/reference/publishing-and-github.md` | None found in active docs. |
| README rendering/auditing/publishing | `src/plugin_examples/__main__.py:319-355`; `src/plugin_examples/publisher/readme_renderer.py`; `src/plugin_examples/publisher/readme_audit_gate.py` | `docs/operations/readme-publishing.md`, `docs/reference/publishing-and-github.md`, `docs/reference/file-contracts.md` | None found in active docs. |
| Batch publishing | `src/plugin_examples/__main__.py:377-396`; `src/plugin_examples/publisher/batch_publisher.py` | `docs/reference/cli.md`, `docs/reference/publishing-and-github.md` | None found in active docs. |
| Post-publication verification | `src/plugin_examples/__main__.py:415-422`; `src/plugin_examples/publisher/post_publication_verifier.py` | `docs/reference/cli.md`, `docs/operations/post-merge-verification.md` | None found in active docs. |
| Release status | `src/plugin_examples/__main__.py:296-311`; `src/plugin_examples/publisher/release_status.py` | `docs/reference/cli.md`, `docs/operations/post-merge-verification.md` | None found in active docs. |
| Target repo health | `src/plugin_examples/__main__.py:444-456`; `src/plugin_examples/publisher/target_repo_health.py` | `docs/reference/cli.md`, `docs/reference/publishing-and-github.md` | Code still has `GH_TOKEN` fallback governance gap. |
| Portfolio next actions | `src/plugin_examples/__main__.py:462-496`; `src/plugin_examples/portfolio_action_planner.py` | `docs/reference/cli.md` | Could add operator guide only if this becomes a common workflow. |
| FormImporter watch | `src/plugin_examples/__main__.py:401-410`; `src/plugin_examples/package_watcher/formimporter_watch.py` | `docs/reference/cli.md` | Could add ops note if actively used. |
| Metrics | `src/plugin_examples/__main__.py:10-90`; `src/plugin_examples/metrics/*`; `pipeline/configs/metrics.yml` | `docs/reference/metrics.md`, `docs/operations/telemetry.md` | Keep operations/reference split synchronized. |
| Evidence contract validator | `src/plugin_examples/evidence_contract.py`; `tests/unit/test_evidence_contract.py` | `docs/reference/file-contracts.md`, `docs/reference/schemas-and-contracts.md` | Large sprint-specific validator surface remains hard to document exhaustively. |
| Tests/CI | `pyproject.toml`; `.github/workflows/build-and-test.yml`; `tests/unit/*.py` | `docs/development/testing.md` | None found in active docs. |
| Taskcard sync | `scripts/sync_taskcards.py:21-22`; `src/plugin_examples/__main__.py:361-367`, `src/plugin_examples/__main__.py:1507-1508` | `docs/development/taskcards.md`, `docs/development/open-taskcard-closure-matrix.md`, `docs/reference/file-contracts.md` | None found in active docs. |
| Root docs hygiene | `Get-ChildItem docs -File`; `docs/README.md`; `docs/_audit/root_orphans.md` | `docs/README.md`, `docs/_audit/root_orphans.md` | No root orphans found. |
