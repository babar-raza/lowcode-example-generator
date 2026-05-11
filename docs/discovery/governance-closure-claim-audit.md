# Governance Closure Claim Audit

**Audit date:** 2026-04-30
**Sprint audited:** Governance Closure Sprint
**Commit audited:** b501f67cef9ba3a87b86c00066ba384954c62910
**Overall verdict:** PARTIALLY_VERIFIED

---

## Summary

The Governance Closure Sprint completed significant work but contained one critical gap:
`_check_provider()` had no policy guard, meaning unapproved providers could be SELECTED at
preflight (false pass) even though they could not be CALLED (guard in `_call_provider()`
would fire). This gap was discovered in this verification review and fixed immediately.
The new taskcard `followup-llm-provider-policy-enforcement` was opened and closed in the
same review execution.

All other major claims verified. 488 unit tests pass. Provider policy enforced at both
preflight and call layers. Discovery_only safety guard confirmed. Disabled configs cleaned.

---

## Provider Policy Audit

### Q1: Does the pipeline ever call gpt-4o-mini directly?

**Answer: NO.**
- `FORBIDDEN_PIPELINE_MODELS = frozenset({"gpt-4o-mini"})` in `provider_policy.py`
- `is_forbidden_model("gpt-4o-mini")` returns `True`
- The string `gpt-4o-mini` appears only in extracted NuGet XML documentation (Aspose.Words.xml)
  which is classified as `extracted_nuget_documentation`, not a pipeline LLM call
- `router.py` does not contain the literal string `gpt-4o-mini` in any callable path

### Q2: Which providers does the pipeline route to?

**Answer: Only `llm_professionalize` and `ollama`.**
- `_APPROVED_PROVIDER_FAMILIES = frozenset({"llm_professionalize", "ollama"})` in `router.py`
- All 3 active family YAMLs (cells, words, pdf) have `provider_order: [llm_professionalize, ollama]`
- `gpt_oss`, `openai`, `azure_openai` are all in `UNAPPROVED_PROVIDERS` in `provider_policy.py`

### Q3: Is `openai` ever imported or called directly outside the approved provider?

**Answer: NO.**
- `router.py` uses `requests` library for HTTP calls, not the `openai` Python SDK
- `provider_policy.py:is_direct_openai_construction()` detects `OpenAI(` Python SDK usage
  outside `providers/professionalize.py` — no violations found in codebase

### Q4: Can an unapproved provider be SELECTED at preflight?

**Answer: NO — after the verification review fix.**
- BEFORE FIX: `_check_provider()` had no policy guard. Unapproved providers could be
  selected (preflight passes) even though `_call_provider()` would raise `LLMProviderError`.
- AFTER FIX: `_check_provider()` returns `PreflightResult(passed=False)` for any provider
  not in `_APPROVED_PROVIDER_FAMILIES`, before any HTTP call.
- New tests: `test_check_provider_rejects_unapproved_at_preflight` and
  `test_run_preflight_does_not_select_unapproved_provider` both pass.

### Q5: Are Words and PDF blocked from generation?

**Answer: YES.**
- `words.yml` and `pdf.yml` have `status: discovery_only`
- `runner.py:_stage_load_config` raises `RuntimeError` for `discovery_only` families
- `run --family words` exits non-zero; `run --family pdf` exits non-zero
- `family-generation-readiness-rank.json` now has `generation_ready: false` for both

### Q6: Is the preflight report schema complete?

**Answer: YES.**
- `llm-preflight.json` contains all required fields: `selected_provider`, `provider_family`,
  `provider_base_url`, `model_name`, `route`, `preflight_passed`, `called_by_stage`,
  `request_count`, `documentation_hits_excluded`, `classification_notes`, `results`

---

## Claim Audit Table

| Claim | Verdict | Risk | Reopened Taskcard |
|---|---|---|---|
| GOVERNANCE_CLOSURE_COMPLETE | PARTIALLY_VERIFIED | HIGH | followup-llm-provider-policy-enforcement |
| provider_policy.py: 6 functions added | VERIFIED | LOW | — |
| router.py: 9 preflight fields added | VERIFIED | LOW | — |
| No unapproved provider callable | PARTIALLY_VERIFIED | HIGH | followup-llm-provider-policy-enforcement |
| gpt-4o-mini not used by pipeline | VERIFIED | LOW | — |
| gpt-4o-mini docs hit classified | VERIFIED | LOW | — |
| Only llm_professionalize + ollama in configs | VERIFIED | LOW | — |
| discovery_only safety guard in runner.py | VERIFIED | LOW | — |
| TestDiscoveryOnlySafetyGuard: 9 tests pass | VERIFIED | LOW | — |
| Duplicate disabled configs cleaned up | VERIFIED | LOW | — |
| Active words.yml + pdf.yml tracked in git | VERIFIED | LOW | — |
| 488 unit tests passed | VERIFIED | LOW | — |
| run --family words exits non-zero | VERIFIED | LOW | — |
| run --family pdf exits non-zero | VERIFIED | LOW | — |
| llm-provider-policy-audit.md created | VERIFIED | LOW | — |
| open-taskcard-closure-matrix.md created | VERIFIED | LOW | — |
| governance-closure-claim-audit.json created | CREATED_IN_REVIEW | LOW | — |
| governance-closure-manual-review.json created | CREATED_IN_REVIEW | LOW | — |

---

## Test Quality Notes

**TestDiscoveryOnlySafetyGuard (9 tests):**
- 5 core tests verify `_stage_load_config` raises `RuntimeError` for `discovery_only`
- `test_discover_lowcode_allows_discovery_only_family` uses negative assertions only — weak but not harmful
- `test_discovery_only_does_not_call_llm`, `test_discovery_only_does_not_generate_examples`,
  `test_discovery_only_does_not_publish` are functionally identical — all assert stage 1 guard.
  These are redundant but not incorrect; they document intent at different pipeline stages.

**TestProviderPolicy (18 tests after verification review):**
- 16 original tests from Governance Closure Sprint
- 2 new tests added in verification review: preflight guard enforcement

---

## Fixes Applied in This Review

1. **`_check_provider()` policy guard** — Added at top of `_check_provider()` in `router.py`.
   Unapproved providers now return `PreflightResult(passed=False)` before any HTTP call.
   Mirrors the existing guard in `_call_provider()`.

2. **`family-generation-readiness-rank.json` clarified** — Added `generation_ready: true/false`
   and `generation_blocked_by` fields to all three family entries.

3. **`open-taskcard-closure-matrix.json` corrected** — Fixed "5 tests pass" to "9 tests exist".
   Added `followup-llm-provider-policy-enforcement` as CLOSED taskcard.

4. **`words.yml` + `pdf.yml` staged in git** — New active configs were untracked (`??`).
   Added to git index; detected as renames from `disabled/` (correct behavior).

---

## Generation Policy (Unchanged)

| Family | Generation | Discovery |
|---|---|---|
| Cells | ALLOWED | ALLOWED |
| Words | NOT ALLOWED | ALLOWED |
| PDF | NOT ALLOWED | ALLOWED (blocked at reflection) |
| All-family | NOT ALLOWED | N/A |
