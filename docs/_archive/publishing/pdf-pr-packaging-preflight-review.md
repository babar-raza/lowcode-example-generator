# PDF Partial Pilot PR Dry-Run Packaging — Phase 0 Preflight Review

**Date:** 2026-05-05
**Gate:** Phase 0 — Mandatory Referenced-Artifact Review
**Verdict:** GATE_0_FAIL_CONTRADICTIONS_FOUND → PROCEED WITH RECONCILED REDUCED SCOPE

---

## Summary

Phase 0 inspection of all referenced artifacts from the PDF Controlled Pilot LLM E2E Dry-Run Trial
revealed **4 critical contradictions** between the evidence summary files and actual run artifacts.

The evidence files (`pdf-llm-e2e-run-result.json`, `pdf-pilot-example-validation.json`,
`pdf-pilot-repair-loop-review.json`) **misrepresent the actual generated code** for both
pdf-merger and pdf-text-extractor.

---

## Artifact Classification

| Artifact | Classification | Finding |
|---|---|---|
| pdf-llm-e2e-run-result.json | CONTRADICTORY | Claims merger build=PASS; canonical run shows BUILD FAIL |
| pdf-pilot-example-validation.json | CONTRADICTORY | Claims 2 PASSED; only 1 passes in canonical run |
| pdf-pilot-repair-loop-review.json | CONTRADICTORY | Claims merger uses MergeOptions; code uses non-existent string array overload |
| open-taskcard-closure-matrix.json | VERIFIED | pdf-pr-packaging OPEN ✓ |
| pipeline/configs/families/pdf.yml | VERIFIED | status=active, correct allowed_types |
| family-generation-readiness-rank.json | CONTRADICTORY | controlled_pilot_pass_count=2 WRONG (should be 1) |
| pdf-merger/Program.cs (run 143724) | CONTRADICTORY | String array overload → BUILD FAIL; evidence claims MergeOptions |
| pdf-text-extractor/Program.cs (run 143724) | CONTRADICTORY | TextAbsorber (core API, not LowCode); evidence claims TextExtractorOptions |
| pdf-splitter/Program.cs (run 143724) | VERIFIED | PluginOptions → BUILD FAIL ✓ |
| pdf-optimizer/Program.cs (run 143724) | VERIFIED | PluginOptions → BUILD FAIL ✓ |
| validation-results.json (run 143724) | VERIFIED | Ground truth: 1 pass (text-extractor), 3 fail |
| pr-candidate-manifest.json (run 143724) | VERIFIED | 1 PR candidate (text-extractor only) |
| pdf-merger/Program.cs (run 142605) | NEEDS_FIX | Passes build+run but defines fake local Merger class |
| workspace/pr-dry-run/pdf-controlled-pilot/ | STALE | Wrong content (pdf-converter); must be rebuilt |
| publisher.py | VERIFIED | Safety gates intact |
| pr_builder.py | VERIFIED | Functional |
| readme_renderer.py | VERIFIED | Functional, PDF slug present |
| readme_auditor.py | VERIFIED | Functional |
| Master plan (linked-nibbling-hamster.md) | VERIFIED | Accurate |
| MEMORY.md | VERIFIED | Consistent (minor: pass_count should be 1) |

---

## Contradictions

### CONTRA-1 (HIGH) — Merger evidence fabricated

**Claim (evidence files):** pdf-merger build=PASS, run=PASS, uses `MergeOptions` with `AddInput`/`AddOutput`.

**Reality:** In canonical run 143724: `merger.Process(new[]{ path1, path2 }, outputPath, null)` — string
array overload that does NOT exist in the Aspose.PDF LowCode API. **BUILD FAIL** confirmed by
`validation-results.json`.

Run 142605 merger passes build+run but defines a fake local `Merger` class that shadows
`Aspose.Pdf.LowCode.Merger`. The LowCode API is imported but never used.

### CONTRA-2 (HIGH) — TextExtractor evidence fabricated

**Claim (evidence files):** pdf-text-extractor uses `TextExtractorOptions` with `StringResult`.

**Reality:** Canonical run 143724 `Program.cs` uses `TextAbsorber` from `Aspose.Pdf.Text`
(core Aspose.PDF). No `Aspose.Pdf.LowCode` namespace imported. **Not a LowCode example.**
Build and run PASS, but demonstrates the wrong API.

### CONTRA-3 (MEDIUM) — Generation readiness rank overcounts passes

**Claim:** `controlled_pilot_pass_count=2`

**Reality:** Canonical run has 1 passing example only.

### CONTRA-4 (MEDIUM) — Partial package has wrong content

**Claim:** `workspace/pr-dry-run/pdf-controlled-pilot/` contains PDF pilot examples.

**Reality:** Contains `pdf-converter` (wrong example type, not a pilot type). README also wrong.

---

## Multi-Run Analysis

| Run | pdf-merger outcome | pdf-text-extractor outcome |
|---|---|---|
| 20260505-140928 | BUILD FAIL | Not generated |
| 20260505-142605 | BUILD PASS (fake local class — NOT LowCode) | Not generated |
| 20260505-143724 (canonical) | BUILD FAIL (non-existent API) | BUILD+RUN PASS (TextAbsorber, not LowCode) |
| 20260505-144850 | Not generated | BUILD FAIL (non-existent string overload) |

**Conclusion:** No run produced a correct LowCode Merger example. No run produced a correct
LowCode TextExtractor example. The best available passing code for each type uses the wrong API.

---

## Reconciliation Decisions

| Example | Decision | Reason |
|---|---|---|
| pdf-merger | EXCLUDED | No run has correct `Aspose.Pdf.LowCode.Merger().Process(MergeOptions)` code that compiles |
| pdf-text-extractor | INCLUDED WITH LIMITATION | Run 143724: build+run PASS; uses TextAbsorber (documented as NEEDS_LLM_REMEDIATION) |
| pdf-splitter | EXCLUDED | PluginOptions hallucination → BUILD FAIL |
| pdf-optimizer | EXCLUDED | PluginOptions hallucination + timeout → BUILD FAIL |

---

## Gate 0 Criteria

| Criterion | Status |
|---|---|
| Merger and TextExtractor verified as build/run PASS | PARTIAL — text-extractor PASS; merger NO valid LowCode code |
| Splitter and Optimizer verified as blocked | PASS ✓ |
| Taskcard JSON and markdown agree | PASS ✓ |
| PDF live publish remains blocked | PASS ✓ |
| No contradictory state remains | FAIL — 4 contradictions documented |

**Gate 0 Verdict:** FAIL → Reconciled to reduced scope (text-extractor only, limitations documented)

---

## Next Required Action

Fix LLM generation for merger and text-extractor:
1. `pdf-merger`: Add few-shot example showing `new Aspose.Pdf.LowCode.Merger().Process(new MergeOptions())` with `AddInput`/`AddOutput`. Prevent fake local class definition.
2. `pdf-text-extractor`: Add few-shot example showing `new TextExtractor().Process(opts)` with `TextExtractorOptions`. Prevent TextAbsorber fallback.
3. These are adjacent to `followup-pdf-splitter-options-class` — the LLM consistently fails to use the correct concrete API for all PDF types.
