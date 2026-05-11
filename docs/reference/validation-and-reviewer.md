# Validation and Reviewer

Audience: Operator, Contributor
Source of truth: `src/plugin_examples/verifier_bridge/`

## Dotnet Validation

Generated projects are validated through:

1. `dotnet restore`
2. `dotnet build`
3. `dotnet run`, unless `--skip-run` is set
4. Output validation when configured

Implementation: `src/plugin_examples/verifier_bridge/dotnet_runner.py`.

Results are written to `validation-results.json`.

## Output Validation

Implementation: `src/plugin_examples/verifier_bridge/output_validator.py`.

Supported semantic checks include text, JSON, HTML, PDF, image, and XLSX output handling. Output validation records pass/fail state and issues for each generated project.

## External Example Reviewer

Implementation:

- `src/plugin_examples/verifier_bridge/reviewer_preflight.py`
- `src/plugin_examples/verifier_bridge/bridge.py`

The reviewer path is resolved from `EXAMPLE_REVIEWER_PATH` or explicit reviewer path arguments in bridge code.

Reviewer evidence:

- `reviewer-preflight.json`
- `reviewer-results.json`

## Required vs Optional

CLI flags can require validation or reviewer availability:

- `--require-validation`
- `--require-reviewer`

If a later optional stage fails and the corresponding requirement flag is not set, the runner can mark the stage degraded rather than hard-failing the run.

See:

- [CLI Reference](cli.md)
- [Gates and Verdicts](gates-and-verdicts.md)
- [File Contracts](file-contracts.md)
