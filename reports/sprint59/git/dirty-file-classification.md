# Dirty File Classification — Sprint 59 Phase 1

**Date:** 2026-05-21
**Total dirty files:** 4 source (unstaged modified) + 106 workspace/verification (unstaged modified) + 2 untracked directories

---

## Category A: Source Changes Required for Sprint 58 Repair
**Action: Stage and commit with exact paths**

| File | Change Summary | Stage? |
|------|---------------|--------|
| `pipeline/configs/families/pdf.yml` | Added `using Aspose.Pdf.Text;` constraint to PdfAConverter.required | YES |
| `src/plugin_examples/publisher/github_pr_merger.py` | Added `_api_delete()`, `_LOWCODE_BRANCH_PREFIXES`, `delete_branch_after_merge()` | YES |
| `tests/unit/test_llm_generation.py` | Added `TestPdfAConverterConstraint` (3 tests) | YES |
| `tests/unit/test_merge_governance.py` | Added `TestBranchAutoDelete` (7 tests) | YES |

**Commit plan:** Single commit — "fix(pdf): add PdfAConverter using constraint; feat(merger): implement branch auto-delete with tests"

---

## Category B: workspace/manifests — Generated Pipeline State
**Action: Stage and commit (workspace/manifests is committed in this repo)**

| File | Change Summary | Stage? |
|------|---------------|--------|
| `workspace/manifests/example-index.json` | Updated from regeneration runs | YES |
| `workspace/manifests/existing-examples-index.json` | Updated from regeneration runs | YES |
| `workspace/manifests/fixture-registry.json` | Updated from regeneration runs | YES |
| `workspace/manifests/package-lock.json` | Updated from regeneration runs | YES |
| `workspace/manifests/scenario-catalog.json` | Updated from regeneration runs | YES |

**Commit plan:** Single commit — "chore(workspace): update manifests from Sprint 58/59 regeneration runs"

---

## Category C: workspace/verification/latest — Generated Verification State
**Action: Stage and commit (workspace/verification/latest is committed in this repo — these are the canonical pipeline outputs that get --promote-latest)**

Files: 101 modified files in `workspace/verification/latest/` and `workspace/verification/latest/families/`

Breakdown:
- `workspace/verification/latest/families/cells/` (9 files) — cells regeneration state
- `workspace/verification/latest/families/words/` (10 files) — words regeneration state
- `workspace/verification/latest/families/pdf/` (9 files) — pdf regeneration state (including PdfAConverter)
- `workspace/verification/latest/families/diagram/` (9 files) — diagram regeneration state
- `workspace/verification/latest/families/email/` (9 files) — email regeneration state
- `workspace/verification/latest/families/slides/` (9 files) — slides regeneration state
- `workspace/verification/latest/` root (18 files) — cross-family aggregation

**Stage as group:** `git add workspace/verification/latest/`

**Commit plan:** Single commit — "chore(verification): promote Sprint 58/59 all-family pipeline outputs to latest"

---

## Category D: Untracked Directories
**Action: Stage and commit (these are the Sprint evidence bundles)**

| Path | Description | Stage? |
|------|-------------|--------|
| `reports/sprint58/` | Sprint 58 evidence bundle (76 files) | YES |
| `reports/sprint59/` | Sprint 59 evidence bundle (in progress) | Stage at close |

**Commit plan:** Separate commit — "docs(sprint58): add Sprint 58 evidence bundle (76 files)"
**Sprint 59 reports:** Add at final closure commit.

---

## Category E: Must Not Commit
None identified. All dirty files fall into actionable categories above.

---

## Summary

| Category | Files | Action |
|----------|-------|--------|
| A — Source changes | 4 | Commit with exact paths |
| B — workspace/manifests | 5 | Commit as group |
| C — workspace/verification/latest | 101 | Commit as group |
| D — Untracked reports/ | 2 dirs | Commit at phase/sprint close |
| E — Must not commit | 0 | — |

**Total dirty:** ~110 files + 2 untracked dirs
**All classified:** YES
