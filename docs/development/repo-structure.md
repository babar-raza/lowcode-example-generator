# Repository Structure

Audience: Contributor
Last verified: 2026-06-17

| Path | Purpose |
|---|---|
| `src/plugin_examples/` | Python package implementation (38 sub-packages). |
| `src/plugin_examples/agents/` | Multi-agent framework (A6 Coordinated): base, registry, dispatcher, context, protocol, builtin. |
| `src/plugin_examples/sprint_governance/` | Sprint loop controller, taskcard FSM, quality scorer, summary parser, evidence bundler, project adapter. |
| `src/plugin_examples/probe_executor/` | Probe execution orchestration and promotion. |
| `src/plugin_examples/probe_generator/` | C# probe template generation for capability-registry entries. |
| `src/plugin_examples/psal/` | PSAL multi-family orchestration loop. |
| `src/plugin_examples/compliance/` | Incident register, release receipt, audit trail, compliance reporter. |
| `pipeline/configs/` | Runtime configuration (family YAMLs, metrics, denominators). |
| `pipeline/plugin-capability-registry/` | Non-LowCode plugin capability registry (18 family YAMLs + `schema.yaml`). |
| `pipeline/plugin-code-registry/` | Plugin code registry entries per family. |
| `pipeline/schemas/` | JSON schemas (11 total: api-catalog, family-config, scenario, validation-result, etc.). |
| `pipeline/contracts/` | Scenario contracts (6 LowCode families). |
| `pipeline/prompts/` | LLM prompt templates. |
| `pipeline/policies/` | Policy definitions. |
| `pipeline/format-authority/` | Format authority manifest and contracts. |
| `autonomous/supervisor/prompts/` | Supervisor prompt assets (P1 audit, P2 harden, P3 execute, loop controller). |
| `autonomous/supervisor/contracts/` | Machine-readable governance contracts (9 YAML files). |
| `plans/` | Active sprint and governance plans. |
| `templates/` | README templates. |
| `tools/DllReflector/` | .NET API reflection tool (targets net8.0). |
| `tests/` | Unit and integration test folders. |
| `scripts/` | Operational and utility helper scripts (see `scripts/README.md`). |
| `workspace/` | Runtime output, evidence, manifests, dry-run packages (gitignored from remote). |
| `docs/` | Current documentation (see `docs/README.md` for navigation). |
| `docs/_archive/` | Historical evidence (sprint reports, wave analyses, discovery sessions). |
| `docs/_audit/` | Documentation audit staging area. |

See [File Contracts](../reference/file-contracts.md) for runtime output contracts.
