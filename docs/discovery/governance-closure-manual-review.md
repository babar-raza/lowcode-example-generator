# Governance Closure Manual Verification Review

**Review date:** 2026-04-30
**Sprint reviewed:** Governance Closure Sprint
**Commit hash:** b501f67cef9ba3a87b86c00066ba384954c62910
**Overall verdict:** PARTIALLY_VERIFIED

---

## Executive Summary

The Governance Closure Sprint made substantial improvements to LLM provider policy
enforcement, discovery safety guards, and audit artifact creation. However, a critical
gap was found and fixed in this verification review:

**`_check_provider()` had no policy guard.** The `_call_provider()` function correctly
raises `LLMProviderError` for unapproved providers, but `_check_provider()` — which runs
at preflight to SELECT a provider — had no such guard. This means an unapproved provider
could pass preflight (`selected_provider` set to e.g. `gpt_oss`) even though the actual
call would later fail. The gap was identified, fixed, and tested in this review.

After the fix: unapproved providers are rejected at BOTH selection (preflight) and
execution (call) layers.

---

## A. Overall Verdict: PARTIALLY_VERIFIED

The sprint completed successfully in most areas. One critical security gap (`_check_provider`
missing guard) was found and closed. No generation, publishing, or Words/PDF pipeline runs
were made during this review.

---

## B. Critical Gap: `_check_provider()` Policy Enforcement

**Location:** `src/plugin_examples/llm_router/router.py`

**Gap (before fix):**
```python
# _check_provider() — NO guard at top:
def _check_provider(provider: str, ...) -> PreflightResult:
    result = PreflightResult(provider=provider)
    # MISSING: policy check here
    try:
        endpoint = _get_endpoint(provider, config)
        if provider in ("openai", "gpt_oss", "llm_professionalize"):
            ...  # Would proceed to HTTP call for ANY of these providers
```

**Fix applied:**
```python
def _check_provider(provider: str, ...) -> PreflightResult:
    result = PreflightResult(provider=provider)
    # Policy enforcement: reject unapproved providers at preflight
    if provider not in _APPROVED_PROVIDER_FAMILIES:
        result.error = (
            f"Provider family '{provider}' is not approved by policy. "
            f"Approved: {sorted(_APPROVED_PROVIDER_FAMILIES)}"
        )
        return result  # passed=False (all boolean fields default to False)
    ...
```

**New tests:**
- `test_check_provider_rejects_unapproved_at_preflight` — verifies gpt_oss, openai, azure_openai all return `passed=False`
- `test_run_preflight_does_not_select_unapproved_provider` — verifies `LLMRouter` never sets `selected_provider` to unapproved family

---

## C. Provider Policy Verification

| Check | Result |
|---|---|
| `_APPROVED_PROVIDER_FAMILIES` = `{llm_professionalize, ollama}` | VERIFIED |
| `_check_provider()` rejects unapproved providers | FIXED + VERIFIED |
| `_call_provider()` rejects unapproved providers | VERIFIED (was present before) |
| All family YAMLs use only approved providers | VERIFIED |
| `gpt-4o-mini` not in any pipeline call path | VERIFIED |
| `gpt-4o-mini` in NuGet XML classified as documentation | VERIFIED |
| No `openai` Python SDK usage outside approved locations | VERIFIED |

---

## D. Discovery Safety Verification

| Check | Result |
|---|---|
| `words.yml` status = `discovery_only` | VERIFIED |
| `pdf.yml` status = `discovery_only` | VERIFIED |
| `cells.yml` status = `active` | VERIFIED |
| `runner.py:_stage_load_config` raises for `discovery_only` | VERIFIED |
| `run --family words` exits non-zero | VERIFIED |
| `run --family pdf` exits non-zero | VERIFIED |
| TestDiscoveryOnlySafetyGuard: 9 tests pass | VERIFIED |

**Test quality note:** 3 of 9 safety guard tests are functionally identical
(`does_not_call_llm`, `does_not_generate_examples`, `does_not_publish`). All call
`_run_stage("load_config", 1, _stage_load_config, ctx)` and assert the same conditions.
They document intent at different pipeline stages but are redundant. Not incorrect.

---

## E. Config File Cleanup Verification

