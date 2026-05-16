# PDF PR#6 Publication Result — Sprint 21

**Status:** APPROVAL_BLOCKED
**Package:** `workspace/pr-dry-run/pdf-controlled-pilot-pr6`
**Examples:** ImageExtractor, TableGenerator, TocGenerator
**Dry-run:** SIMULATION_PASSED
**Generation method:** Template-first (all 3 types)

## Blocker

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` env var is absent.

## To Publish (after PR#5 merged)

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = "APPROVE_LIVE_PR"
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr6 --promote-latest
```
