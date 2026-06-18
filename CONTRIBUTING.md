# Contributing

Thank you for your interest in contributing to the Lowcode Example Generator.

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd lowcode-example-generator-gitlab

# Create a virtual environment
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# source .venv/bin/activate     # Linux/macOS

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

**Requirements**: Python 3.12 or later, .NET SDK 10.0 or newer (CI uses 10.0.204; for DllReflector builds only).

## Coding Standards

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting.
For documentation contributions, follow the [Documentation Style Guide](docs/development/style-guide.md) — key rules: reference pages instead of copying tables, use the guide template for new guides, and update `Last verified` frontmatter when making source-verified changes.

- **Line length**: 120 characters
- **Target Python**: 3.12+
- **Style**: ruff format (Black-compatible)
- **Lint rules**: pyflakes (F), pycodestyle (E/W), isort (I), pyupgrade (UP), simplify (SIM)

Run locally before committing:

```bash
ruff check src/ tests/
ruff format --check src/ tests/
```

## Testing

All changes must pass the existing test suite:

```bash
# Unit tests (required for all PRs)
python -m pytest tests/unit/ -v --timeout=60

# Integration tests (required for all PRs)
python -m pytest tests/integration/ -v --timeout=120

# Coverage check (threshold: 70%)
python -m pytest tests/unit/ --cov=src/plugin_examples --cov-report=term-missing --cov-fail-under=70
```

### Test Guidelines

- Place unit tests in `tests/unit/` mirroring the source tree structure
- Place integration tests in `tests/integration/`
- Use `tmp_path` fixtures for file system tests (no hardcoded paths)
- Use `pytest.mark.skipif` for tests requiring external dependencies (e.g., DllReflector)
- Name test functions `test_<what_it_tests>`
- Add timeout decorators for tests that could hang

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(gates): add publication freeze validator
fix(discovery): handle missing NuGet index gracefully
chore(ci): update ruff to 0.5
test(ehv): add EHV-09 security policy validator tests
docs(adr): add ADR-005 for mutation testing strategy
```

Prefixes: `feat`, `fix`, `chore`, `test`, `docs`, `refactor`, `ci`, `perf`.

## Pull Request Workflow

1. Create a feature branch from `main`: `git checkout -b feat/your-feature`
2. Make your changes following the coding standards above
3. Run the full test suite and ensure all tests pass
4. Run `ruff check src/ tests/` and fix any violations
5. Push your branch and open a merge request
6. Ensure all CI gates pass (ruff, bandit, compile-check, unit tests, integration tests)
7. Request review from the code owners listed in `CODEOWNERS`

### CI Gates (all must pass)

| Gate | Stage | Blocking |
|------|-------|----------|
| ruff-lint | lint | Yes |
| compile-check | lint | Yes |
| gate-isolation | lint | Yes |
| bandit-sast | lint | Yes |
| license-check | lint | Yes |
| unit-tests | test | Yes |
| integration-tests | test | Yes |
| secret-scan | lint | Yes |
| pip-audit | lint | No (advisory) |
| mypy-check | lint | No (advisory) |
| compliance-gate | test | Yes |

## Architecture Decisions

Significant design decisions are documented as ADRs in `docs/adr/`. Before proposing a large change, check existing ADRs and consider whether a new ADR is needed.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security policy.

## Code Ownership

Review routing is defined in `CODEOWNERS`. All changes to `src/`, `tests/`, and CI configuration require review from the designated team.
