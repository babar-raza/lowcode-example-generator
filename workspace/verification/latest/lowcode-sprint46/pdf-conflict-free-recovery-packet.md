# PDF Conflict-Free Recovery Packet — Sprint 46

## Status: DRY-RUN (both approval gates absent)

## Strategy: Recreate All Six PRs

All 6 PRs (#5-#10) conflict on `README.md`. Recreating from fresh branches against current target-repo main resolves all conflicts.

## Recovery Steps (when approved)

### 1. Set Approval Gates
```bash
export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
export PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
```

### 2. Close Existing PRs
```bash
for pr in 5 6 7 8 9 10; do
  gh pr close $pr --repo aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples
done
```

### 3. Recreate PRs via Pipeline
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family pdf --publish --approval-token APPROVE_LIVE_PR \
  --package-path workspace/pr-dry-run/pdf-controlled-pilot/

# Repeat for pr5, pr6, pr7, pr8, pr9 directories
```

### 4. Verify Conflict-Free State
```bash
gh pr list --repo aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples \
  --json number,mergeable
```

### 5. Merge (after conflict verification)
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family pdf --pr-number <N> --merge --approval-token APPROVE_MERGE_PR
```

## Rollback
Close any failed PR. Local packages are preserved. Re-run publish-pr.

## Packages
| GitHub PR | Local Package | Examples |
|-----------|--------------|----------|
| new (replaces #5) | pdf-controlled-pilot/ | doc-converter, html, xls-converter |
| new (replaces #6) | pdf-controlled-pilot-pr5/ | jpeg, png, tiff |
| new (replaces #7) | pdf-controlled-pilot-pr6/ | image-extractor, table-generator, toc-generator |
| new (replaces #8) | pdf-controlled-pilot-pr7/ | form-flattener, security |
| new (replaces #9) | pdf-controlled-pilot-pr8/ | form-editor, form-exporter |
| new (replaces #10) | pdf-controlled-pilot-pr9/ | signature |
