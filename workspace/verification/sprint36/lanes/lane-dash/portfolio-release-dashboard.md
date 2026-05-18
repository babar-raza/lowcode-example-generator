# Portfolio Release Dashboard — Sprint 36

**Generated:** 2026-05-18
**Verdict:** SPRINT36_APPROVAL_BLOCKED_PORTFOLIO_HARDENED_AND_OPERATOR_READY
**Test Suite:** 1789/1789 PASS *(reconciled — Sprint 35 dashboard showed stale 1744)*

---

## Portfolio Totals

| Metric | Value |
|--------|-------|
| Published Examples | **28** |
| PR-Ready (pending approval) | **14** |
| Total After Approval | **42** |
| Confirmed LowCode Families | **6** |

---

## Family Status

| Family | Status | Published | WRT | Drift | Target Repo |
|--------|--------|-----------|-----|-------|-------------|
| Cells | FAMILY_COMPLETE | 9/9 | 9 | 26.4.0->26.5.1 MINOR | aspose-cells-net |
| Words | PILOT_COMPLETE | 8/8 | 9 | NONE | aspose-words-net |
| PDF | PARTIAL_CANARY | 5+14 | 22 | NONE | aspose-pdf-net |
| Diagram | PILOT_COMPLETE | 2/2 | 2 | 26.4.0->26.5.0 MINOR | aspose-diagram-net |
| Email | PILOT_COMPLETE | 1/1 | 1 | NONE | aspose-email-net |
| Slides | PILOT_COMPLETE | 3/3 | 3 | NONE | aspose-slides-net |

---

## Blocked Families

| Family | Blocker | Escalation |
|--------|---------|------------|
| OCR | Aspose.AI.LLM not on NuGet | **ESCALATION_PACKAGE_READY** |
| PSD | Aspose.JavaAttributes not on NuGet | **ESCALATION_PACKAGE_READY** |
| EPUB | No standalone NuGet package | Confirmed |

---

## Publication Gate

- `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`: **NOT SET**
- `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL`: **NOT SET**
- `GH_TOKEN` (classic PAT): **SET**
- All 6 PDF packages: **CLEAN (0 bin/obj, SIMULATION_PASSED)**
- Security in PR#7: **CONFIRMED**

---

## New Commands (Sprint 36)

```bash
# Version drift check
python -m plugin_examples version-drift

# Target repo health
python -m plugin_examples target-repo-health
```

**Drift:** Cells 26.4.0->26.5.1 (MINOR), Diagram 26.4.0->26.5.0 (MINOR) — non-blocking
**Target repos:** ALL 6 HEALTHY via gh CLI
