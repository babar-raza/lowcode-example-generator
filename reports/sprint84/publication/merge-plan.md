Sprint 84 — Merge Plan
======================
Date: 2026-05-24
Author: Lane E

## Preconditions
1. PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR (6 PRs created)
2. PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR (all CI checks pass)
3. All PRs reviewed and approved by maintainer

## Merge Sequence

### Step 1: email
```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family email --pr-number <N> --merge --approval-token APPROVE_MERGE_PR
```
Verify: 1 README in remote examples/email/lowcode/converter/

### Step 2: slides
```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family slides --pr-number <N> --merge --approval-token APPROVE_MERGE_PR
```
Verify: 3 READMEs in remote examples/slides/lowcode/{compress,convert,merger}/

### Step 3: diagram
```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family diagram --pr-number <N> --merge --approval-token APPROVE_MERGE_PR
```
Verify: 2 READMEs in remote examples/diagram/lowcode/{diagram-diagram-converter,diagram-pdf-converter}/

### Step 4: cells
```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family cells --pr-number <N> --merge --approval-token APPROVE_MERGE_PR
```
Verify: 9 READMEs in remote examples/cells/lowcode/{html-converter,...}/

### Step 5: words
```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family words --pr-number <N> --merge --approval-token APPROVE_MERGE_PR
```
Verify: 8 READMEs in remote examples/words/lowcode/{comparer,...}/

### Step 6: pdf
```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family pdf --pr-number <N> --merge --approval-token APPROVE_MERGE_PR
```
Verify: 19 READMEs in remote examples/pdf/lowcode/{doc-converter,...}/

## After All Merges
1. Run post-merge-verification (see post-merge-verification-plan.md)
2. Delete branches (see branch-delete-plan.md)
3. Update publication-truth-matrix-final.json with merge timestamps
4. Run release-status --promote-latest

## Status
APPROVAL_BLOCKED — this plan is ready for execution when gates are lifted.
