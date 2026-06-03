# Shareability Remediation — Stage 2 Report

**Date:** 2026-06-03
**Branch:** main
**Baseline:** `a6f7fef` (Stage 0+1 complete)
**Final:** `edfc813` (Stage 2 complete)
**Verdict:** ALL TASKCARDS DONE — 3222/0/18 (passed/failed/skipped)

---

## What Changed

### TC-13: Scripts index fix (`065ac46`)
Fixed summary counts in `scripts/README.md`. All 6 "untracked" scripts were already indexed — only the SPRINT-HISTORICAL count (58→65) and total (99→106) were wrong.

### TC-09: Legacy LLM provider removal (`38417e2`)
Removed ~28 lines of dead code from `src/plugin_examples/llm_router/router.py`:
- `_resolve_api_key()`: Removed LLM_API_KEY/OPENAI_API_KEY fallbacks
- `_get_endpoint()`: Removed openai/gpt_oss defaults
- `_call_provider()`: Removed openai/gpt_oss elif branches
- `_check_provider()`: Simplified conditional to llm_professionalize only

Preserved: `_APPROVED_PROVIDER_FAMILIES`, ollama support, llm_professionalize support, dual-layer gate pattern. 82 LLM/provider tests pass unchanged.

### TC-08: Ruff configuration (`c1e80ad`)
Added `[tool.ruff]` to `pyproject.toml`:
- `target-version = "py312"`, `line-length = 120`
- Select: E (errors), F (pyflakes), W (warnings)
- 8 ignored rules to avoid churn on existing codebase
- `ruff check src/` exits 0 with zero code changes

### TC-12: Evidence validator decomposition (`b3d5bef`)
Replaced 7,860-line `evidence_validator.py` with a 17-module package:

| Module | Lines | Rules |
|--------|-------|-------|
| `models.py` | 51 | — |
| `helpers.py` | 71 | — |
| `validator.py` | 320 | — |
| `rules/s60.py` | 385 | 7 |
| `rules/s61_s66.py` | 632 | 13 |
| `rules/s67_s69.py` | 545 | 12 |
| `rules/s70_s71.py` | 615 | 12 |
| `rules/s72_s75.py` | 573 | 11 |
| `rules/s76_s77.py` | 608 | 13 |
| `rules/s78_s83.py` | 693 | 14 |
| `rules/s84_s86.py` | 657 | 14 |
| `rules/s87_s88.py` | 718 | 16 |
| `rules/s89.py` | 613 | 13 |
| `rules/s90_s95.py` | 664 | 13 |
| `rules/s96_s99.py` | 392 | 6 |
| `rules/s100_s104.py` | 300 | 3 |
| **Total** | **8015** | **147** |

Pattern: Mixin classes composed via multiple inheritance. Import path unchanged: `from plugin_examples.evidence_validator import EvidenceValidator`.

### TC-11: CLI decomposition (`88a9407`)
Replaced 2,270-line `__main__.py` with 35-line dispatcher + 22-module `commands/` package:
- 20 subcommands extracted into individual modules
- Shared metrics helpers in `_metrics.py` (91 lines)
- `register_all(subparsers)` in `__init__.py` (48 lines)
- Largest command module: `publish_pr.py` (459 lines)

### Verification fixes (`edfc813`)
Post-decomposition corrections:
- Fixed `Path(__file__).resolve().parents[2]` → `parents[3]` in 18 command modules
- Added missing `import logging` to 4 modules, `import os` to 4 modules
- Updated 6 test files to reference command modules instead of `__main__.py`
- Removed duplicate `validate_for_storage` block
- Fixed ruff violations (W293, F811, F821)

---

## Verification Results

| Gate | Result |
|------|--------|
| pytest | 3222 passed, 0 failed, 18 skipped |
| compileall | exit 0 |
| ruff check src/ | All checks passed |
| Rule count | 147 (verified via introspection) |
| Command count | 20 subcommands (verified via --help) |

---

## Remaining Gaps

None for Stage 2. All structural refactors complete. The codebase is now decomposed into navigable modules suitable for sharing with colleagues.
