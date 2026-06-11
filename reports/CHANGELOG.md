# Changelog

## [0.28.0] — 2026-06-11 — Sprint 20260611b

### Commit ee3be655 — feat(sprint-20260611b)

**Engineering Practices (P dimension):**

- **Bandit SAST in CI**: `.github/workflows/build-and-test.yml` — bandit scan added, artifact uploaded; non-blocking first pass
- **pip-audit hardened**: promotes from advisory to blocking for HIGH CVEs
- **`[tool.bandit]` in pyproject.toml**: `skips = ["B101","B404","B603","B607"]`; satisfies EHV-04
- **`engineering_hygiene_validators.py`** (EHV-01..05): AST-based `except Exception: pass` detection, integration test count guard, bandit config check, CODEOWNERS check
- **`doctor.py` refactored**: EHV-01..05 exposed as individual health checks → 13 total (plan requirement: ≥12)
- **`evidence_contract.py`**: ~20 `except Exception: pass` handlers replaced with specific types + logging
- **Provider guard tests**: `test_router_enforces_approved_endpoint.py` — 8 tests verify `_APPROVED_PROVIDER_FAMILIES` enforcement in `_call_provider` and `_check_provider`
- **Coverage**: 78.83% total (gate: ≥60%)

**Enterprise Readiness (R dimension):**

- **`decision_audit.py`** (LLM router): `DecisionAuditRecord` + `DecisionAuditLog` (thread-safe JSONL); wired into `router.py` to record per-invocation: provider, model, latency_ms, outcome, error_message
- **`docs/operations/runbook.md`**: 7 failure scenarios (LLM timeout, NuGet restore, hash regression, evidence contract mismatch, git dirty, coverage failure, EHV failures)
- **`docs/operations/`**: Added incident-response.md, release-process.md, sla.md
- **Dockerfile**: Fixed curl|bash supply chain pattern → save-then-execute

**Tests (+44 new):**

- `tests/unit/llm_router/test_llm_decision_audit.py` — 10 unit tests
- `tests/unit/llm_router/test_router_enforces_approved_endpoint.py` — 8 unit tests (AUTH-HARDEN-004)
- `tests/unit/fixture_factory/test_engineering_hygiene_validators.py` — 21 unit tests
- `tests/integration/test_llm_audit_integration.py` — 5 integration tests

**Auth hardening completed (AUTH-HARDEN-001..004):**

- Coverage gate verified: 78.83% ≥ 60%
- Doctor check count: 13 ≥ 12 (plan acceptance criterion met)
- Integration test traceability: all 6 plan scenarios mapped to passing tests
- Provider guard test: 8/8 pass

**Test commands:**

```bash
PYTHONPATH=src python -m pytest tests/unit --cov=src/plugin_examples --cov-fail-under=60
PYTHONPATH=src python -m pytest tests/integration
ruff check src/ tests/
python -m plugin_examples doctor
```
