# PDF Wave 1 Preflight Review

**Sprint:** Wave 1 — PDF Splitter and Optimizer Completion
**Date:** 2026-05-07
**Gate 0 Verdict:** PASS

---

## Summary

All prerequisite evidence has been manually inspected and verified. Gate 0 passes with no blocking contradictions. Two stale artifacts are documented. Four source code changes are required before execution.

---

## Artifact Review

| Artifact | Status | Notes |
|----------|--------|-------|
| docs/plans/coverage-100-final-execution-plan.md | MISSING | Planned output of this sprint |
| coverage-100-plan-hardening-preflight.json | MISSING | Planned output of this sprint |
| pdf-splitter-optimizer-current-root-cause-verification.json | MISSING | Being created in this sprint |
| coverage-100-wave1-readiness-review.json | MISSING | Being created in this sprint |
| open-taskcard-closure-matrix.json | VERIFIED | 62/13/48 — followup-pdf-splitter/optimizer-options-class both OPEN HIGH |
| docs/discovery/open-taskcard-closure-matrix.md | VERIFIED | In sync with JSON |
| linked-nibbling-hamster.md | VERIFIED | Wave 1 plan documented; retry in router.py listed as required |
| pdf-source-of-truth-proof.json | VERIFIED | 101 types, 71 methods |
| pdf-type-role-classification.json | VERIFIED | 25 WORKFLOW_ROOT + 75 support = 100 classified |
| pdf-options-aware-review.json | STALE | AddOutput(FileSaveTarget) error in templates; use pdf-fixture-strategy-review.json |
| pdf-fixture-strategy-review.json | VERIFIED | 4 validated fixture strategies |
| pdf-pilot-api-truth-table.json | VERIFIED | Merger/TextExtractor fully documented |
| pdf-example-lifecycle-summary.json | VERIFIED | GATE_3_PASS; 2 published, 2 backlogged, 0 dropped |
| families/pdf/example-lifecycle.json | VERIFIED | 2 PASS, 2 EXCLUDED_BY_SCOPE |
| backlog/pdf/examples-backlog.json | VERIFIED | 2 HIGH priority entries |
| family-generation-readiness-rank.json | VERIFIED | PDF restricted to pilot |
| pipeline/configs/families/pdf.yml | VERIFIED | allowed_types: [Merger, TextExtractor] — will change |
| packet_builder.py | VERIFIED | _pdf_type_hints injecting SplitOptions/OptimizeOptions at lines 168-174 |
| code_generator.py | VERIFIED | PluginOptions = ERROR at line 550; repair filter gap identified |
| runner.py | VERIFIED | 1,381 lines; NO timeout retry |
| router.py | VERIFIED | 428 lines; NO retry; 120s timeout single-shot |
| planner.py | VERIFIED | allowed_types enforcement active — will block Splitter/Optimizer until config change |
| example_lifecycle.py | VERIFIED | No silent drops; backlog for failures |
| publisher.py | VERIFIED | APPROVE_LIVE_PR required |

---

## Source Code Verification

| Claim | Verified | Detail |
|-------|---------|--------|
| packet_builder injects SplitOptions | YES | Lines 133-174 `_pdf_type_hints["splitter"]` |
| packet_builder injects OptimizeOptions | YES | Lines 133-174 `_pdf_type_hints["optimizer"]` |
| Injection is actively used | YES | Lines 168-174 — `if type_short in _pdf_type_hints` |
| PluginOptions blocked as ERROR | YES | code_generator.py line 550 — added to issues list |
| repair filter includes code pattern | YES | Filter matches "REQUIRED: exact usage pattern" at line 82 |
| repair filter includes options class | NO | "REQUIRED: options class is" NOT in filter — gap to fix |
| runner.py has timeout retry | NO | Confirmed missing |
| router.py has timeout retry | NO | _call_openai_compatible/_call_ollama: single attempt, no retry |
| pdf.yml excludes Splitter/Optimizer | YES | allowed_types: [Merger, TextExtractor] at lines 61-62 |

---

## Required Changes for Wave 1

1. **router.py** — Add retry with backoff (max 2 retries: 30s, 60s) to `_call_openai_compatible` and `_call_ollama` for `Timeout` and `ConnectionError` only. Do NOT retry policy failures or deterministic validation errors.

2. **code_generator.py** — Add `"REQUIRED: options class is" in c` to repair filter at line 82. This ensures the LLM sees the explicit options class name in repair prompts, not just the code pattern.

3. **pdf.yml** — Change `allowed_types: [Merger, TextExtractor]` to `[Merger, TextExtractor, Splitter, Optimizer]`.

4. **tests** — Add 8 new tests covering timeout retry, no-retry on policy failure, and PDF constraint injection.

---

## Gate 0 Pass Criteria

| Criterion | Pass? |
|-----------|-------|
| SplitOptions/OptimizeOptions injection verified in current code | YES |
| PluginOptions blocking validator verified | YES |
| pdf.yml currently excludes Splitter/Optimizer | YES |
| runner.py timeout retry confirmed missing | YES |
| PDF lifecycle/backlog consistent | YES |
| Taskcard JSON/MD match | YES |
| No contradictory evidence | YES |

**Gate 0: PASS — proceed to Phase 1 implementation**
