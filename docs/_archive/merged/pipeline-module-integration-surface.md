# Pipeline Module Integration Surface

Verified against source at commit b3ecbc3 (2026-04-28).

## 1. family_config

**Import:** `from plugin_examples.family_config import load_family_config, FamilyConfig, DisabledFamilyError`

```python
load_family_config(path: str | Path) -> FamilyConfig
```

Key fields on FamilyConfig (frozen dataclass):
- `family: str`, `enabled: bool`, `status: str`
- `nuget: NuGetConfig` — `.package_id`, `.version_policy`, `.pinned_version`, `.allow_prerelease`, `.target_framework_preference: list[str]`, `.dependency_resolution: DependencyResolution` (`.enabled`, `.max_depth`)
- `plugin_detection: PluginDetection` — `.namespace_patterns: list[str]`
- `fixtures: FixturesConfig` — `.sources: list[FixtureSource]`
- `existing_examples: ExistingExamplesConfig` — `.sources: list[FixtureSource]`
- `generation: GenerationConfig` — `.min_examples_per_family`, `.max_examples_per_monthly_run`
- `validation: ValidationConfig` — `.require_run`, `.require_example_reviewer`
- `llm: LLMConfig` — `.provider_order: list[str]`

FixtureSource (frozen dataclass): `type: str, owner: str, repo: str, branch: str, paths: list[str]`

## 2. nuget_fetcher

**Import:** `from plugin_examples.nuget_fetcher import fetch_package, resolve_dependencies`

```python
fetch_package(package_id: str, version_policy: str, *, pinned_version: str | None = None,
              allow_prerelease: bool = False, run_dir: Path, family: str) -> dict
# Returns: {package_id, version, sha256, source_url, cached_path}

resolve_dependencies(nupkg_path: Path, *, target_frameworks: list[str], max_depth: int = 2,
                     run_dir: Path, family: str) -> list[dict]
# Returns: [{package_id, version, sha256, source_url, cached_path, depth, status, error?}]
```

**Direct imports needed:**
```python
from plugin_examples.nuget_fetcher.dependency_resolver import write_dependency_manifest, update_package_lock
write_dependency_manifest(deps: list[dict], run_dir: Path, family: str) -> Path
update_package_lock(download_manifest: dict, deps: list[dict], manifests_dir: Path) -> Path
```

## 3. nupkg_extractor

**Import:** `from plugin_examples.nupkg_extractor import extract_package`

```python
extract_package(nupkg_path: Path, *, package_id: str, family: str,
                target_framework_preference: list[str], run_dir: Path,
                dependency_nupkgs: list[Path] | None = None) -> dict
# Returns: {package_id, family, selected_framework, framework_selection_reason,
#   requires_windows_runner, dll_path, xml_path, xml_warning,
#   dependency_dll_paths, extracted_primary_path, extracted_dependency_paths}
```

## 4. reflection_catalog

**Import:** `from plugin_examples.reflection_catalog import build_catalog`

```python
build_catalog(*, dll_path: Path, output_path: Path, xml_path: Path | None = None,
              dependency_paths: list[Path] | None = None, reflector_dir: Path | None = None,
              namespace_filter: list[str] | None = None, timeout: int = 120) -> dict
# Returns: validated API catalog dict {assembly_name, assembly_version, namespaces, diagnostics}
```

## 5. plugin_detector

**Import:** `from plugin_examples.plugin_detector import detect_plugin_namespaces, write_source_of_truth_proof, write_product_inventory, assert_source_of_truth_eligible`

