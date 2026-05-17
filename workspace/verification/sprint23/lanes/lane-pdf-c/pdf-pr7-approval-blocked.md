# PDF PR#7 — Approval Blocked

**Sprint:** sprint23
**Package:** `workspace/pr-dry-run/pdf-controlled-pilot-pr7/`
**Types:** Security, FormFlattener (Wave E)
**Package version:** Aspose.PDF 26.5.0
**Status:** APPROVAL_BLOCKED — `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` absent

## Publish Command (when approval granted)

```bash
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = 'APPROVE_LIVE_PR'
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family pdf \
  --publish \
  --approval-token APPROVE_LIVE_PR \
  --package-path pdf-controlled-pilot-pr7
```

## Evidence

- Both Security and FormFlattener: ALL_PASS (build + runtime)
- Template-first generation — harness-verified patterns from Sprint 22
- Security: PDF encrypted output confirmed
- FormFlattener: AcroForm flattened, 0 fields after flatten confirmed
