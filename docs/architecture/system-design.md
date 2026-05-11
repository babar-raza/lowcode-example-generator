# System Design

Audience: Contributor, Operator
Source of truth: `docs/_audit/system_audit.md`, `src/plugin_examples/`

The pipeline combines deterministic source-of-truth extraction with constrained generation and validation.

```text
NuGet package
  -> dependency resolution
  -> extraction
  -> reflection catalog
  -> plugin detection
  -> API delta and impact
  -> fixtures and example mining
  -> scenario planning
  -> LLM/template generation
  -> restore/build/run/output validation
  -> example-reviewer
  -> gates
  -> PR publishing
```

## Primary Components

| Component | Code |
|---|---|
| CLI | `src/plugin_examples/__main__.py` |
| Runner | `src/plugin_examples/runner.py` |
| Config | `src/plugin_examples/family_config/` |
| NuGet/extraction/reflection | `nuget_fetcher/`, `nupkg_extractor/`, `reflection_catalog/` |
| Detection/planning | `plugin_detector/`, `scenario_planner/` |
| Generation | `generator/`, `llm_router/` |
| Validation | `verifier_bridge/` |
| Gates/lifecycle | `gates/` |
| Publishing | `publisher/` |
| Metrics | `metrics/` |

## Design Constraints

- API symbols come from reflected NuGet packages.
- Generation cannot proceed without source-of-truth proof.
- Blocked scenarios are preserved with explicit reasons.
- Publishing is PR-based and approval-gated.
- Evidence is written before exit, including partial and failed runs.

See [Pipeline Stages](pipeline-stages.md) and [File Contracts](../reference/file-contracts.md).
