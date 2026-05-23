# Sprint 75 — PDF Publication Truth Summary

**Date:** 2026-05-23
**Reconciling:** Weekly Review Item 1 — "14 PDF examples blocked by approval gate"

## Verdict: VERIFIED_HISTORICAL_BUT_SUPERSEDED

The weekly review claim was accurate at the time it was made (Sprint 21, 2026-05-16) but has
been superseded by subsequent publication work.

## Current PDF Publication State

| Category | Count | Notes |
|----------|-------|-------|
| Total PDF scenarios (exc. FormImporter) | 19 | FormImporter blocked upstream — not counted |
| Remote example present | 19/19 | All PRESENT_VERIFIED |
| Remote Program.cs exists | 19/19 | All PRESENT_VERIFIED |
| Remote README exists | 19/19 | All have README files |
| Remote README has I/O section | 0/19 | NONE — I/O update is current open work |
| Local handoff README has I/O | 19/19 | All ready for publication |

## PR History Reconciliation

At Sprint 21 (2026-05-16), the state was:
- 5 PDF examples published via PRs #1, #2, #4 (merged before Sprint 21)
- 14 examples staged in "draft" PRs #3/#5/#6/#7/#8/#9 — blocked by approval gate

Since Sprint 21, the following merged:
- PR#11 (2026-05-19): pdf-doc-converter, pdf-html, pdf-xls-converter (3 examples)
- PR#17 (2026-05-19): pdf-jpeg, pdf-png, pdf-tiff (3 examples)
- PR#18 (2026-05-19): pdf-image-extractor, pdf-table-generator, pdf-toc-generator (3 examples)
- PR#19 (2026-05-19): pdf-form-flattener, pdf-security (2 examples)
- PR#20 (2026-05-19): pdf-form-editor, pdf-form-exporter (2 examples)
- PR#21 (2026-05-19): pdf-signature (1 example)

Total via PRs #11, #17-#21: 14 examples → All 14 previously-blocked examples are now merged.

## PRs #3/#5/#6/#7/#8/#9 Status

These old PR numbers from Sprint 21 are NOT in the sprint75 proof index. They were either:
- Never created (replaced by different-numbered PRs in later sprints)
- Closed in favor of new PRs
- Superseded entirely by bulk publication sprints

Authority: sprint75 proof index has 9 PDF PRs (#1, #2, #4, #11, #17-#21), all merged.
Current open PDF PRs: 0 (confirmed from sprint75 remote-repo-state-before.json).

## Separation of Two Publication Events

| Event | State |
|-------|-------|
| PDF example code publication (Program.cs, csproj, README skeleton) | COMPLETE — 19/19 merged |
| PDF README I/O section publication | PENDING — 0/19 remote, 19/19 local handoff ready, blocked by PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL |

## Conclusion

- The "14 blocked" claim from Sprint 21 is no longer current.
- All 19 PDF examples are remotely present and verified.
- The remaining work is README I/O section publication — a distinct publication event.
- No correction package required for example-code publication.
- Weekly Review Item 1: **VERIFIED_HISTORICAL_BUT_SUPERSEDED**
