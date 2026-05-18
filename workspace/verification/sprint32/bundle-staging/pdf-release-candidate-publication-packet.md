# PDF LowCode Release Candidate Publication Packet — Sprint 32

**Date:** 2026-05-18
**Status:** APPROVAL_BLOCKED

## Already Published (DO NOT republish)

Merger, TextExtractor, PdfAConverter, Splitter, Optimizer (5 examples on target repo main branch)

## PR Packages Ready to Publish (14 new examples)

| PR | Package | Examples | Version | Bin/Obj |
|----|---------|----------|---------|---------|
| #3 | pdf-controlled-pilot | DocConverter, Html, XlsConverter | 26.4.0 | 0 |
| #5 | pdf-controlled-pilot-pr5 | Jpeg, Png, Tiff | 26.4.0 | 0 |
| #6 | pdf-controlled-pilot-pr6 | ImageExtractor, TableGenerator, TocGenerator | 26.4.0 | 0 |
| #7 | pdf-controlled-pilot-pr7 | Security, FormFlattener | 26.5.0 | 0 |
| #8 | pdf-controlled-pilot-pr8 | FormEditor, FormExporter | 26.5.0 | 0 |
| #9 | pdf-controlled-pilot-pr9 | Signature | 26.5.0 | 0 |

## Publish Commands

```powershell
# Prerequisites
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable('GH_TOKEN', 'User')
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = 'APPROVE_LIVE_PR'

# PR #3
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --promote-latest

# PR #5
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr5 --promote-latest

# PR #6
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr6 --promote-latest

# PR #7
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr7 --promote-latest

# PR #8
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr8 --promote-latest

# PR #9
.venv\Scripts\python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr9 --promote-latest
```

## After Publication

- Run post-merge verification for all 14 new examples
- Total examples will be 19/19 pilot = 100% pilot coverage
