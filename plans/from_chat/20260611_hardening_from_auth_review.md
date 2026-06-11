# Hardening Plan — Auth Review Taskcards

Source: Authorization Review (AUTHORIZATION_GRANTED_WITH_LIMITS)
Date: 2026-06-11
Sprint: 20260611b-recruitize-current-project

## Context

Sprint 20260611b completed implementation but the independent authorization review identified 4 hardening gaps before sprint closeout can be authorized. This plan executes those 4 taskcards autonomously.

## Goals

1. Satisfy all plan Phase 7 verification gates
2. Achieve doctor check count ≥ 12 OR formally document the delta
3. Establish test traceability for 6 plan-specified integration scenarios
4. Add provider guard unit test

## Assumptions (UNVERIFIED until checked)

- A1: Coverage is still ≥ 60% after +36 new tests (UNVERIFIED — must run gate)
- A2: doctor.py refactor to individual EHV checks is feasible without breaking imports (UNVERIFIED)
- A3: Existing integration tests cover ≥ 4 of 6 plan scenarios (UNVERIFIED — need mapping)
- A4: _APPROVED_PROVIDER_FAMILIES is accessible/testable in router.py (UNVERIFIED)

## Steps

1. AUTH-HARDEN-001: Run coverage gate
   - Command: `PYTHONPATH=src python -m pytest tests/unit --cov=src/plugin_examples --cov-report=term-missing --cov-fail-under=60`
   - Output: `.local/rating-healing-runs/20260611b-recruitize-current-project/07a-coverage-gate.txt`

2. AUTH-HARDEN-002: Refactor doctor.py (Option A)
   - Modify `run_all_checks()` to call each EHV validator individually
   - Each EHV-01..05 becomes its own HealthCheck entry
   - Verify: doctor shows ≥ 14 checks

3. AUTH-HARDEN-003: Integration test traceability
   - Inspect existing integration tests for the 6 plan scenarios
   - Write `.local/rating-healing-runs/20260611b-recruitize-current-project/03a-integration-test-traceability.md`
   - Add any missing tests

4. AUTH-HARDEN-004: Provider guard test
   - Create `tests/unit/llm_router/test_router_enforces_approved_endpoint.py`
   - ≥ 2 tests: approved family accepted, unapproved family rejected

5. Final verification: run full suite + ruff + doctor

6. Commit all sprint files

## Acceptance Criteria

- [ ] Coverage gate: exit 0, total ≥ 60%
- [ ] Doctor: ≥ 12 checks (target: ≥ 14 with individual EHV)
- [ ] Traceability: all 6 plan scenarios mapped to passing tests
- [ ] Provider guard: ≥ 2 tests pass
- [ ] Ruff: 0 violations
- [ ] Integration tests: all pass
- [ ] Sprint files committed

## Evidence Commands

```bash
PYTHONPATH=src python -m pytest tests/unit --cov=src/plugin_examples --cov-report=term-missing --cov-fail-under=60
python -m plugin_examples doctor
ruff check src/ tests/
pytest tests/unit/llm_router/test_router_enforces_approved_endpoint.py -v
pytest tests/integration/ -v
```

## Risks + Rollback

- Risk: doctor.py refactor breaks imports → rollback: restore original single-check pattern; use Option B instead
- Risk: provider guard test reveals router doesn't actually enforce guard → fix the guard before adding test

## Open Questions

(Must be empty by end)
