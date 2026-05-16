# PDF PR5 — APPROVAL_BLOCKED

**Sprint:** sprint21
**Date:** 2026-05-16
**Package:** workspace/pr-dry-run/pdf-controlled-pilot-pr5
**Examples:** jpeg, png, tiff

## Dry-run Result

`SIMULATION_PASSED` — package verified, gate verdict PR_DRY_RUN_READY, repo access ready.

## Blocker

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` not set to `APPROVE_LIVE_PR`.

## Publication Command (when approved)

```bash
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL='APPROVE_LIVE_PR'
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf --publish   --approval-token APPROVE_LIVE_PR   --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr5   --promote-latest
```
