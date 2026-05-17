# PDF PR#3 — Approval Blocked

**Sprint:** sprint23
**Date:** 2026-05-17
**Package:** `workspace/pr-dry-run/pdf-controlled-pilot/`
**Examples:** doc-converter, html, xls-converter
**Package audit:** PASS
**Blocker:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` not set

To publish:
```bash
export GITHUB_TOKEN=$GH_TOKEN
export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot --promote-latest
```
