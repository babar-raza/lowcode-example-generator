# Root Orphans

Contract: `docs/` root is reserved for `docs/README.md` only, plus meta folders such as `docs/_audit/` and `docs/_archive/`. Files directly under `docs/` other than `README.md` are root orphans and must be triaged.

Root sweep command evidence: `Get-ChildItem docs -File` returned `monthly-runbook.md` and `verifier-integration.md`. No `docs/README.md` was present.

| orphan_path | brief content summary | likely target area | action | canonical merge target | risks/notes |
|---|---|---|---|---|---|
| `docs/monthly-runbook.md` | Short monthly operation runbook. Overlaps with the more complete `docs/publishing/monthly-maintenance-runbook.md` and CI workflow `.github/workflows/monthly-package-refresh.yml`. | ops | merge | `docs/publishing/monthly-maintenance-runbook.md` | Must reconcile commands with current CLI in `src/plugin_examples/__main__.py` and monthly workflow. Do not keep as root file. |
| `docs/verifier-integration.md` | Short note about verifier/example-reviewer integration. Overlaps with `docs/discovery/example-reviewer-integration-surface.md`, `docs/discovery/example-reviewer-fixture-system.md`, and code in `src/plugin_examples/verifier_bridge/`. | reference/dev | merge | `docs/discovery/example-reviewer-integration-surface.md` or future canonical verifier reference | Needs code-backed refresh from `verifier_bridge/bridge.py`, `reviewer_preflight.py`, `dotnet_runner.py`, `output_validator.py`. Do not keep as root file. |

## Missing Root Canonical File

`docs/README.md` is missing. Under the root hygiene contract, create it later as a docs index after triage. Suggested scope: point humans and LLMs to canonical overview, operator runbooks, architecture/reference, and archive policy.
