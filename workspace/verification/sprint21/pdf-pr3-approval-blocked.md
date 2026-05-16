# PDF PR#3 Publication Result — Sprint 21

**Status:** APPROVAL_BLOCKED
**Package:** `workspace/pr-dry-run/pdf-controlled-pilot`
**Examples:** DocConverter, Html, XlsConverter
**Dry-run:** SIMULATION_PASSED

## Blocker

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` env var is absent.

## To Publish

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = "APPROVE_LIVE_PR"
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot --promote-latest
```