```python
detect_plugin_namespaces(catalog: dict, namespace_patterns: list[str]) -> DetectionResult

write_source_of_truth_proof(*, family: str, package_id: str, resolved_version: str,
    nupkg_sha256: str | None, selected_target_framework: str | None,
    dll_path: str | None, xml_path: str | None, xml_warning: str | None,
    dependency_count: int, dependency_paths: list[str],
    api_catalog_path: str | None, detection_result: DetectionResult,
    verification_dir: Path) -> Path
# Writes to: {verification_dir}/latest/{family}-source-of-truth-proof.json

write_product_inventory(*, family: str, package_id: str, resolved_version: str,
    detection_result: DetectionResult, manifests_dir: Path) -> Path

assert_source_of_truth_eligible(path: str) -> None  # raises SourceOfTruthGateError
```

DetectionResult dataclass: `matched_namespaces: list[NamespaceMatch]`, `unmatched_patterns: list[dict]`, `public_plugin_type_count: int`, `public_plugin_method_count: int`, `@property is_eligible: bool`

NamespaceMatch dataclass: `namespace: str`, `matched_by_pattern: str`, `public_type_count: int`, `public_method_count: int`

## 6. api_delta

**Import:** `from plugin_examples.api_delta import compute_delta, map_impact`

```python
compute_delta(new_catalog: dict, old_catalog: dict | None = None) -> DeltaResult
map_impact(delta: DeltaResult, existing_examples_index: dict | None = None) -> ImpactReport
```

**Direct imports needed:**
```python
from plugin_examples.api_delta.delta_engine import write_delta_report
write_delta_report(delta: DeltaResult, verification_dir: Path) -> Path
# Writes to: {verification_dir}/latest/api-delta-report.json

from plugin_examples.api_delta.impact_mapper import write_impact_report
write_impact_report(impact: ImpactReport, verification_dir: Path) -> Path
# Writes to: {verification_dir}/latest/example-impact-report.json
```

DeltaResult: `initial_run: bool`, `old_version: str | None`, `new_version: str`, `added_types`, `removed_types`, `modified_types`, `@property has_changes`, `total_changes`

## 7. fixture_registry

**Import:** `from plugin_examples.fixture_registry import FixtureRegistry, write_fixture_registry`

**Direct import needed:**
```python
from plugin_examples.fixture_registry.registry import build_fixture_registry
build_fixture_registry(family: str, fixture_sources: list[dict]) -> FixtureRegistry
write_fixture_registry(registry: FixtureRegistry, manifests_dir: Path) -> Path
# Writes to: {manifests_dir}/fixture-registry.json
```

## 8. example_miner

**Import:** `from plugin_examples.example_miner import mine_examples`

```python
mine_examples(family: str, example_sources: list[dict], *, catalog: dict | None = None) -> MiningResult
```

**Direct imports needed:**
```python
from plugin_examples.example_miner.miner import write_examples_index, write_stale_report
write_examples_index(result: MiningResult, manifests_dir: Path) -> Path
write_stale_report(result: MiningResult, verification_dir: Path) -> Path
```

MiningResult: `family: str`, `examples: list[MinedExample]`, `stale_examples`, `@property total`, `stale_count`

## 9. scenario_planner

**Import:** `from plugin_examples.scenario_planner import plan_scenarios, write_scenario_catalog, write_blocked_scenarios`

```python
plan_scenarios(*, family: str, catalog: dict, plugin_namespaces: list[str],
               fixture_registry: dict | None = None, min_examples: int = 3,
               source_of_truth_proof_path: str | None = None) -> PlanningResult
```

**BINDING: `fixture_registry` expects `dict | None`, NOT a FixtureRegistry dataclass.**
Internally accesses `fixture_registry.get("fixtures", [])`.

```python
write_scenario_catalog(result: PlanningResult, manifests_dir: Path) -> Path
write_blocked_scenarios(result: PlanningResult, verification_dir: Path) -> Path
```

`_scenario_to_dict(s: Scenario) -> dict` is PRIVATE — NOT exported. Runner must implement its own `scenario_to_dict`.

Scenario dataclass: `scenario_id, title, target_type, target_namespace, target_methods, required_symbols, required_fixtures, output_plan, validation_plan, status, blocked_reason`

