# PDF PR#5 — Approval Blocked

**Sprint:** sprint23 | **Package:** `workspace/pr-dry-run/pdf-controlled-pilot-pr5/` | **Examples:** jpeg, png, tiff
**Blocker:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` not set. Publish AFTER PR#3 merged.

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr5 --promote-latest
```
