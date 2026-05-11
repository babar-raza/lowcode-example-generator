# PDF Excluded Examples Root Cause Review

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/pdf-excluded-examples-root-cause-review.json`
**Verdict:** GATE_1_PASS

## pdf-splitter

- **Planned:** Yes
- **Selected by allowlist:** No — excluded by `allowed_types=[Merger, TextExtractor]`
- **Generated:** No — blocked before generation at scenario_planning
- **Root cause:** LLM hallucinated abstract `PluginOptions` instead of concrete `SplitOptions`. `new PluginOptions()` does not compile (abstract class).
- **Limitation category:** LLM behavior — insufficient prompt constraints
- **Backlog entry:** `pdf-backlog-splitter-001`
- **Taskcard:** `followup-pdf-splitter-options-class` (OPEN, high priority)
- **Fix:** SplitOptions few-shot, prompt constraint, code validator rule, repair feedback

## pdf-optimizer

- **Planned:** Yes
- **Selected by allowlist:** No — excluded by `allowed_types=[Merger, TextExtractor]`
- **Generated:** No — blocked before generation at scenario_planning
- **Root cause:** LLM used abstract `PluginOptions` instead of `OptimizeOptions` + LLM timed out during repair attempt
- **Limitation category:** LLM behavior + infrastructure timeout
- **Backlog entry:** `pdf-backlog-optimizer-001`
- **Taskcard:** `followup-pdf-optimizer-options-class` (OPEN, high priority)
- **Fix:** OptimizeOptions few-shot, prompt constraint, code validator, timeout/retry policy
