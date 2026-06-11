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

## Developer Setup

After cloning the repo, install dev dependencies and activate git hooks:

```bash
pip install -e ".[dev]"   # installs pytest, ruff, pre-commit, and all dev deps
pre-commit install         # activates hooks — runs on every commit
```

**What the hooks enforce** (scope: `src/` and `tests/` only):
- **ruff** — lint check (blocking; exits non-zero on violations)
- **ruff-format** — code formatting (auto-formats on commit)
- **check-yaml** — YAML syntax validation (all YAML files)
- **end-of-file-fixer / trailing-whitespace** — file hygiene
- **compileall** — Python syntax check (`python -m compileall src/`)

`scripts/` and `reports/` are excluded from ruff enforcement (legacy generated files).

To run hooks manually without committing: `pre-commit run --all-files`
