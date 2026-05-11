# Operator Quickstart

Audience: Operator

## Prerequisites

- Python 3.12 or newer.
- .NET SDK 8.0 for reflector and generated project validation.
- Dependencies installed with `pip install -e ".[dev]"` for test workflows or `pip install -e .` for basic operation.
- `GITHUB_TOKEN` only for live GitHub operations.

## Check the CLI

```powershell
python -m plugin_examples status
```

## Run a Dry-Run Pipeline

```powershell
python -m plugin_examples run --family cells --dry-run --template-mode --promote-latest
```

Inspect:

- `workspace/runs/{run_id}/pilot-report.json`
- `workspace/runs/{run_id}/evidence/latest/`
- `workspace/verification/latest/families/cells/` when promoted

## Next Steps

- Full command details: [CLI Reference](../reference/cli.md)
- Evidence files: [File Contracts](../reference/file-contracts.md)
- Monthly operation: [Monthly Maintenance](../operations/monthly-maintenance.md)
- Publishing: [Live Publishing](../operations/live-publishing.md)
