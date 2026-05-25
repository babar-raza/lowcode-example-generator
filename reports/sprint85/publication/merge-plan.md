Sprint 85 — Merge Plan
=======================
Date: 2026-05-24
Author: Lane E

## Merge Plan: DEFERRED (no PRs to merge)

### Per-Family Merge Steps (when PRs exist)
For each family PR in merge order (email → slides → diagram → cells → words → pdf):
1. Verify PR CI status is green.
2. Verify PR diff matches publication-file-plan.json.
3. Merge via GitHub merge button (squash or merge commit per repo policy).
4. Fetch remote main to confirm merge.
5. Verify example README I/O sections are present.
6. Record merge SHA in merge-result.json.

### Conflict Resolution
If merge conflict occurs:
- Do NOT force merge.
- Investigate conflict source.
- If conflict is with root README PR (#5/#7/#2), rebase sprint85 branch excluding root README.
- If conflict is unexpected, halt and document.

### Approval Required
PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR must be set before any merge.
