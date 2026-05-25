Sprint 85 — Post-Merge Verification Plan
==========================================
Date: 2026-05-24
Author: Lane E

## Plan: DEFERRED (no PRs to merge)

### Per-Family Post-Merge Checks
1. Fetch remote main branch after merge.
2. For each example in the family:
   a. Verify README.md exists at expected path.
   b. Verify README.md contains ## Input and ## Output sections.
   c. Verify Program.cs is unchanged.
3. Verify root README is unchanged (not included in PR).
4. Record remote SHA for each verified file.

### Failure Handling
If any post-merge check fails:
- Do NOT delete the branch.
- Document the failure in post-merge-verification.json.
- Halt further merges until investigated.

### Evidence
- reports/sprint85/publication/post-merge-verification.json (per-family results)
