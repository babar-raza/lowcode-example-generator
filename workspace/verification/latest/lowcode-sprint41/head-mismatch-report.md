# Lane 0 — HEAD Mismatch Report

**Status:** RESOLVED

## Mismatch

- Sprint 40 `final-state-summary.json` HEAD: `0a4e695`
- Sprint 40 `git-log.txt` first line: `1add673`
- Current HEAD: `1add673`

## Classification of Commit 1add673

```
test(denominator): expand to all 6 families, add conservation equation, fix schema
```

**Author:** Babar Raza
**Date:** 2026-05-19T12:20:40+0500
**Files changed:** 4 files, +169/-201 lines

| File | Change |
|------|--------|
| pipeline/configs/families/disabled/email.yml | DELETED (89 lines) |
| pipeline/configs/families/disabled/slides.yml | DELETED (90 lines) |
| pipeline/schemas/denominator.schema.json | Modified (+11/-?) |
| tests/unit/test_denominator_model.py | Modified (+180/-?) |

**Classification:** POST_SPRINT40_BUNDLE_WORK

This commit was created after the Sprint 40 evidence bundle was built (which captured `0a4e695` as HEAD in final-state-summary.json) but before Sprint 41 started. The git-log.txt in the Sprint 40 bundle includes it because it was captured at a different time than the summary.

**Impact:** Beneficial — adds denominator test coverage for all 6 families (was only 3), adds conservation equation test, fixes schema to support all families. Increases test count from ~2130 to 2187.

**Sprint 41 treatment:** Include in Sprint 41 closure state. HEAD at start of Sprint 41 = 1add673.
