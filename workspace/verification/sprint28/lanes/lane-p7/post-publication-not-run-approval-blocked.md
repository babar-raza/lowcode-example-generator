# Post-Publication Verification — Not Run (Approval Blocked)

**Sprint:** 28
**Date:** 2026-05-17
**Status:** NOT_RUN_APPROVAL_BLOCKED

## Reason

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` is not set to `APPROVE_LIVE_PR`. No live PRs were created in Sprint 28. Therefore no post-publication verification was run.

## What Would Run

If approval were set, the following would be verified for each created PR:
- `gh pr view` — PR URL, number, branch, title/body, labels
- File list — only intended examples, no bin/obj, no secrets
- No already-published examples included

## PR Packages Awaiting Approval

| PR | Package | Types | Version |
|----|---------|-------|---------|
| PR#3 | pdf-controlled-pilot | DocConverter, XlsConverter, Html | 26.4.0 |
| PR#5 | pdf-controlled-pilot-pr5 | Jpeg, Tiff, Png | 26.4.0 |
| PR#6 | pdf-controlled-pilot-pr6 | TocGenerator, TableGenerator, ImageExtractor | 26.4.0 |
| PR#7 | pdf-controlled-pilot-pr7 | Security, FormFlattener | 26.5.0 |
| PR#8 | pdf-controlled-pilot-pr8 | FormEditor, FormExporter | 26.5.0 |
| PR#9 | pdf-controlled-pilot-pr9 | Signature | 26.5.0 |

## Action

Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` and rerun Sprint 29 publication lanes.
