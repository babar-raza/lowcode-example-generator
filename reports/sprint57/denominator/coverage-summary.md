# Coverage Summary — Sprint 57

**True Denominator:** 42 planned runnable examples across 6 families
**100% Target:** 42/42
**90% Threshold:** 38/42

## Family Coverage

| Family | Active Types | Destination State | Coverage |
|--------|-------------|------------------|----------|
| Cells | 9 | All POST_MERGE_VERIFIED (PR#1, PR#6) | 9/9 = 100% |
| Words | 8 | All POST_MERGE_VERIFIED (PR#1, PR#5) | 8/8 = 100% |
| PDF | 19 | 5 POST_MERGE_VERIFIED (PR#1,#2,#4) + 14 MERGED (PR#11,#17-#21) | 19/19 = 100% |
| Diagram | 2 | All POST_MERGE_VERIFIED | 2/2 = 100% |
| Email | 1 | All POST_MERGE_VERIFIED | 1/1 = 100% |
| Slides | 3 | All POST_MERGE_VERIFIED | 3/3 = 100% |
| **Total** | **42** | 28 POST_MERGE_VERIFIED + 14 MERGED | **42/42 = 100%** |

## Denominator Notes

- The old denominator of 42 is confirmed correct.
- OCR and PSD are NOT in denominator (reflection blocked; LowCode namespace existence unknown).
- If OCR/PSD gain LowCode namespaces, denominator would increase. Retest monthly.
- 17 families are CONFIRMED_NO_LOWCODE and permanently excluded from denominator.

## Publication Coverage

Examples that have been published (PR merged to destination repo):
- Cells: 9/9 (all merged)
- Words: 8/8 (all merged)
- PDF: 19/19 (all merged, 14 pending content verification)
- Diagram: 2/2 (all merged)
- Email: 1/1 (merged)
- Slides: 3/3 (all merged)
- **Total published: 42/42 = 100%**

## Generation Coverage (Sprint 57 From-Scratch Runs)

Background tasks started for all 6 families. Results pending.
Expected: 42/42 pass (same as Sprint 56 post-fix runs confirmed).
