# PDF PR Merge Preflight — Sprint 43

Generated: 2026-05-19

## Gate Check

| Gate | Status |
|------|--------|
| PLUGIN_EXAMPLES_MERGE_PR_APPROVAL | NOT SET |
| GH_TOKEN | SET |

## PR Status

| PR | State | Mergeable | Scenarios | Conflicts |
|----|-------|-----------|-----------|-----------|
| #5 | OPEN | CONFLICTING | doc-converter, html, xls-converter | README.md |
| #6 | OPEN | CONFLICTING | jpeg, png, tiff | README.md |
| #7 | OPEN | CONFLICTING | image-extractor, table-generator, toc-generator | README.md |
| #8 | OPEN | CONFLICTING | security, form-flattener | README.md, build configs |
| #9 | OPEN | CONFLICTING | form-editor, form-exporter | README.md, build configs |
| #10 | OPEN | CONFLICTING | signature | README.md, build configs |

## Critical Finding

**All 6 PRs are CONFLICTING.** This is a NEW finding not present in Sprint 42.

Root cause: Each PR modifies README.md. PRs #8-#10 also modify Directory.Build.props, Directory.Packages.props, and global.json.

## Action: BLOCKED_DUAL

1. Approval gate absent
2. All PRs have merge conflicts

## Resolution Plan

1. Close all 6 conflicting PRs
2. Create new sequential PRs rebased against current main
3. Set APPROVE_MERGE_PR gate
4. Merge sequentially
