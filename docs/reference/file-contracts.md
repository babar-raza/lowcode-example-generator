# File and Evidence Contracts

Audience: Operator, Contributor

Source of truth: `src/plugin_examples/runner.py`, `src/plugin_examples/evidence_layout.py`, writer modules under `src/plugin_examples/`

Last verified from audit: 2026-05-25

## Primary Inputs

| Path | Contract |
|---|---|
| `pipeline/configs/families/*.yml` | Family configs loaded and schema-validated before a run. |
| `pipeline/configs/families/disabled/*.yml` | Disabled configs. The loader rejects these paths. |
| `pipeline/schemas/*.schema.json` | JSON schemas for configs, catalogs, scenarios, packets, validation results, denominators, manifests, and contracts. |
| `pipeline/configs/denominators/*.json` | Family denominator models and source version/catalog hash truth. |
| `pipeline/contracts/{family}/*.json` | Scenario contracts for planned/generated examples. |
| `pipeline/format-authority/manifest.json` | Format authority manifest used by publication/format checks. |
| `pipeline/format-authority/contracts/*.json` | Format authority contracts. |
| `pipeline/prompts/*.md` | Prompt templates for generation and repair. |
| `templates/root-readme/*.j2` | README rendering templates. |
| `tools/DllReflector/` | .NET reflection helper project. |

## Run-Scoped Directories

| Path | Contract |
|---|---|
| `workspace/runs/{run_id}/` | One pipeline run. Contains generated artifacts and `pilot-report.json`. |
| `workspace/runs/{run_id}/packages/{family}/` | Primary NuGet package cache/download target for the run. |
| `workspace/runs/{run_id}/packages/{family}/deps/` | Dependency package cache/download target for the run. |
| `workspace/runs/{run_id}/extracted/{family}/` | Extracted package assemblies/XML and dependencies. |
| `workspace/runs/{run_id}/catalog/{family}/api-catalog.json` | Reflected API catalog for the family. |
| `workspace/runs/{run_id}/generated/{family}/` | Generated SDK-style C# projects. |
| `workspace/runs/{run_id}/evidence/latest/` | Canonical evidence directory for a single run. |

## Run-Scoped Files

| Path | Contract |
|---|---|
| `workspace/runs/{run_id}/pilot-report.json` | Structured run report with metadata, stage results, comparison summary, gate summary, environment, and verdict. |
| `workspace/runs/{run_id}/packages/{family}/dependency-manifest.json` | Dependency resolution output when dependency resolution runs. |
| `workspace/runs/{run_id}/generated/{family}/.../Program.cs` | Generated example source. |
| `workspace/runs/{run_id}/generated/{family}/.../*.csproj` | Generated project file. |
| `workspace/runs/{run_id}/generated/{family}/.../example.manifest.json` | Generated example manifest. |
| `workspace/runs/{run_id}/generated/{family}/.../expected-output.json` | Expected output contract when generated. |

## Promoted Outputs

| Path | Contract |
|---|---|
| `workspace/verification/latest/families/{family}/` | Family-isolated promoted evidence. Prefer this for family-specific evidence. |
| `workspace/verification/latest/` | Global aggregate evidence plus backward-compatible aliases. Family-specific root aliases are deprecated. |
| `workspace/manifests/` | Promoted manifest-like files such as package lock, fixture registry, existing examples index, scenario catalog, and example index. |
| `workspace/pr-dry-run/` | Dry-run PR packages and README render outputs. |
| `workspace/verification/agent-metrics-post-ledger.jsonl` | Metrics duplicate-post ledger. |

## Common Evidence Files

| File | Meaning |
|---|---|
| `{family}-source-of-truth-proof.json` | NuGet/reflection/plugin namespace proof. |
| `product-inventory.json` | Product/plugin inventory. |
| `api-delta-report.json` | API delta result. |
| `example-impact-report.json` | Impact mapping. |
| `package-lock.json` | Resolved package and dependency lock data. |
| `fixture-registry.json` | Fixture inventory. |
| `existing-examples-index.json` | Mined existing examples. |
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
| `semantic-output-validation-results.json` | Semantic output validation results. |
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
| `release-status.json` | Release status report. |
| `family-publish-readiness.json` | Publish target readiness report. |
| `family-repo-access-resolution.json` | GitHub repo access probe report. |
| `publish-permission-probe.json` | Publish permission probe report. |

## Taskcard Matrix

| Path | Contract |
|---|---|
| `workspace/verification/latest/open-taskcard-closure-matrix.json` | Authoritative taskcard matrix JSON. |
| `docs/development/open-taskcard-closure-matrix.md` | Generated markdown view produced by `sync-taskcard-docs`. Do not edit directly. |

## Evidence Layout Rule

For family-specific promoted evidence, use:

```text
workspace/verification/latest/families/{family}/{file}
```

The root `workspace/verification/latest/{file}` location exists for global aggregate files and backward-compatible aliases only.

## Related Pages

- [CLI Reference](cli.md)
- [Gates and Verdicts](gates-and-verdicts.md)
- [Publishing and GitHub](publishing-and-github.md)
