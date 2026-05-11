# Cells Live PR Canary Result

**Sprint:** Cells Live PR Canary Sprint
**Date:** 2026-05-02
**Result:** PR_CREATED

---

## PR Details

| Field | Value |
|---|---|
| PR URL | https://github.com/aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples/pull/1 |
| PR Number | #1 |
| PR Title | Add verified Aspose.Cells LowCode examples for .NET controlled pilot |
| Branch | `plugin-examples/cells/20260502-153727` |
| Base | `main` |
| State | OPEN |
| Merged | NO — awaiting human review |

---

## Package

| Field | Value |
|---|---|
| Package Path | `workspace/pr-dry-run/cells-controlled-pilot/` |
| Files Committed | 57 |
| Examples Count | 9 |
| NuGet Version | 26.4.0 |
| Target Framework | net8.0 |

---

## Examples Included

| Example | Path in PR |
|---|---|
| HtmlConverter | `examples/cells/lowcode/html-converter/` |
| ImageConverter | `examples/cells/lowcode/image-converter/` |
| JsonConverter | `examples/cells/lowcode/json-converter/` |
| PdfConverter | `examples/cells/lowcode/pdf-converter/` |
| SpreadsheetConverter | `examples/cells/lowcode/spreadsheet-converter/` |
| SpreadsheetLocker | `examples/cells/lowcode/spreadsheet-locker/` |
| SpreadsheetMerger | `examples/cells/lowcode/spreadsheet-merger/` |
| SpreadsheetSplitter | `examples/cells/lowcode/spreadsheet-splitter/` |
| TextConverter | `examples/cells/lowcode/text-converter/` |

---

## Validation Checks

| Check | Result |
|---|---|
| PR URL exists | PASS |
| PR number exists | PASS |
| Target repo is aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples | PASS |
| Source branch is not main | PASS (`plugin-examples/cells/20260502-153727`) |
| Base branch is main | PASS |
| files changed = 57 (expected) | PASS |
| All 9 Cells examples present | PASS |
| No Words files | PASS |
| No PDF family files | PASS |
| PR_SUMMARY.md excluded | PASS |
| bin/ excluded | PASS |
| No token leakage | PASS — token never logged or serialized |
| PR is OPEN | PASS |
| PR is NOT merged | PASS — mergedAt=null |
| PR body has DO NOT MERGE warning | PASS |

---

## Approval

- **Approval source:** Human explicit approval (APPROVE_LIVE_PR token passed as CLI argument)
- **Token persisted to env:** NO — passed via `--approval-token` argument only
- **Token written to evidence:** NO

---

## Command Run

```
PYTHONPATH=src GITHUB_TOKEN="$GH_TOKEN" .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family cells --publish --approval-token APPROVE_LIVE_PR --promote-latest
```

**GITHUB_TOKEN requirement:** must be a classic PAT with `repo` scope, OR a fine-grained PAT with
"Contents: Read and Write" permission granted for the target repo. The pipeline reads only
`GITHUB_TOKEN` — the operator is responsible for ensuring the correct token is set before running.

Same token pattern as Words canary: classic PAT assigned for the process only.

---

## What Was NOT Done

- Words additional PR: NOT created
- PDF PR: NOT created
- Merge: NOT performed
- Push to main: NOT performed
- New examples generated: NO
- Token written to any file: NO

---

## Next Step

1. Human reviews PR #1 at https://github.com/aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples/pull/1
2. Approve and merge when satisfied with example quality
3. Both Words PR #1 and Cells PR #1 are now open — human review and merge at discretion
