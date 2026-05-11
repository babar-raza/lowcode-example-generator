# Contributing

Audience: Contributor

## Ground Rules

- Code and schemas are the source of truth.
- Do not bypass gates.
- Do not publish directly to `main`.
- Preserve blocked scenarios with reasons.
- Keep docs canonical: guides link to references instead of copying tables.

## Main Code Areas

- CLI: `src/plugin_examples/__main__.py`
- Runner: `src/plugin_examples/runner.py`
- Config: `src/plugin_examples/family_config/`
- Validation: `src/plugin_examples/verifier_bridge/`
- Gates: `src/plugin_examples/gates/`
- Publisher: `src/plugin_examples/publisher/`

See [Repository Structure](repo-structure.md) and [Testing and CI](testing.md).
