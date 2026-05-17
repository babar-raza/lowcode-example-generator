# PR#3 Approval Blocked — Sprint 30

**PR:** PR#3 (Aspose.PDF 26.4.0 — DocConverter, Html, XlsConverter)
**Sprint:** sprint30
**Date:** 2026-05-17
**Status:** APPROVAL_BLOCKED

## Reason

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` is not set in the environment. Live publication requires this variable to be set to `APPROVE_LIVE_PR`.

## Package State

- bin/obj artifacts: **NONE** (package is clean — no cleanup needed for PR#3)
- Blocking flags: **NONE**
- Publication readiness: **READY** pending approval env var

## To Publish

```powershell
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = 'APPROVE_LIVE_PR'
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable('GH_TOKEN', 'User')
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --promote-latest
```
