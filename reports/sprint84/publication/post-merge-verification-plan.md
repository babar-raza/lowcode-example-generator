Sprint 84 — Post-Merge Verification Plan
=========================================
Date: 2026-05-24
Author: Lane E

## Purpose
After all 6 family PRs are merged, verify that remote repos reflect the expected README I/O content.

## Verification Steps Per Family

### 1. Check remote README I/O presence
For each of 42 examples, verify README.md exists at remote_path and contains IO section.
Expected: `## Input and Output` header or equivalent in each README.

### 2. Email/Slides runtime check
Email and Slides runtime was repaired in Sprint 73. Carry-forward: REPAIRED.
After merge: run smoke test to confirm runtime still valid.
```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run --family email --require-validation
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run --family slides --require-validation
```

### 3. PDF verification
19 examples across 7 waves. FormImporter remains BLOCKED_EXTERNAL (Wave H).
Verify 19 READMEs present and valid after merge.

### 4. Update publication-truth-matrix
For each merged example:
- Set `remote_readme_io_classification`: "HAS_IO_SECTION"
- Set `readme_io_post_merge_verified`: true
- Set `pr_merged_at`: <timestamp>

### 5. Release status
```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples release-status --promote-latest
```

## Status
APPROVAL_BLOCKED — plan ready for execution when gates are lifted.
