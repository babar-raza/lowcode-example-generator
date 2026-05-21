# README Update Package Summary — Sprint 61 Phase 8

## Overview

Sprint 61 Phase 4 found that 0/42 published example READMEs have I/O format
documentation. This document summarizes the correction package ready for Sprint 62
publication.

---

## Before / After State

| Metric | Before (Current) | After (With Corrections) |
|--------|-----------------|--------------------------|
| IO_DOC_MATCH | 0/42 | 38/42 |
| INPUT_DOC_MISSING | 3/42 | 3/42 (no input.EXT in Program.cs) |
| BOTH_DOC_MISSING | 42/42 → 1/42 | 1/42 (pdf-pdf-aconverter, no local pkg) |

---

## Correction Coverage

- **41/42** scenarios have corrections with known I/O text ready to add
- **1/42** scenario (`pdf-pdf-aconverter`) requires manual correction (no local package)
- **3/42** scenarios have output-only known I/O (input is data source/runtime):
  - `words-mail-merger` — input is data source
  - `words-report-builder` — input is data source + template
  - `pdf-text-extractor` — output is stdout (no output file)

---

## Correction Template

For each example, the following block is added after the description:

```markdown
## I/O Formats

**Input:** `.{ext}` file
**Output:** `.{ext}` file
```

Special cases documented in `readme-io-correction-plan.json`.

---

## Families Covered

cells, diagram, email, pdf, slides, words (all 6 families)

---

## Publication Gate

Pushing README corrections requires:

```
PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH
```

This is enforced by `check_readme_audit_gate()` wired into `publish-pr` (Phase 5).

---

## Status

**AUDIT_COMPLETE_PUSH_DEFERRED_TO_SPRINT62**

Sprint 61 delivers:
- Honest audit evidence (0/42 before, 38/42 achievable after)
- Per-example correction plan (41 corrections with known I/O)
- Policy document (`readme-io-documentation-policy.md`)
- Wired gate (`check_readme_audit_gate` in `publish-pr` live mode)

The live README push is deferred to Sprint 62.