| Check | Result |
|---|---|
| `pipeline/configs/families/disabled/words.yml` deleted | VERIFIED |
| `pipeline/configs/families/disabled/pdf.yml` deleted | VERIFIED |
| `pipeline/configs/families/words.yml` exists + tracked in git | VERIFIED |
| `pipeline/configs/families/pdf.yml` exists + tracked in git | VERIFIED |
| `TestDuplicateConfigCleanup` (4 tests) pass | VERIFIED |

**Git rename note:** Git detected the new `words.yml` and `pdf.yml` as renames (`R`) from
`disabled/words.yml` and `disabled/pdf.yml` because content similarity exceeded the rename
threshold. This is correct behavior.

---

## F. Test Results

- **Total unit tests passing:** 488
- **TestProviderPolicy:** 18 tests (16 from sprint + 2 added in this review)
- **TestDiscoveryOnlySafetyGuard:** 9 tests
- **TestDuplicateConfigCleanup:** 4 tests
- **compileall src -q:** exits 0

---

## G. Artifacts Updated in This Review

| File | Change |
|---|---|
| `src/plugin_examples/llm_router/router.py` | Added `_check_provider()` policy guard |
| `tests/unit/test_llm_generation.py` | Added 2 preflight policy tests |
| `workspace/verification/latest/open-taskcard-closure-matrix.json` | Fixed test count; added `followup-llm-provider-policy-enforcement` as CLOSED |
| `workspace/verification/latest/family-generation-readiness-rank.json` | Added `generation_ready` and `generation_blocked_by` fields |
| `workspace/verification/latest/governance-closure-claim-audit.json` | Created (was missing) |
| `workspace/verification/latest/governance-closure-manual-review.json` | Created (was missing) |
| `docs/discovery/governance-closure-claim-audit.md` | Created (was missing) |
| `docs/discovery/governance-closure-manual-review.md` | Created (was missing) |
| `pipeline/configs/families/words.yml` | Staged in git index |
| `pipeline/configs/families/pdf.yml` | Staged in git index |

---

## H. Taskcard Status After Review

**Reopened and immediately closed:**
- `followup-llm-provider-policy-enforcement` — CLOSED (fix applied in this review)

**Remain closed (verified):**
- `followup-publisher-evidence-ordering`
- `followup-discovery-sweep-deps`
- `followup-github-api-403`
- `followup-discovery-only-safety`
- `followup-disabled-configs-cleanup`

**Remain open:**
- `followup-pdf-reflection-dedup` — blocks PDF discovery
- `followup-words-options-aware-review` — blocks Words generation
- `followup-words-role-classification-review` — blocks Words generation
- `followup-family-readiness-ranker-trust` — observability only
- `followup-fixture-token-ci` — CI integration

**Total: 11 taskcards tracked. 6 closed. 5 open.**

---

## I. Generation Policy (Immutable)

| Family | Generation | Discovery |
|---|---|---|
| Cells | ALLOWED | ALLOWED |
| Words | NOT ALLOWED | ALLOWED |
| PDF | NOT ALLOWED | ALLOWED (blocked at reflection) |
| All-family | NOT ALLOWED | N/A |

Words generation blocked by: `followup-words-options-aware-review` + `followup-words-role-classification-review`
PDF generation blocked by: `followup-pdf-reflection-dedup`

Do not enable Words or PDF generation until both blocking taskcards are `CLOSED_VERIFIED`.

---

## J. Next Sprint Recommendations

**Priority 1:** `followup-pdf-reflection-dedup`
- Implement assembly-identity deduplication in DllReflector dependency resolution
- Blocker: `FileLoadException: System.Text.Json, Version=8.0.0.0` — two packages extract same DLL
- Acceptance: PDF discovery succeeds; `pdf-source-of-truth-proof.json` written

**Priority 2 (parallel):** `followup-words-options-aware-review` + `followup-words-role-classification-review`
- Validate MailMergeOptions, ReportBuilderOptions, SplitOptions constraints
- Review MailMergeDataSource confidence 0.70 classification
- Both must be `CLOSED_VERIFIED` before Words generation enabled

**Priority 3:** `followup-fixture-token-ci`
- Document `GITHUB_TOKEN` in CI workflow environment variables
- Medium priority — blocks full CI integration but not local generation
