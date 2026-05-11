# Cross-Family Planned Completion Gap Analysis

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/cross-family-planned-completion-gap-analysis.json`
**Verdict:** GATE_2_PASS

## Cells (100% complete)

- 9/9 candidate scenarios published and merged
- 13 excluded types are all non-runnable (abstract bases, options, callbacks, results)
- No system gaps. No further action needed for standalone APIs.

## Words (44% complete — 4/9 candidates)

| Excluded Type | Root Cause | Taskcard |
|---------------|-----------|----------|
| Comparer | MISSING_FIXTURE_STRATEGY (paired input) | followup-words-pair-fixture-strategy |
| Merger | MISSING_FIXTURE_STRATEGY (array input) | followup-words-pair-fixture-strategy |
| MailMerger | MISSING_FIXTURE_STRATEGY (merge fields) | followup-words-mail-merger-fixture-documentation |
| ReportBuilder | MISSING_FIXTURE_STRATEGY (LINQ tags) | (new taskcard needed) |
| Processor | MISSING_OPTIONS_STRATEGY (builder pattern) | (new taskcard needed) |

Additional: WORDS-005 Splitter.Split blocked by missing SplitCriteria enum values.

## PDF (8% complete — 2/25 candidates)

| Scenario | Root Cause | Taskcard |
|----------|-----------|----------|
| Splitter | LLM_WRONG_API_USAGE (PluginOptions hallucination) | followup-pdf-splitter-options-class |
| Optimizer | LLM_WRONG_API_USAGE + LLM_TIMEOUT | followup-pdf-optimizer-options-class |
| 21 others | PILOT_SCOPE_LIMIT (not yet attempted) | followup-pdf-expanded-coverage |

## System Gaps Summary

1. No type-specific few-shot injection from source-of-truth
2. No paired/array fixture strategy
3. No template-with-merge-fields fixture
4. No enum value enumeration in DllReflector
5. No LLM timeout retry
6. No structured reviewer feedback
7. No cross-run learning from backlog
8. Code validator PluginOptions check is informational, not blocking
9. Repair prompt lacks API catalog context
10. No format-specific output validators
