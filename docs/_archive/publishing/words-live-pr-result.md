# Words Live PR Canary Result

**Sprint:** Words Live PR Canary Sprint
**Date:** 2026-05-02
**Result:** PR_CREATED

---

## PR Details

| Field | Value |
|---|---|
| PR URL | https://github.com/aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples/pull/1 |
| PR Number | #1 |
| PR Title | Add verified Aspose.Words LowCode examples for .NET controlled pilot |
| Branch | `plugin-examples/words/20260502-135703` |
| Base | `main` |
| State | OPEN |
| Merged | NO — awaiting human review |

---

## Package

| Field | Value |
|---|---|
| Package Path | `workspace/pr-dry-run/words-controlled-pilot/` |
| Files Committed | 23 |
| Examples Count | 4 |
| NuGet Version | 26.4.0 |
| Target Framework | net8.0 |

---

## Examples Included

| Example | Path in PR |
|---|---|
| Converter | `examples/words/lowcode/converter/` |
| Replacer | `examples/words/lowcode/replacer/` |
| Splitter | `examples/words/lowcode/splitter/` |
| Watermarker | `examples/words/lowcode/watermarker/` |

---

## Validation Checks

| Check | Result |
|---|---|
| PR URL exists | PASS |
| PR number exists | PASS |
| Target repo is aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples | PASS |
| Source branch is not main | PASS (`plugin-examples/words/20260502-135703`) |
| Base branch is main | PASS |
| files changed = 23 (expected) | PASS |
| examples/words/lowcode/converter exists | PASS |
| examples/words/lowcode/watermarker exists | PASS |
| examples/words/lowcode/splitter exists | PASS |
| examples/words/lowcode/replacer exists | PASS |
| No Cells files | PASS |
| No PDF files | PASS |
| No blocked Words scenarios | PASS |
| PR_SUMMARY.md excluded | PASS |
| bin/ excluded | PASS |
| No token leakage | PASS — token never logged or serialized |
| PR is OPEN | PASS |
| PR is NOT merged | PASS — mergedAt=null |

---

## Approval

- **Approval source:** Human explicit approval (APPROVE_LIVE_PR token passed as CLI argument)
- **Token persisted to env:** NO — passed via `--approval-token` argument only
- **Token written to evidence:** NO

---

## Command Run

```
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family words --publish --approval-token APPROVE_LIVE_PR --promote-latest
```

**GITHUB_TOKEN requirement:** must be a classic PAT with `repo` scope, OR a fine-grained PAT with
"Contents: Read and Write" permission granted for the target repo. The pipeline reads only
`GITHUB_TOKEN` — the operator is responsible for ensuring the correct token is set before running.

During this canary, the effective GITHUB_TOKEN was a classic PAT assigned for the process only.
A fine-grained PAT that lacked Contents write permission failed at POST /git/blobs (HTTP 403).
The operator corrected this by assigning a suitable token to `GITHUB_TOKEN` for the process.

---

## What Was NOT Done

- Cells PR: NOT created
- Merge: NOT performed
- Push to main: NOT performed
- New examples generated: NO
- PDF publication: NO
- Token written to any file: NO

---

## Next Step

1. Human reviews PR #1 at https://github.com/aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples/pull/1
2. Approve and merge when satisfied with example quality
3. After Words PR is merged: proceed with Cells live PR canary (9 examples)
4. Record `GITHUB_TOKEN` clarification: must be a classic PAT with `repo` scope, OR a fine-grained PAT with "Contents: Read and Write" permission for target repos
