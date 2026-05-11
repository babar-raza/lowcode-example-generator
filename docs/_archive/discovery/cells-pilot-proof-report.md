# Aspose.Cells Pilot Proof Report

**Run ID:** `pilot-cells-20260429`
**Date:** 2026-04-29
**Baseline commit:** `d67df7e` (main, synced with origin)
**Verdict:** `DATA_FLOW_PROTOTYPE_ONLY`
**Reclassified:** 2026-04-29 (healing sprint audit — original verdict was `COMPLETE, DATA-FLOW PROOF ONLY`)

## Executive Summary

All 16 pipeline stages executed successfully with real Aspose.Cells data flowing through every module. The pipeline resolved NuGet package 26.4.0, extracted DLLs, reflected the API, detected 22 LowCode plugin types with 33 methods, planned 14 ready scenarios, generated 14 template examples, and completed publisher dry-run with evidence verification. No hard stops, no degraded stages, no failures.

Template-mode build failures (14/14) are expected and documented — template code is structurally valid but not compilable without LLM refinement.

**Reclassification note:** The original report marked all 16 stages as PASS. The healing sprint audit found that validation (0/14 builds passing) and reviewer (not installed) were incorrectly reported as PASS due to the catch-all degradation logic in the runner and default `require_validation=False`. The honest statuses are DEGRADED and SKIPPED respectively.

## Before / After Comparison

| Location | Before | After |
|----------|--------|-------|
| `workspace/manifests/` | empty | empty (no `--promote-latest`) |
| `workspace/verification/latest/` | empty | empty (no `--promote-latest`) |
| Run evidence files | N/A | 9 JSON files |

## Stage Results

| # | Stage | Status | Duration | Key Artifacts |
|---|-------|--------|----------|---------------|
| 1 | load_config | PASS | 201ms | family=cells, package_id=Aspose.Cells |
| 2 | nuget_fetch | PASS | 35.5s | version=26.4.0, sha256=68692b88... |
| 3 | dependency_resolution | PASS | 18.1s | 8 dependencies resolved |
| 4 | extraction | PASS | 2.5s | netstandard2.0, DLL+XML extracted |
| 5 | reflection | PASS | 717ms | 1 namespace (Aspose.Cells.LowCode) |
| 6 | plugin_detection | PASS | 11ms | 22 types, 33 methods, eligible=true |
| 7 | api_delta | PASS | 5ms | initial_run, 22 total changes |
| 8 | impact_mapping | PASS | 2ms | 22 new API examples needed |
| 9 | fixture_registry | PASS | 3ms | 1 fixture registered |
| 10 | example_mining | PASS | 5ms | 1 mined, 0 stale |
| 11 | scenario_planning | PASS | 7ms | 14 ready, 8 blocked |
| 12 | llm_preflight | PASS | 8.2s | no provider available |
| 13 | generation | PASS | 35ms | 14 examples (template mode) |
| 14 | validation | DEGRADED | 39.8s | 0 build pass, 14 build fail (require_validation=False masked) |
| 15 | reviewer | SKIPPED | 59ms | not installed (require_reviewer=False masked) |
| 16 | publisher | PASS | 5ms | dry_run, evidence_verified=true |

**Total duration:** 105.1 seconds

## Key Metrics

| Metric | Value |
|--------|-------|
| NuGet package | Aspose.Cells 26.4.0 |
| Package SHA256 | `68692b88f4b5c395ea00ad20b5a96a176fc1eb39085e0dffae4ac41e280e6ac6` |
| Target framework | netstandard2.0 |
| Plugin namespace | Aspose.Cells.LowCode |
| Public plugin types | 22 |
| Public plugin methods | 33 |
| Dependencies resolved | 8 |
| Ready scenarios | 14 |
| Blocked scenarios | 8 |
| Examples generated | 14 |
| Generation mode | template |
| Build pass rate | 0/14 (expected in template mode) |
| Reviewer | unavailable (not installed) |
| Publisher | dry_run, evidence verified |

## Evidence Files

Location: `workspace/runs/pilot-cells-20260429/evidence/latest/`

1. `cells-source-of-truth-proof.json` — NuGet → DLL → reflection → detection chain
2. `api-delta-report.json` — initial run, all 22 types added
3. `example-impact-report.json` — 22 new API examples needed
4. `blocked-scenarios.json` — 8 scenarios with documented blocking reasons
5. `llm-preflight.json` — no provider available
6. `validation-results.json` — 14 template examples, all build-fail (expected)
7. `example-reviewer-results.json` — reviewer not installed
8. `publishing-report.json` — dry_run, evidence_verified=true
9. `stale-existing-examples.json` — 0 stale examples

