# PDF Approval Runbook — Sprint 52

## Prerequisites
- PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR must be set
- GITHUB_TOKEN must map to classic PAT (GH_TOKEN)

## Step 1: Create replacement PRs
```bash
export GITHUB_TOKEN="$GH_TOKEN"
export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family pdf --publish \
  --approval-token APPROVE_LIVE_PR
```

## Expected PR titles
- "Add verified Aspose.Pdf LowCode examples for .NET controlled pilot"

## Expected types per PR batch
14 types: DocConverter, XlsConverter, Html, Jpeg, Png, Tiff, TocGenerator, TableGenerator, ImageExtractor, Security, FormFlattener, FormEditor, FormExporter, Signature

## Step 2: Merge (requires separate approval)
```bash
export PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family pdf --pr-number <N> --merge \
  --approval-token APPROVE_MERGE_PR
```

## Validation gates
- Build: `dotnet build` on target repo branch
- Conflict-free: PR must have no merge conflicts
- Tests: Scenario contracts must pass for all 14 types

## Rollback strategy
- Close PR without merging if build fails or conflicts detected
- No force operations on target repo

## Current state: Approvals ABSENT — producing ready-to-run packet only.
