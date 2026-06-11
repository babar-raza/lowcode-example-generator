# Task Backlog — Orchestrator Run 20260611b-harden

Generated: 2026-06-11
Sprint: 20260611b-recruitize-current-project

| ID | Title | Owner | Status | Acceptance Criteria | Risk |
|----|-------|-------|--------|--------------------|----|
| AUTH-HARDEN-001 | Run coverage gate | A-Discovery | COMPLETE | Coverage ≥ 60%, exit 0 | LOW |
| AUTH-HARDEN-002 | Refactor doctor.py to individual EHV checks | B-Implementation | COMPLETE | Doctor shows ≥ 12 checks | MEDIUM |
| AUTH-HARDEN-003 | Integration test traceability matrix | D-Docs | COMPLETE | All 6 plan scenarios mapped | LOW |
| AUTH-HARDEN-004 | Legacy provider guard test | C-Tests | COMPLETE | ≥ 2 tests pass | LOW |
| COMMIT-001 | Commit all sprint source/test/docs files | B-Implementation | PENDING | git status clean for sprint files | LOW |

## Workstreams

### Stream 1: Verification (AUTH-HARDEN-001) — COMPLETE
- Coverage gate: 78.83% ≥ 60% ✓
- Evidence: .local/rating-healing-runs/20260611b-recruitize-current-project/07a-coverage-gate.txt

### Stream 2: Source Change (AUTH-HARDEN-002) — COMPLETE
- doctor.py refactored to expose 5 individual EHV checks
- Doctor now shows 13 checks (≥ 12 requirement met)

### Stream 3: Tests (AUTH-HARDEN-004) — COMPLETE
- 8 new provider guard tests, all passing
- File: tests/unit/llm_router/test_router_enforces_approved_endpoint.py

### Stream 4: Docs/Evidence (AUTH-HARDEN-003) — COMPLETE
- Traceability matrix: all 6 plan scenarios covered
- File: .local/.../03a-integration-test-traceability.md

### Stream 5: Commit — PENDING
- Awaiting final ruff check + doctor verification
