# PDF PR #1 Post-Merge Verification

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/pdf-pr1-post-merge-verification.json`
**Verdict:** POST_MERGE_VERIFIED

## Merge Details

- PR #1: closed/merged
- Merge SHA: `a9f9e254fbdbd012e6486e699395298e427169eb`
- Merged at: 2026-05-06T11:01:12Z

## Remote Verification

| Check | Result |
|---|---|
| main contains merger | YES |
| main contains text-extractor | YES |
| main contains splitter | NO (excluded) |
| main contains optimizer | NO (excluded) |
| README exists | YES (4282 bytes) |
| README lists only approved examples | YES |
| No bin/obj/secrets | CLEAN |
| Token leakage | NONE |

## Post-Merge Clean Checkout from Main

| Example | Restore | Build | Run | Verdict |
|---|---|---|---|---|
| merger | PASS | PASS (0W 0E) | PASS | ALL_PASS |
| text-extractor | PASS | PASS (0W 0E) | PASS | ALL_PASS |

Both examples build and run from a fresh clone of main. No failed or backlogged examples published.
