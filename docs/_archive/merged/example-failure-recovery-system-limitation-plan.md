# Example Failure Recovery — System Limitation and Improvement Plan

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/example-failure-recovery-system-limitation-plan.json`

## What the System Handles Today

- NuGet reflection discovery, scenario planning, LLM code generation
- Build-repair loop (compiler error → LLM → rebuild)
- Runtime-repair loop (runtime error → classification → LLM → rerun)
- Code quality validation (forbidden patterns, null-options, PluginOptions)
- PR packaging, live publish, merge governance, post-merge validation
- Family-scoped evidence promotion
- Lifecycle tracking for all planned examples (including excluded)
- Durable backlog with root cause and taskcard cross-links

## What the System Cannot Handle

| Gap | Impact | Fix Priority |
|---|---|---|
| Reviewer-driven repair loop | Reviewer failures require manual intervention | P3 |
| Cross-run backlog learning | Same failures repeat across runs | Future |
| PDF Splitter/Optimizer concrete options few-shot | 2 examples excluded | P1/P2 |
| LLM timeout recovery | Optimizer failed during repair | P2 |
| DOCX semantic validation | Words output not text-validated | P7 |
| Paired-input fixtures | Comparer/Merger need 2+ files | P5 |
| SplitCriteria enum | Not in DllReflector output | P4 |

## Excluded Examples Root Cause

| Example | Root Cause | Category |
|---|---|---|
| pdf-splitter | PluginOptions hallucination | LLM behavior |
| pdf-optimizer | PluginOptions + timeout | LLM + infrastructure |

Both are NOT API complexity issues — the APIs are straightforward. The LLM simply lacks concrete options class few-shot guidance.

## Recommended Next Sprint

**PDF Splitter+Optimizer Few-Shot and Options-Class Fix Sprint**
1. Add SplitOptions/OptimizeOptions few-shot to prompt packet
2. Add code validator rule: reject `new PluginOptions()`
3. Add LLM timeout retry policy
4. Regenerate Splitter and Optimizer
5. If 4/4 pass: create PDF PR #2
