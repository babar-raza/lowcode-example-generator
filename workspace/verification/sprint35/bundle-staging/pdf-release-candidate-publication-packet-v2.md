# PDF LowCode Release Candidate Publication Packet v2 (Sprint 33)

## Status: APPROVAL_BLOCKED

**Gate:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` not set.

## Overview

- **14 new examples** across **6 PR packages** are ready to publish.
- **5 examples already published**: Merger, TextExtractor, PdfAConverter, Splitter, Optimizer — DO NOT republish.
- All 6 packages have **0 bin/obj files** (Sprint 30 cleanup persists through Sprint 33).
- All 6 packages have **SIMULATION_PASSED** dry-run status.

## PR Package Summary

| PR# | Package | Examples | Version | Status |
|-----|---------|----------|---------|--------|
| #3 | pdf-controlled-pilot | DocConverter, Html, XlsConverter | 26.4.0 | CLEAN |
| #5 | pdf-controlled-pilot-pr5 | Jpeg, Png, Tiff | 26.4.0 | CLEAN |
| #6 | pdf-controlled-pilot-pr6 | ImageExtractor, TableGenerator, TocGenerator | 26.4.0 | CLEAN |
| #7 | pdf-controlled-pilot-pr7 | **Security, FormFlattener** | 26.5.0 | CLEAN |
| #8 | pdf-controlled-pilot-pr8 | FormEditor, FormExporter | 26.5.0 | CLEAN |
| #9 | pdf-controlled-pilot-pr9 | Signature | 26.5.0 | CLEAN |

## To Publish

```powershell
# 1. Map GH_TOKEN to GITHUB_TOKEN
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable('GH_TOKEN', 'User')

# 2. Set approval gate
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = 'APPROVE_LIVE_PR'

# 3. Publish in order (review+merge each before next)
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --promote-latest
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr5 --promote-latest
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr6 --promote-latest
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr7 --promote-latest
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr8 --promote-latest
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr9 --promote-latest
```

## Rollback

- **Before merge**: Close the PR. No rollback needed.
- **After merge with error**: Open a follow-up PR to remove the erroneous example(s). Do NOT force-push or reset main.
- **Token compromise**: Revoke at github.com/settings/tokens immediately. Generate new classic PAT (repo scope).

## Post-Merge Verification

After each PR merge, run:
```bash
.venv/Scripts/python.exe -m plugin_examples run --family pdf --tier 5 --promote-latest
```

Expected result per example: `POST_MERGE_VERIFIED`

## After Publication

Total PDF examples: **19** (5 already published + 14 new)
Full pilot coverage: **19/19 (100%)**
Portfolio total: **42 examples** (28 current + 14 new)
