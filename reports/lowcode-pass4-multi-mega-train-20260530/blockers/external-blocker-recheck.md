# External Blocker Recheck — Fresh Raw Commands

Sprint: lowcode-pass4-multi-mega-train-20260530
Date: 2026-05-30

## epub: EXTERNAL_PACKAGE_BLOCKER

**Command:** `dotnet restore` with Aspose.Epub package reference

**Result:** NU1101 — Unable to find package Aspose.Epub

**Detail:** Aspose.Epub does not have a standalone NuGet package. EPUB conversion is covered by
Aspose.Words (words family, already included). Status: EXTERNAL_PACKAGE_BLOCKER.

**Prior classification:** EXTERNAL_PACKAGE_BLOCKER (unchanged from Sprint 34, 2026-05-18)

---

## ocr: NO_LOWCODE_CONFIRMED (reclassified from EXTERNAL_PACKAGE_BLOCKER)

**Command:** Loaded Aspose.OCR.dll via Assembly.LoadFrom() in a .NET 8 reflection program

**NuGet:** Aspose.OCR 26.5.0 — restores successfully

**Result:**
- Total types loaded: 1,257
- Types with LowCode in namespace: **0**
- LowCode namespace: **NOT PRESENT**

**Detail:** Prior runs were blocked by Aspose.AI.LLM dependency not being on NuGet. Fresh check
using direct DLL reflection with Aspose.OCR 26.5.0 confirmed zero LowCode types.

**Verdict:** NO_LOWCODE_CONFIRMED — OCR has no LowCode API. Not in scope for LowCode examples.

---

## psd: NO_LOWCODE_CONFIRMED (reclassified from EXTERNAL_PACKAGE_BLOCKER)

**Command:** Loaded Aspose.PSD.dll via Assembly.LoadFrom() in a .NET 8 reflection program

**NuGet:** Aspose.PSD 26.5.0 — restores successfully

**Result:**
- Total types loaded: 4,432
- Types with LowCode in namespace: **0**
- LowCode namespace: **NOT PRESENT**

**Detail:** Prior runs were blocked by Aspose.JavaAttributes dependency not being on NuGet. Fresh
check using direct DLL reflection with Aspose.PSD 26.5.0 confirmed zero LowCode types.

**Verdict:** NO_LOWCODE_CONFIRMED — PSD has no LowCode API. Not in scope for LowCode examples.

---

## Summary

| Product | Prior Status | Current Status | Change |
|---------|-------------|----------------|--------|
| epub    | EXTERNAL_PACKAGE_BLOCKER | EXTERNAL_PACKAGE_BLOCKER | No change |
| ocr     | EXTERNAL_PACKAGE_BLOCKER | NO_LOWCODE_CONFIRMED | RECLASSIFIED |
| psd     | EXTERNAL_PACKAGE_BLOCKER | NO_LOWCODE_CONFIRMED | RECLASSIFIED |

**Impact on example count:** None. OCR and PSD have no LowCode API to generate examples for.
The 42-example universe is unchanged.
