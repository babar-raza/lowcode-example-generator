# Lane 10: Work-Ahead Preparation

**Sprint**: lowcode-durable-full-closure-20260529
**Date**: 2026-05-29
**Status**: COMPLETE

## Key Findings for Next Sprint

### Template_first Expansion
Two additional types were fixed in this sprint (pdf-table-generator, slides-convert) bringing total
template_first types to 9. If new types show similar ambiguity or API chain issues, the same pattern
applies: add `template_first: true` + deterministic template in `_generate_deterministic_template_for_scenario`.

### Verification/Latest Staleness
The `workspace/verification/latest/families/diagram/` directory has a stale state from a prior run
where generation was BLOCKED. This causes the publisher to show "blocked" for diagram even when
the current run shows 2 valid PR candidates. This should be addressed by a verification promotion
step after each successful pilot run.

### Publication Gate
`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` is still NOT SET. When this gate is set to `APPROVE_LIVE_PR`,
the pipeline will create actual GitHub PRs for all 41 PR candidates.

### TableGenerator FORBIDDEN constraint update
The pdf.yml now correctly forbids the `TableOptions.Create()` fluent chain (which ends at
TableCellBuilder causing CS1061). The mandatory_reference_example has been updated to show
the correct `new TableOptions()` pattern.

## Outstanding Taskcard
- `followup-words-processor-api-investigation`: Processor type is disabled in words.yml due to
  CS0120 (no public constructor). API investigation needed before re-enabling.
