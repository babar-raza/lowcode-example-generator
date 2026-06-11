# Plan Sources

Generated: 2026-06-11
Sprint: 20260611b-recruitize-current-project
Orchestrator Run: orchestrator-20260611b-harden

## PrimaryPlanSource

**Source:** Chat — Authorization Review output (independent reviewer verdict)
**Type:** AUTHORIZATION_GRANTED_WITH_LIMITS with 4 hardening taskcards
**File:** plans/from_chat/20260611_hardening_from_auth_review.md (to be created)

### ChatExtractedSteps

1. AUTH-HARDEN-001: Run `PYTHONPATH=src python -m pytest tests/unit --cov=src/plugin_examples --cov-report=term-missing --cov-fail-under=60` and capture output
2. AUTH-HARDEN-002: Refactor doctor.py to expose EHV-01..05 as individual HealthCheck entries (Option A) OR document delta formally (Option B)
3. AUTH-HARDEN-003: Produce integration test traceability matrix mapping 6 plan scenarios to existing/new tests
4. AUTH-HARDEN-004: Create `tests/unit/llm_router/test_router_enforces_approved_endpoint.py` with ≥2 tests for provider guard behavior
5. COMMIT: After all above pass, commit sprint source/test/docs files

### ChatExtractedGapsAndFixes

| Gap ID | Description | Fix |
|--------|-------------|-----|
| GAP-001 | Coverage gate not run | Run pytest --cov with fail-under=60 |
| GAP-002 | Doctor check count 9 < plan requirement 12 | Refactor to individual EHV checks OR document delta |
| GAP-003 | 5 audit tests added instead of 6 behavioral pipeline tests | Traceability matrix mapping 6 plan scenarios |
| GAP-004 | Legacy provider guard test not implemented | Add test_router_enforces_approved_endpoint.py |

### ChatMentionedFiles

- `src/plugin_examples/health/doctor.py`
- `tests/unit/llm_router/test_router_enforces_approved_endpoint.py`
- `tests/integration/` (existing suite for traceability mapping)
- `.local/rating-healing-runs/20260611b-recruitize-current-project/07a-coverage-gate.txt`
- `.local/rating-healing-runs/20260611b-recruitize-current-project/03a-integration-test-traceability.md`

### SubstantialityCheck

SUBSTANTIAL — 5 actionable steps, 4 concrete gaps with fixes, acceptance criteria and evidence commands specified for each

### ResolutionStrategy

Execute 4 hardening taskcards autonomously, then commit sprint artifacts

## SecondarySources

- `.local/rating-healing-runs/20260611b-recruitize-current-project/08-final-report.md`
- `C:\Users\prora\.claude\plans\peppy-frolicking-muffin.md` (original sprint plan)

## MissingCandidates

None — all required context present in chat

## Evidence-Based Rationale

Authorization review explicitly enumerated 4 hardening taskcards with exact commands, acceptance criteria, and evidence requirements. This is the highest-priority input per CHAT-FIRST rule.
