# Cells Tier-5 Monthly Rerun Proof

**Proof Date:** 2026-05-04
**Run ID:** `pilot-cells-20260430-175422`
**Run Date:** 2026-04-30
**Verdict:** `PR_DRY_RUN_READY`

---

## Package

| Field | Value |
|---|---|
| Package | Aspose.Cells 26.4.0 |
| nupkg SHA256 | `68692b88f4b5c395ea00ad20b5a96a176fc1eb39085e0dffae4ac41e280e6ac6` |
| Framework | netstandard2.0 |
| Dependencies | 8 |
| Plugin namespace | Aspose.Cells.LowCode |
| Plugin types | 22 |
| Plugin methods | 33 |
| Source-of-truth | eligible |

---

## 16-Stage Result

All 16 stages **PASSED** (degraded=0, failed=0, skipped=0, hard_stopped=false).

| # | Stage | Status |
|---|---|---|
| 1 | load_config | success |
| 2 | nuget_fetch | success |
| 3 | dependency_resolution | success |
| 4 | extraction | success |
| 5 | reflection | success |
| 6 | plugin_detection | success |
| 8 | api_delta | success |
| 9 | impact_mapping | success |
| 10 | fixture_registry | success |
| 11 | example_mining | success |
| 12 | scenario_planning | success |
| 13 | llm_preflight | success |
| 14 | generation | success |
| 15 | validation | success |
| 16 | reviewer | success |
| 17 | publisher | success |

---

## LLM Provider

| Field | Value |
|---|---|
| Provider selected | `llm_professionalize` |
| Endpoint | `https://llm.professionalize.com/v1/` |
| Model | `recommended` |
| Preflight | PASSED |
| Latency | 1368 ms |
| Forbidden model used | NO — `gpt-4o-mini` NOT used |

Provider policy: `llm_professionalize` is APPROVED. `gpt_oss` and `openai` are UNAPPROVED and not in config.

---

## Generated Examples (9/9)

| Scenario | Build | Run |
|---|---|---|
| cells-html-converter | PASS | PASS |
| cells-image-converter | PASS | PASS |
| cells-json-converter | PASS | PASS |
| cells-pdf-converter | PASS | PASS |
| cells-spreadsheet-converter | PASS | PASS |
| cells-spreadsheet-locker | PASS | PASS |
| cells-spreadsheet-merger | PASS | PASS |
| cells-spreadsheet-splitter | PASS | PASS |
| cells-text-converter | PASS | PASS |

**9/9 build PASS, 9/9 run PASS.**

---

## Repair Summary

| Type | Count |
|---|---|
| Build repairs | 1 |
| Runtime repairs | 0 |

**Build repair:** `cells-spreadsheet-merger` — multi-overload violation caught by options-aware validator. Repaired on attempt 1. Fixed code: `SpreadsheetMerger.Process(new[] { inputPath }, outputPath)`.

---

## Fixture Strategy

| Field | Value |
|---|---|
| Strategy | `synthetic_fixture_factory` |
| GitHub API status | 403 (rate limited without GITHUB_TOKEN) |
| Impact | Stage succeeded; synthetic fallback used |
| Fixtures generated | 9 |

All 9 fixtures created programmatically:
- 8 `.xlsx` files (3131 bytes each) for spreadsheet-based scenarios
- 1 `.csv` file (73 bytes) for `cells-text-converter`

No GitHub fixture API dependency in this run.

---

## Reviewer

- Available: YES
- Passed: YES
- Preflight ready: YES

---

## PR Dry-Run Readiness

- Verdict: `PR_DRY_RUN_READY`
- dry_run: true
- publishable: false (by design — dry_run mode)
- evidence_verified: true
- pr_candidate_count: 9

---

## Live PR Status

The generated examples from this run were subsequently packaged and published:

| Field | Value |
|---|---|
| PR URL | https://github.com/aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples/pull/1 |
| Branch | `plugin-examples/cells/20260502-153727` |
| Merge SHA | `f6e5515c070184e4b08a2cff647220bea1113b08` |
| Merged At | 2026-05-03T09:03:13Z |
| Post-merge | POST_MERGE_VERIFIED (9/9 ALL_PASS from clean clone) |

**No new publishing recommended.** PR #1 is already merged. Next publishing requires new human sign-off for new examples.

---

## Evidence Note: Cross-Family Promotion Contamination

`workspace/verification/latest/` was partially overwritten by a Words run (`pilot-words-20260501-150103`) on 2026-05-01. Four files were stale at time of review:

- `validation-results.json` — was showing 4 Words results
- `pr-candidate-manifest.json` — was showing 2 Words candidates
- `example-gate-results.json` — was showing Words gate results
- `example-reviewer-results.json` — was showing Words reviewer workspace

All four reconciled from canonical source: `workspace/runs/pilot-cells-20260430-175422/evidence/latest/`.

New architectural taskcard: `followup-family-scoped-evidence-promotion` — `--promote-latest` must be family-scoped to prevent cross-family overwrite.

**Canonical evidence path:** `workspace/runs/pilot-cells-20260430-175422/evidence/latest/`

---

## Test Suite (at proof verification date)

- Total: 759
- Passed: 759
- Failed: 0
- `compileall src -q`: PASS
- `dotnet build DllReflector -c Release`: PASS (0 errors)