PlanningResult: `family, ready_scenarios: list[Scenario], blocked_scenarios: list[Scenario], @property ready_count, blocked_count`

## 10. llm_router

**Import:** `from plugin_examples.llm_router import LLMRouter, LLMProviderError`

```python
LLMRouter(provider_order: list[str])
  .run_preflight(*, timeout: int = 30, llm_config: dict | None = None) -> list[PreflightResult]
  .get_provider() -> str  # raises LLMProviderError
  .generate(prompt: str, *, system_prompt: str = "", timeout: int = 120) -> str
  .selected_provider: str | None
```

**Direct import needed:**
```python
from plugin_examples.llm_router.router import write_preflight_report
write_preflight_report(results: list[PreflightResult], selected: str | None, verification_dir: Path) -> Path
```

**BINDING MISMATCH:** `generate_example` calls `llm_generate(prompt, system_prompt)` positionally. `LLMRouter.generate` has `system_prompt` as keyword-only. Runner must wrap: `lambda p, s: router.generate(p, system_prompt=s)`

## 11. generator

**Import:** `from plugin_examples.generator import build_packet, generate_example, generate_project, write_example_index`

```python
build_packet(scenario: dict, catalog: dict, *, prompt_template: str | None = None) -> PromptPacket
generate_example(packet: PromptPacket, *, llm_generate: callable | None = None, max_repairs: int = 1) -> GeneratedExample
generate_project(example: GeneratedExample, *, package_id: str, target_framework: str = "net8.0", output_dir: Path) -> dict
write_example_index(examples: list[dict], manifests_dir: Path) -> Path
```

GeneratedExample: `scenario_id, code, claimed_symbols, repair_attempts, status, failure_reason`

## 12. verifier_bridge

**Import:** `from plugin_examples.verifier_bridge import run_dotnet_validation, run_example_reviewer`

```python
run_dotnet_validation(project_dir: Path, scenario_id: str, *, skip_run: bool = False, timeout: int = 120) -> ValidationResult
run_example_reviewer(*, family: str, workspace_dir: Path, reviewer_path: Path | None = None, timeout: int = 300) -> ReviewerResult
```

**Direct imports needed:**
```python
from plugin_examples.verifier_bridge.dotnet_runner import write_validation_results
write_validation_results(results: list[ValidationResult], verification_dir: Path) -> Path

from plugin_examples.verifier_bridge.bridge import write_reviewer_results, ReviewerUnavailableError
write_reviewer_results(result: ReviewerResult, verification_dir: Path) -> Path
```

ValidationResult: `scenario_id, restore, build, run, passed, failure_stage`

## 13. publisher

**Import:** `from plugin_examples.publisher import publish_examples`

```python
publish_examples(*, family: str, run_id: str, examples: list[dict], verification_dir: Path,
                 dry_run: bool = True, github_token: str | None = None) -> PublishResult
```

**Direct import needed:**
```python
from plugin_examples.publisher.publisher import write_publishing_report
write_publishing_report(result: PublishResult, verification_dir: Path) -> Path
```

PublishResult: `dry_run, branch_name, pr_url, files_included, evidence_verified, status, blocked_reason`

## Confirmed Mismatches vs Original Plan

| # | Issue | Detail |
|---|-------|--------|
| 1 | LLM callable signature | `generate_example` expects `(prompt, system_prompt)` positional; `LLMRouter.generate` has keyword-only `system_prompt` |
| 2 | `_scenario_to_dict` private | Not exported; runner must implement own `scenario_to_dict` |
| 3 | `plan_scenarios` fixture param | Expects `dict | None`, not `FixtureRegistry` dataclass |
| 4 | `FixtureSource` is dataclass | `config.fixtures.sources` returns `list[FixtureSource]`, must convert to `list[dict]` |
| 5 | write_* not in __init__ | 10+ write functions require direct submodule imports |
| 6 | write_source_of_truth_proof path | Appends `/latest/` to `verification_dir` internally |
