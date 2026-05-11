# Pipeline Stages

Audience: Contributor, Operator
Source of truth: `src/plugin_examples/runner.py`

The runner executes the stage list in `STAGE_DEFINITIONS`.

| Order | Stage | Main output |
|---:|---|---|
| 1 | `load_config` | Loaded family config |
| 2 | `nuget_fetch` | Download manifest |
| 3 | `dependency_resolution` | Dependency manifest/package lock |
| 4 | `extraction` | DLL/XML extraction record |
| 5 | `reflection` | API catalog |
| 6 | `plugin_detection` | Source-of-truth proof |
| 8 | `api_delta` | API delta report |
| 9 | `impact_mapping` | Example impact report |
| 10 | `fixture_registry` | Fixture registry |
| 11 | `example_mining` | Existing examples index/stale report |
| 12 | `scenario_planning` | Scenario catalog and blocked scenarios |
| 13 | `llm_preflight` | LLM preflight result |
| 14 | `generation` | Generated projects and example index |
| 15 | `validation` | Restore/build/run/output validation results |
| 16 | `reviewer` | Reviewer preflight/results |
| 17 | `publisher` | Publishing report |

Stage 7, `source_of_truth_gate`, is represented in the definition list but combined into plugin detection.

After stages complete, the runner writes per-example gates, aggregate gates, PR candidate manifest, scenario feedback, gate results, lifecycle evidence, and optional run-to-run comparison.

See [Gates and Verdicts](../reference/gates-and-verdicts.md).
