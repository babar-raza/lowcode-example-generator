# State Sync Summary

**Run ID:** sysqual-20260528-001
**Date:** 2026-05-28

## Product State After Qualification

### LowCode Confirmed (6)
| Product | Prior Status | E2E Status | Publication |
|---|---|---|---|
| cells | LOWCODE_CONFIRMED | E2E_PASSED (14/17 stages) | APPROVAL_BLOCKED |
| diagram | LOWCODE_CONFIRMED | E2E_PASSED (14/17 stages) | APPROVAL_BLOCKED |
| email | LOWCODE_CONFIRMED | E2E_PASSED (14/17 stages) | APPROVAL_BLOCKED |
| pdf | LOWCODE_CONFIRMED | E2E_FAILED_HEALED_AND_PASSED | APPROVAL_BLOCKED |
| slides | LOWCODE_CONFIRMED | E2E_PASSED (14/17 stages) | APPROVAL_BLOCKED |
| words | LOWCODE_CONFIRMED | E2E_FAILED_HEALED_AND_PASSED | APPROVAL_BLOCKED |

### No-LowCode (16)
All 16 products remain NO_LOWCODE_CONFIRMED. No change.

### External Blockers (3)
| Product | Blocker |
|---|---|
| ocr | Aspose.AI.LLM 25.12.0.0 not on NuGet |
| psd | Aspose.JavaAttributes not on NuGet |
| epub | Package Aspose.Epub does not exist |

## Machinery State

| Component | Prior State | Current State |
|---|---|---|
| DllReflector | BUILT | BUILT (rebuilt this sprint) |
| runner.py | BUG: missing include_all_tfm_groups | FIXED |
| words denominator | STALE_SOURCE_REFERENCE | UPDATED |
| pdf.yml | Missing include_all_tfm_groups | ADDED |

## Next Gate

The only remaining gates are:
1. `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` — to create live PRs
2. `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR` — to merge PRs

No more readiness loops. Machinery is qualified.
