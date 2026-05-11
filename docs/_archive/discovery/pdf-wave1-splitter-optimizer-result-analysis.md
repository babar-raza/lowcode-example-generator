# PDF Wave 1 Splitter and Optimizer Result Analysis

**Sprint:** Wave 1 PDF Tier 5 LLM Pilot Completion
**Date:** 2026-05-07
**Run ID:** pilot-pdf-20260507-110824

---

## Summary

| Scenario | Pipeline Verdict | Agent Verdict | Correct API? | Publishable? |
|----------|-----------------|---------------|-------------|-------------|
| Merger | PR_DRY_RUN_READY | PASS | YES — MergeOptions + Merger().Process() | YES |
| **Splitter** | PR_DRY_RUN_READY | **PASS** | **YES — SplitOptions + Splitter().Process()** | **YES (new!)** |
| Optimizer | PR_DRY_RUN_READY | **SEMANTIC_FAIL** | **NO — File.Copy() instead of OptimizeOptions** | **NO** |
| TextExtractor | GENERATION_FAILED | GENERATION_FAIL | N/A | NO (regression) |

**Overall verdict: `PDF_WAVE1_PARTIAL_WITH_PRECISE_BLOCKERS`**

---

## Splitter Analysis — PASS ✓

**Status:** First successful Splitter example ever generated.

**Code verified:**
```csharp
var options = new SplitOptions();
options.AddInput(new FileDataSource(inputPath));
options.AddOutput(new FileDataSource(outputPath));
var result = new Splitter().Process(options);
```

**Evidence:**
- Static validator detected `new PluginOptions()` → blocked → repair produced SplitOptions → CORRECT
- `_pdf_type_hints` constraint injection worked: `"REQUIRED: options class is 'SplitOptions'"` was in prompt
- Build: PASS (0 build repairs)
- Runtime: PASS
- Reviewer: PASS
- Taskcard `followup-pdf-splitter-options-class`: **CLOSE** — acceptance criteria met

---

## Optimizer Analysis — SEMANTIC FAIL ✗

**Pipeline says:** EXAMPLE_READY_FOR_PR_DRY_RUN
**Agent override:** SEMANTIC_FAIL — do NOT publish

**Problem:** After 2 build repair cycles, the LLM produced:
```csharp
// Simulate optimization by copying the file (replace with real optimizer when available)
File.Copy(inputPath, outputPath, overwrite: true);
```

This does **not** demonstrate `Aspose.PDF.LowCode.Optimizer`. No `OptimizeOptions`, no `new Optimizer().Process(options)` call.

**Required code:**
```csharp
var options = new OptimizeOptions();
options.AddInput(new FileDataSource(inputPath));
options.AddOutput(new FileDataSource(outputPath));
var result = new Optimizer().Process(options);
```

**Root cause:** The build repair path (`runner.py` ~line 695) does NOT re-inject PDF-specific constraints (options class name, code pattern). The generation repair path does re-inject them (fixed in code_generator.py). But after 2 failed build repairs, the LLM reverted to a semantically wrong but compilable File.Copy approach.

**New gap identified:** Build repair needs the same PDF constraint re-injection that generation repair has. New taskcard required: `followup-pdf-optimizer-build-repair-constraint-injection`.

**Taskcard `followup-pdf-optimizer-options-class`: REMAIN OPEN** — semantic failure confirmed.

---

## TextExtractor Analysis — GENERATION FAIL (Regression)

**Prior run (pilot-pdf-20260505-214804):** PASS
**This run:** FAILED at static validation

**Error:** `"PDF TextExtractor: must instantiate TextExtractorOptions and call Process(options)"`

The LLM generated a different code path in this run that did not satisfy the TextExtractorOptions static check, even after repair.

**Root cause:** Non-deterministic LLM behavior. The prior run succeeded; this run failed. The repair did not recover within max attempts.

**Note:** The TextExtractor code already exists on `main` from the merged PR #1. This regression does not invalidate the previously published code.

**New taskcard required:** `followup-pdf-text-extractor-static-validation-regression` — investigate why the validator fails on some LLM outputs; possibly tighten repair prompt for TextExtractor.

---

## Blockers for Optimizer

1. **Build repair constraint gap**: Build repair does not re-inject `REQUIRED: options class is 'OptimizeOptions'` — LLM can produce any compilable code, including wrong simulations
2. **Recommended fix**: Add PDF constraint re-injection to build repair path in `runner.py` (similar to generation repair in `code_generator.py`)

## Blockers for TextExtractor

1. **Regression in static validation**: Non-deterministic failure — LLM sometimes generates code that doesn't pass TextExtractorOptions check
2. **Recommended fix**: Strengthen TextExtractor repair prompt with explicit TextExtractorOptions example; or reduce max repair to fail faster and trigger backlog entry
