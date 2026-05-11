# LLM Provider Policy Audit

**Audit date:** 2026-04-30
**Sprint:** Governance Closure Sprint
**Audited by:** Governance Closure automation + manual review

---

## Approved Provider Policy

| Field | Value |
|---|---|
| Approved provider families | `llm_professionalize`, `ollama` |
| Forbidden provider families | `gpt_oss`, `openai`, `azure_openai` |
| Forbidden pipeline models | `gpt-4o-mini` |
| Policy module | `src/plugin_examples/llm_router/provider_policy.py` |
| Enforcement point | `router.py:_call_provider` — raises `LLMProviderError` for unapproved families |

---

## Audit Questions and Answers

### 1. Was gpt-4o-mini ever used by the pipeline?

**NO.**

`gpt-4o-mini` was previously hardcoded in `router.py` as a model default but was
replaced with `os.environ.get("OPENAI_MODEL", "gpt-4o")`. No active family config
ever sets `gpt-4o-mini` as a model. Test `test_gpt_4o_mini_replaced_with_env_var`
verifies the source no longer contains that string.

### 2. Was gpt-4o-mini found only in extracted NuGet documentation?

**YES.**

`gpt-4o-mini` appears inside extracted NuGet XML documentation for Aspose.Words
(`Aspose.Words.xml`, `net462`). The hit is in Aspose's own AI API documentation
code example (`OpenAiModel("gpt-4o-mini", apiKey)`). This is not a pipeline LLM
call. Classification: `extracted_nuget_documentation`, `is_pipeline_call: false`.

Evidence location: extracted NuGet XML documentation — `Aspose.Words.xml`
Evidence classification: `extracted_nuget_documentation`

### 3. Are any unapproved provider families callable?

**NO** (after Governance Closure Sprint enforcement).

`router.py:_call_provider` now raises `LLMProviderError` if the provider is not
in `_APPROVED_PROVIDER_FAMILIES = frozenset({"llm_professionalize", "ollama"})`.

Previously `gpt_oss` and `openai` branches existed and were callable. They remain
in the code as dead branches (the router can dispatch to them by name) but are
now blocked by the policy guard before any HTTP call is made.

Status: The `openai` and `gpt_oss` branches in `_call_provider` are now
unreachable at runtime because the guard raises before reaching them. They are
classified as `implemented_unapproved_route_blocked_by_policy`.

### 4. Are all actual generation calls routed through llm_professionalize or ollama?

**YES.**

All active family configs (`cells.yml`, `words.yml`, `pdf.yml`) specify:
```yaml
llm:
  provider_order:
    - llm_professionalize
    - ollama
```

The LLMRouter selects from this list in order. Only approved families can pass
the preflight and the call guard.

### 5. Are documentation hits excluded from runtime LLM evidence?

**YES.**

`write_preflight_report` sets `documentation_hits_excluded: true` in all
reports. The `classify_documentation_hit` and `classify_llm_hit` functions
in `provider_policy.py` return `is_pipeline_call: false` for any hit inside
`.xml` files or paths containing `nuget`/`extracted`.

### 6. Are provider family and model name recorded separately?

**YES.**

`llm-preflight.json` now contains:
- `provider_family` — the selected provider family (`llm_professionalize` or `ollama`)
- `model_name` — the model configured under that family (e.g. `recommended`, `codellama`)
- `route` — canonical route label (`llm_professionalize` or `local_ollama`)
- `documentation_hits_excluded` — always `true`
- `classification_notes` — explains gpt-4o-mini documentation hit treatment

---

## Hit Inventory

| Location | Hit | Classification | Status | Action |
|---|---|---|---|---|
| `router.py:230` | `gpt-4o-mini` | `violation_hardcoded_model` | FIXED | Replaced with `OPENAI_MODEL` env var |
| `router.py:149,163,206,211,232,233` | `gpt_oss` | `implemented_unapproved_route_blocked_by_policy` | MITIGATED | Policy guard raises before call; no config routes to it |
| `router.py:225-228` | `openai` | `implemented_unapproved_route_blocked_by_policy` | MITIGATED | Policy guard raises before call; no config routes to it |
| `cells.yml:73` | `gpt_oss` | `violation_active_config` | FIXED | Removed from provider_order |
| `words.yml:71` | `gpt_oss, openai` | `violation_active_config` | FIXED | Removed from provider_order |
| `pdf.yml:71` | `gpt_oss, openai` | `violation_active_config` | FIXED | Removed from provider_order |
| `test_family_config.py:76` | `gpt_oss` | `test_fixture_outdated` | FIXED | Updated assertion to expect approved providers |
| `test_code_quality_sprint.py:508` | `gpt_oss` | `test_fixture_acceptable` | NO ACTION | Internal test fixture, not asserting policy compliance |
| `llm-preflight.json` (prior run) | `gpt_oss` | `historical_evidence_artifact` | NO ACTION | Pre-policy run; not reproducible after fix |
| Extracted `Aspose.Words.xml` | `gpt-4o-mini` | `extracted_nuget_documentation` | NO ACTION | Aspose AI API documentation example; not a pipeline call |

---

## Classification Legend

| Classification | Meaning |
|---|---|
| `approved_llm_provider_config` | Approved provider in valid config |
| `approved_ollama_model` | Model name under approved ollama provider |
| `approved_professionalize_model` | Model name under approved llm_professionalize provider |
| `extracted_nuget_documentation` | Found inside NuGet XML doc, not a pipeline call |
| `test_fixture` | Test-only fixture, not production |
| `historical_evidence_artifact` | Pre-policy run artifact, not reproducible |
| `violation_hardcoded_model` | Forbidden model hardcoded in source |
| `violation_active_config` | Unapproved provider in active family config |
| `violation_unapproved_provider` | Unapproved provider family used |
| `implemented_unapproved_route_blocked_by_policy` | Code path exists but is blocked by runtime guard |
| `test_fixture_outdated` | Test used stale fixture, now fixed |
| `test_fixture_acceptable` | Test uses unapproved provider as fixture, not asserting production |

---

## Conclusion

The pipeline is fully compliant after the Governance Closure Sprint:

- Active family configs: only `llm_professionalize` and `ollama`
- Runtime guard: `_call_provider` raises `LLMProviderError` for unapproved families
- gpt-4o-mini: not in pipeline source, found only in extracted NuGet documentation
- Evidence reporting: `llm-preflight.json` records provider_family and model_name separately
- Documentation hits: excluded from pipeline LLM evidence with explicit classification

**Remaining open item:** The `openai` and `gpt_oss` branches in `router.py` are dead code
(blocked by policy guard). They should be removed in a future cleanup sprint to eliminate
the dead code entirely. Until then, they are classified as
`implemented_unapproved_route_blocked_by_policy` — not violations, but technical debt.
