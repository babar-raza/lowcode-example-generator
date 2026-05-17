# Post-Publication Verification — Not Run (Approval Blocked)

**Sprint:** 29
**Date:** 2026-05-17
**Status:** NOT_RUN_APPROVAL_BLOCKED

## Reason

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` is not set to `APPROVE_LIVE_PR`. No live PRs were created in Sprint 29. Therefore no post-publication verification was run.

## What Would Run

If approval were set, the following would be verified for each created PR:
- `gh pr view` — PR URL, number, branch, title/body, labels
- File list — only intended examples, no bin/obj, no secrets
- No already-published examples included

## PR Packages Awaiting Approval

| PR | Package | Types | Version | Audit Flags |
|----|---------|-------|---------|-------------|
| PR#3 | pdf-controlled-pilot | DocConverter, Html, XlsConverter | 26.4.0 | None |
| PR#5 | pdf-controlled-pilot-pr5 | Jpeg, Tiff, Png | 26.4.0 | None |
| PR#6 | pdf-controlled-pilot-pr6 | TocGenerator, TableGenerator, ImageExtractor | 26.4.0 | None |
| PR#7 | pdf-controlled-pilot-pr7 | Security, FormFlattener | 26.5.0 | None |
| PR#8 | pdf-controlled-pilot-pr8 | FormEditor, FormExporter | 26.5.0 | bin/obj present — cleanup required |
| PR#9 | pdf-controlled-pilot-pr9 | Signature | 26.5.0 | bin/obj present — cleanup required |

## Pre-Publication Actions Required Before PR#8/#9

1. Remove `bin/` and `obj/` directories from `workspace/pr-dry-run/pdf-controlled-pilot-pr8/examples/pdf/lowcode/form-editor/`
2. Remove `bin/` and `obj/` directories from `workspace/pr-dry-run/pdf-controlled-pilot-pr8/examples/pdf/lowcode/form-exporter/`
3. Remove `bin/` and `obj/` directories from `workspace/pr-dry-run/pdf-controlled-pilot-pr9/examples/pdf/lowcode/signature/`
4. Re-run dry-run validation for PR#8 and PR#9 after cleanup

## Action

Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` and rerun Sprint 30 publication lanes (after PR#8/#9 bin/obj cleanup).
