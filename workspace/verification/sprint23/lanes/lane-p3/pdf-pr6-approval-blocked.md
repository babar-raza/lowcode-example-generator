# PDF PR#6 — Approval Blocked

**Sprint:** sprint23 | **Package:** `workspace/pr-dry-run/pdf-controlled-pilot-pr6/` | **Examples:** image-extractor, table-generator, toc-generator
**Blocker:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` not set. Publish AFTER PR#5 merged.

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf --publish --approval-token APPROVE_LIVE_PR --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr6 --promote-latest
```
