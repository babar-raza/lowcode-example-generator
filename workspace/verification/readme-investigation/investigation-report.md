# README Investigation Report

**Date:** 2026-05-04
**Scope:** Full repository investigation for README authoring
**Outcome:** README.md replaced (was 2-line placeholder)

---

## Investigation Method

Files were read directly and cross-referenced. No claims were accepted from memory alone.
Three parallel Explore agents were run, then key files were read directly to verify:
- pyproject.toml (deps, Python version, CLI entry point)
- AGENTS.md (governance rules, inconsistencies)
- pipeline/configs/families/cells.yml, words.yml, pdf.yml (family config details)
- src/plugin_examples/llm_router/provider_policy.py (env var names)
- docs/ci/environment-variables.md (authoritative env var reference)
- .github/workflows/build-and-test.yml (CI details)
- workspace/verification/latest/release-status.json (evidence of accomplishments)

---

## Key Findings

### 1. Project purpose (verified)
- Source: AGENTS.md line 9
- "It generates, validates, and publishes SDK-style C# examples for Aspose .NET plugin APIs"
- Pipeline repo only; published examples live in separate repos

### 2. Cells accomplishments (verified by evidence)
- Source: workspace/verification/latest/release-status.json
- 9/9 POST_MERGE_VERIFIED, version 26.4.0, PR #1 merged

### 3. Words accomplishments (verified by evidence)
- Source: workspace/verification/latest/release-status.json
- 4/4 POST_MERGE_VERIFIED, version 26.4.0, PR #1 merged

### 4. PDF status (verified by config)
- Source: pipeline/configs/families/pdf.yml line 4
- `status: discovery_only` — confirmed blocked

### 5. Words allowed_types (verified by config)
- Source: pipeline/configs/families/words.yml lines 60-64
- Converter, Watermarker, Splitter, Replacer — confirmed 4 types only

### 6. LLM env var names (verified — AGENTS.md is stale)
- Source: docs/ci/environment-variables.md, src/plugin_examples/llm_router/provider_policy.py
- Actual env vars: GPT_OSS_ENDPOINT, GPT_OSS_API_KEY, GPT_OSS_MODEL
- AGENTS.md incorrectly references LLM_PROFESSIONALIZE_API_KEY — STALE

### 7. CI platform (verified)
- Source: .github/workflows/build-and-test.yml
- Runs on ubuntu-latest, Python 3.12 and 3.13
- Also builds DllReflector on .NET 8.0

### 8. Approved LLM providers (verified)
- Source: src/plugin_examples/llm_router/provider_policy.py lines 12-13
- APPROVED_PROVIDERS = {"llm_professionalize", "ollama"}
- UNAPPROVED_PROVIDERS = {"gpt_oss", "openai", "azure_openai"}

### 9. CLI entry point (verified)
- Source: pyproject.toml line 23
- `plugin-examples = "plugin_examples.__main__:main"`
- Python >= 3.12, 4 runtime dependencies

---

## Inconsistencies Found

1. **AGENTS.md vs actual env vars:** AGENTS.md references `LLM_PROFESSIONALIZE_API_KEY` but the
   actual env var is `GPT_OSS_API_KEY`. Documented in README Known Gaps section.

2. **AGENTS.md credentials table:** Lists `LLM_PROFESSIONALIZE_API_KEY` but docs/ci/environment-variables.md
   is authoritative and uses GPT_OSS_* prefix.

---

## Verification Results

### Unit tests
Run: `PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/unit -q --timeout=60`
Result: **759 passed in 21.42s** — confirmed

### Path verification
All 29 README-referenced paths confirmed to exist on disk via `os.path.exists`.

---

## Areas Not Fully Investigated

- Full source of every one of the 759 unit tests (names were read; bodies not fully verified)
- The monthly-package-refresh.yml workflow (existence confirmed; full content not read)
- The full runner.py source (structure verified via agent; not read line-by-line)
- The full __main__.py source (CLI commands verified via agent; not read line-by-line)
