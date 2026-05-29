# Lane 11: AI/LLM Accounting

**Sprint**: lowcode-durable-full-closure-20260529
**Date**: 2026-05-29
**Status**: COMPLETE

## LLM Usage in This Sprint

All 42 examples were generated using `--template-mode` with `template_first: true` deterministic templates.
**No LLM calls were made for code generation** in any of the 6 family runs.

### LLM Router
The pipeline's `llm_preflight` stage selects `llm_professionalize` as the LLM provider for all families.
However, since `template_first: true` is set for all generated types, the LLM router is bypassed
for code generation.

### Template-first Coverage
| Family | Total Types | template_first Types | LLM Used for Gen |
|--------|-------------|---------------------|------------------|
| cells | 9 examples | SpreadsheetMerger | No |
| diagram | 2 examples | DiagramConverter, PdfConverter | No |
| words | 8 examples | Merger, Watermarker | No (others: Converter, Splitter, Replacer, Comparer, MailMerger, ReportBuilder have template_first from prior sprints) |
| pdf | 19 examples | TableGenerator + 18 others | No |
| email | 1 example | EmailConverter | No |
| slides | 3 examples | Convert, Compress, Merger | No |

### Healing Intelligence
The pipeline's healing intelligence system loaded for all families with:
- failure_patterns_count: 9
- repair_patterns_count: 9
- validator_rules_count: 12

Healing intelligence informed template selection but no repairs were needed (template_first templates generate correct code directly).

## Summary

LLM usage: 0 code generation calls.
All 42 examples generated deterministically via template_first templates.
