# Verifier Integration

## Overview

The pipeline integrates with the `example-reviewer` tool for publishing gate validation.

## Integration Mode

CLI subprocess: `python -m src.cli.main`

## Workflow

1. Generated examples are placed in workspace
2. `compile-verify --family {family} --json` validates compilation
3. `runtime-verify --family {family} --json` validates runtime
4. `final-review --family {family} --json` performs LLM review

## Failure Behavior

- Reviewer unavailable: blocks publishing (fail-closed)
- Compilation failure: blocks publishing
- Runtime failure: blocks publishing
- Review failure: blocks publishing

## Configuration

- Reviewer repo path configurable via `pipeline/configs/verifier.yml`
- Family configs must match between pipeline and reviewer

## See Also

- [example-reviewer-integration-surface.md](discovery/example-reviewer-integration-surface.md)
- [pipeline/configs/verifier.yml](../pipeline/configs/verifier.yml)
