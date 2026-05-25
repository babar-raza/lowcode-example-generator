Sprint 85 — Branch Delete Plan
================================
Date: 2026-05-24
Author: Lane E

## Plan: DEFERRED (no PRs or merges to trigger branch deletion)

### Branch Deletion Safety Gate
A branch may be deleted ONLY when ALL of these conditions are met:
1. The PR for the family was merged successfully.
2. Post-merge verification confirms all README I/O sections are present.
3. The branch name matches `lowcode-examples-{family}-sprint85`.
4. The branch is NOT main, master, or a root-README PR branch.

### Branches to Delete (when conditions met)
- lowcode-examples-email-sprint85
- lowcode-examples-slides-sprint85
- lowcode-examples-diagram-sprint85
- lowcode-examples-cells-sprint85
- lowcode-examples-words-sprint85
- lowcode-examples-pdf-sprint85

### Branches NEVER to Delete
- main/master on any destination repo
- Branches for PRs #5, #7, #2 (root README PRs)
- Any branch not created by this sprint
