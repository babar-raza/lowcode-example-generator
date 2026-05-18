# Next Family Launch Candidate Plan (Sprint 33)

## Status: ALL 6 ACTIVE FAMILIES AT PILOT_COMPLETE OR HIGHER

No new families are ready for activation. All 6 active families have completed their controlled pilots.

## Current Family Status Matrix

| Family | Status | Published | Notes |
|--------|--------|-----------|-------|
| Cells | FAMILY_COMPLETE | 9/9 | All runnable types published |
| Words | PILOT_COMPLETE | 8/9 | Processor permanently blocked |
| Diagram | PILOT_COMPLETE | 2/2 | All runnable types published |
| Email | PILOT_COMPLETE | 1/1 | All runnable types published |
| Slides | PILOT_COMPLETE | 3/3 | All runnable types published |
| PDF | PARTIAL_CANARY | 5 published + 14 PR-ready | Approval-blocked |

## Families Potentially Activatable (Discovery-Only)

### epub (Reflection-Blocked)
- **Blocker**: Aspose.Epub package download has been failing
- **Resolution**: Retry NuGet restore; if successful, run DllReflector scan for LowCode namespace
- **Likelihood of LowCode namespace**: UNKNOWN

### ocr (Reflection-Blocked)
- **Blocker**: Aspose.Drawing.Common dependency missing
- **Resolution**: Add to resolved-libs list in ocr.yml before next scan
- **Likelihood of LowCode namespace**: UNKNOWN

### psd (Reflection-Blocked)
- **Blocker**: Newtonsoft.Json dependency missing
- **Resolution**: Add to resolved-libs list in psd.yml before next scan
- **Likelihood of LowCode namespace**: UNKNOWN

## Prioritization

1. **Priority 1**: Publish 14 PDF examples (TC-PUBLICATION-01) — 42 total examples
2. **Priority 2**: Words full SOT (TC-WORDS-01) — already complete as of Sprint 33
3. **Priority 3**: Resolve epub/ocr/psd reflection blockers — unblock future family discovery
4. **Priority 4**: FormImporter retest when Aspose.PDF > 26.5.0 (TC-PDF-FORMIMPORTER-RETEST)

## Verdict

`NO_NEW_FAMILY_ACTIVATION_NEEDED_THIS_SPRINT` — portfolio is at 28 published examples with 14 pending approval.
