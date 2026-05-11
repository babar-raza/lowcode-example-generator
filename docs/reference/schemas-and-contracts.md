# Schemas and Contracts

Audience: Contributor
Source of truth: `pipeline/schemas/`, `pipeline/contracts/`, tests under `tests/unit/`

## Schemas

| Schema | Purpose |
|---|---|
| `pipeline/schemas/family-config.schema.json` | Family YAML validation. |
| `pipeline/schemas/api-catalog.schema.json` | Reflected API catalog shape. |
| `pipeline/schemas/scenario.schema.json` | Scenario shape. |
| `pipeline/schemas/scenario-packet.schema.json` | Prompt packet shape. |
| `pipeline/schemas/scenario-contract.schema.json` | Scenario contract shape. |
| `pipeline/schemas/example-manifest.schema.json` | Example manifest shape. |
| `pipeline/schemas/validation-result.schema.json` | Validation result shape. |
| `pipeline/schemas/denominator.schema.json` | Denominator model shape. |

## Contracts

Scenario contracts live under `pipeline/contracts/{family}/`.

Current contract families include Cells, Diagram, PDF, and Words.

## Tests

Relevant tests:

- `tests/unit/test_family_config.py`
- `tests/unit/test_denominator_model.py`
- `tests/unit/test_scenario_contracts.py`
- `tests/unit/test_catalog_hash_enforcement.py`
