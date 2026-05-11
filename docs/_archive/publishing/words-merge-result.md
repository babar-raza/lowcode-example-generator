# Words PR Merge Result

**Sprint:** Words PR Merge and Post-Merge Verification Sprint
**Date:** 2026-05-03
**Result:** POST_MERGE_VERIFIED

---

## Merge Summary

| Field | Value |
|---|---|
| PR URL | https://github.com/aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples/pull/1 |
| PR Number | #1 |
| State | closed (merged) |
| Merged At | 2026-05-03T08:35:49Z |
| Merge Commit SHA | `b66fb43023d4d1af7162270ac9d3ef3ef881451f` |
| Merge Method | merge (merge commit) |
| Approval Token Used | `APPROVE_MERGE_PR` |
| Target Branch | `main` |
| Source Branch | `plugin-examples/words/20260502-135703` |

---

## Approval

- **Token:** `APPROVE_MERGE_PR` — passed as CLI argument only, never persisted
- **Separate from:** `APPROVE_LIVE_PR` (PR creation token, explicitly rejected for merge)
- **GITHUB_TOKEN:** set as classic PAT with repo scope; never logged or serialized

---

## Command Run

```
PYTHONPATH=src GITHUB_TOKEN="$GH_TOKEN" .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family words --pr-number 1 --merge --approval-token APPROVE_MERGE_PR --promote-latest
```

---

## Post-Merge Verification

| Check | Result |
|---|---|
| PR merged=true | PASS |
| merge_commit_sha recorded | PASS — `b66fb43023d4d1af7162270ac9d3ef3ef881451f` |
| main branch contains all 4 examples | PASS |
| no unexpected files in main | PASS |
| source branch still exists | PASS — not deleted |
| clean-clone from main | PASS |

### Clean Checkout from Main (4/4 ALL_PASS)

| Example | Build | Run | Output |
|---|---|---|---|
| converter | PASS | PASS | output.pdf |
| watermarker | PASS | PASS | Watermark applied successfully. |
| splitter | PASS | PASS | ExtractPages succeeded: output.docx |
| replacer | PASS | PASS | Replace succeeded (result=1). output.docx |

---

## What Was NOT Done

- Branch not deleted
- Cells PR not touched
- No new PRs created
- No push to main outside PR merge API
- Token not written to any file
