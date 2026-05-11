# File Contracts

Audience: Operator, Contributor
Source of truth: `src/plugin_examples/runner.py`, `src/plugin_examples/evidence_layout.py`, writer modules under `src/plugin_examples/`

## Inputs

| Path | Contract |
|---|---|
| `pipeline/configs/families/*.yml` | Family configs loaded and schema-validated before a run. |
| `pipeline/schemas/*.json` | JSON schemas for configs, catalogs, scenarios, packets, validation results, denominators, and contracts. |
| `pipeline/contracts/{family}/*.json` | Scenario contracts for planned/generated examples. |
| `pipeline/prompts/*.md` | Prompt templates for generation and repair. |
| `templates/root-readme/*.j2` | README rendering templates. |
| `tools/DllReflector/` | .NET reflection tool built before reflection workflows. |

## Run-Scoped Outputs

| Path | Contract |
|---|---|
| `workspace/runs/{run_id}/` | One pipeline run. Contains generated artifacts and `pilot-report.json`. |
| `workspace/runs/{run_id}/pilot-report.json` | Structured run report with meta, stage results, comparison summary, gate summary, and verdict. |
| `workspace/runs/{run_id}/evidence/latest/` | Canonical evidence directory for a single run. |
| `workspace/runs/{run_id}/catalog/{family}/api-catalog.json` | Reflected API catalog for the family. |
| `workspace/runs/{run_id}/generated/` | Generated SDK-style C# projects. |

## Promoted Outputs

| Path | Contract |
|---|---|
| `workspace/verification/latest/families/{family}/` | Family-isolated promoted evidence. Prefer this over root aliases. |
| `workspace/verification/latest/` | Global aggregate evidence and backward-compatible aliases. Family-specific root aliases are deprecated. |
| `workspace/manifests/` | Promoted manifest-like files such as package lock, fixture registry, scenario catalog, and example index. |
| `workspace/pr-dry-run/` | Dry-run PR packages and README render outputs. |
| `workspace/queues/` | Completion queue data. |
| `workspace/verification/agent-metrics-post-ledger.jsonl` | Metrics duplicate-post ledger. |
| `~/.cache/plugin-examples/fixture-listings` | Fixture listing cache. |

## Common Evidence Files

| File | Meaning |
|---|---|
| `{family}-source-of-truth-proof.json` | NuGet/reflection/plugin namespace proof. |
| `product-inventory.json` | Product/plugin inventory. |
| `api-delta-report.json` | API delta result. |
| `example-impact-report.json` | Impact mapping. |
| `fixture-registry.json` | Fixture inventory. |
| `existing-examples-index.json` | Mined examples. |
| `stale-examples-report.json` | Existing example drift report. |
| `scenario-catalog.json` | Planned scenarios. |
| `blocked-scenarios.json` | Preserved blocked scenarios. |
| `catalog-hash-validation.json` | Catalog hash enforcement result. |
| `fixture-strategy-plan.json` | Fixture strategy by scenario. |
| `scenario-input-format-map.json` | Input/output format selection. |
| `llm-preflight.json` | LLM provider preflight result. |
| `example-index.json` | Generated example index. |
| `generated-fixtures.json` | Generated fixture records. |
| `llm-fewshot-patterns.json` | Few-shot pattern evidence. |
| `validation-results.json` | Dotnet restore/build/run results. |
| `runtime-failure-classifications.json` | Runtime failure classification. |
| `repair-attempts.json` | Repair attempts. |
| `reviewer-preflight.json` | External reviewer readiness. |
| `reviewer-results.json` | External reviewer result. |
| `publishing-report.json` | Publisher result. |
| `example-gate-results.json` | Per-example gate outcomes. |
| `aggregate-gate-results.json` | Aggregate gate counts. |
| `pr-candidate-manifest.json` | Publishable example manifest. |
| `scenario-feedback-updates.json` | Feedback for future planning. |
| `gate-results.json` | Overall gate verdict. |
| `example-lifecycle-records.json` | Lifecycle records and backlog input. |
| `run-to-run-comparison.json` | Optional comparison against a prior run. |

## Evidence Layout Rule

For family-specific evidence, use:

```text
workspace/verification/latest/families/{family}/{file}
```

The root `workspace/verification/latest/{file}` location exists for global aggregate files and backward-compatible aliases only.
