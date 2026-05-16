# PDF PR#5 Publication Result — Sprint 21

**Status:** APPROVAL_BLOCKED
**Package:** `workspace/pr-dry-run/pdf-controlled-pilot-pr5`
**Examples:** Jpeg, Png, Tiff
**Dry-run:** SIMULATION_PASSED
**Png quarantine:** CLEARED (Sprint 17, ResultCollection.Count > 0 validation)

## Blocker

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` env var is absent.

## To Publish (after PR#3 merged)

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = "APPROVE_LIVE_PR"
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr5 --promote-latest
```