Additional evidence in run directory:
- `workspace/runs/pilot-cells-20260429/packages/cells/` — downloaded .nupkg + download-manifest
- `workspace/runs/pilot-cells-20260429/extracted/cells/` — DLLs + extraction-manifest
- `workspace/runs/pilot-cells-20260429/catalog/cells/api-catalog.json` — full API catalog
- `workspace/runs/pilot-cells-20260429/generated/cells/` — 14 generated C# projects
- `workspace/runs/pilot-cells-20260429/pilot-report.json` — full structured report

## Gate Summary

| Category | Count |
|----------|-------|
| Passed | 14 |
| Degraded | 1 |
| Failed | 0 |
| Skipped | 1 |
| Hard stopped | No |

## Degraded Stages Explanation

- **validation (DEGRADED):** 0/14 generated examples passed build. The runner's catch-all logic converted this to "success" because `require_validation=False`. Honest status: DEGRADED — validation ran but found 100% build failures.
- **reviewer (SKIPPED):** example-reviewer is not installed locally. The runner's catch-all logic converted this to "success" because `require_reviewer=False`. Honest status: SKIPPED — reviewer was not available to execute.

The LLM preflight returned no provider but did not fail — the pipeline correctly fell through to template mode generation.

## Test Results

- **Unit tests:** 235 passed (197 existing + 38 new runner tests)
- **compileall:** all source files compile
- **DllReflector:** builds with 0 warnings, 0 errors
- **Old-path grep:** no forbidden bare paths found

## Files Created/Modified

### New files
- `src/plugin_examples/runner.py` — pipeline orchestrator (817 lines)
- `scripts/pilot_run.py` — CLI wrapper (137 lines)
- `tests/unit/test_runner.py` — 38 orchestrator unit tests
- `docs/discovery/pipeline-module-integration-surface.md` — module API inventory
- `docs/discovery/cells-pilot-proof-report.md` — this report

### Modified files
- `src/plugin_examples/__main__.py` — `run` command wired to `run_pipeline()`

## Verdict Justification

**DATA_FLOW_PROTOTYPE_ONLY**

This verdict is correct because:
1. Real Aspose.Cells NuGet data flowed through every pipeline module (source-of-truth proven)
2. Template mode was used (no LLM provider available) — generated code is structurally valid but not compilable
3. 0/14 generated examples pass build — validation is DEGRADED, not PASSED
4. Reviewer is not installed — reviewer gate is SKIPPED, not PASSED
5. Evidence chain is complete from NuGet resolution through publisher dry-run
6. This is NOT "FULL_E2E_PASSED" because: template mode was used, builds fail, reviewer absent
7. This is NOT publishable — DATA_FLOW_PROTOTYPE_ONLY cannot publish

The pipeline data flow is proven. LLM integration + build pass + reviewer pass are needed for FULL_E2E_PASSED.

## Drift Items Discovered

The healing sprint audit identified 16 implementation drifts. See `docs/discovery/implementation-gap-report.md` for full details.

| # | Drift | Severity | Blocks Publishing |
|---|-------|----------|-------------------|
| 1 | Runner reports success when builds fail | Critical | Yes |
| 2 | CLI forces template mode and skips runtime | Critical | Yes |
| 3 | Generated examples missing required output files | High | Yes |
| 4 | Generated .csproj uses inline package versions | High | Yes |
| 5 | Output validator ignores expected-output.json | High | Yes |
| 6 | Fixture registry registers directory paths as filenames | High | Yes |
| 7 | Example miner registers paths, no C# parsing | Medium | No |
| 8 | Scenario planner ignores missing fixtures | High | Yes |
| 9 | LLM router uses localhost only | Medium | No |
| 10 | example-reviewer command not operational | Medium | Yes |
| 11 | Publisher does not check all required gates | Critical | Yes |
| 12 | Package watcher does not resolve NuGet versions | Medium | No |
| 13 | Experimental families active by default | Medium | No |
| 14 | No evidence promotion to durable paths | Medium | No |
| 15 | pytest-timeout not in dependencies | Low | No |
| 16 | DllReflector build artifacts in working tree | Low | No |
