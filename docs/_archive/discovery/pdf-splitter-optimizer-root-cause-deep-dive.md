# PDF Splitter and Optimizer Root-Cause Deep Dive

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/pdf-splitter-optimizer-root-cause-deep-dive.json`
**Verdict:** ROOT_CAUSE_IDENTIFIED_FIX_DEFINED

## Shared Root Cause

The LLM consistently generates `new PluginOptions()` instead of `new SplitOptions()` / `new OptimizeOptions()`. PluginOptions is abstract and cannot be instantiated (CS0144).

**Why:** The prompt packet builder does not inject the correct concrete options class name from the type-role-classification. The LLM sees method signatures but not the paired_options mapping.

## Splitter

- **Generated:** `new PluginOptions()` (3 independent runs)
- **Validator:** code_generator._validate_code() line 549 catches it — but as INFORMATIONAL, not blocking
- **Repair:** Repair prompt lacks SplitOptions name. LLM cannot discover it from compiler error alone.
- **First subsystem that failed:** packet_builder.py (no SplitOptions in prompt)
- **Should have caught earlier:** _validate_code() should trigger targeted repair, not just log

## Optimizer

- Same PluginOptions hallucination as Splitter
- **Additional:** LLM repair call timed out (120s, no retry)
- **First subsystem that failed:** packet_builder.py + router.py timeout handling

## Fix (both)

1. packet_builder: inject paired_options from type-role-classification into prompt
2. packet_builder: add SplitOptions/OptimizeOptions few-shot code examples
3. code_generator: change PluginOptions check from informational to blocking (trigger repair)
4. router.py: add retry_count=2 with exponential backoff for generate()
