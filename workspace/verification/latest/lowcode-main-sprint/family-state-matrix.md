# Family State Matrix — Sprint 38

| Family | Package | Status | LowCode Types | Workflow Roots | Allowed Pilot | Published | PR Dry-Run | Excluded | Blockers | Target Repo | Release Status | Evidence | Action |
|--------|---------|--------|--------------|----------------|---------------|-----------|------------|----------|----------|-------------|----------------|----------|--------|
| cells | Aspose.Cells 26.4.0 | FAMILY_COMPLETE | 22 | 9 | 9 (FULL_SOT) | 9 | 0 | 13 | None | aspose-cells-net (e43c921) | FAMILY_COMPLETE | VERIFIED | Update denominator 26.4.0->26.5.1 (drift pilot PASS) |
| words | Aspose.Words 26.5.0 | PILOT_COMPLETE | 25 | 9 | 8 | 8 | 0 | 17 | Processor PERMANENTLY_BLOCKED | aspose-words-net (1b9f4e7) | PILOT_COMPLETE | VERIFIED | Monitor; Processor needs package upgrade |
| pdf | Aspose.PDF 26.5.0 | PARTIAL_CANARY | 101 | 22 | 19 | 5 | 14 | 82 | FormImporter WAVE_H, Timestamp/Ofd PERM_BLOCKED | aspose-pdf-net (e49ea8a) | PARTIAL_CANARY | VERIFIED | Merge PRs #5-#10 when approved |
| diagram | Aspose.Diagram 26.4.0 | PILOT_COMPLETE | 5 | 2 | 2 | 2 | 0 | 3 | None | aspose-diagram-net (469c50d) | PILOT_COMPLETE | VERIFIED | Update denominator 26.4.0->26.5.0 (drift pilot PASS) |
| email | Aspose.Email 26.4.0 | PILOT_COMPLETE | 3 | 1 | 1 | 1 | 0 | 2 | None | aspose-email-net (6d10c59) | PILOT_COMPLETE | VERIFIED | Monitor for drift |
| slides | Aspose.Slides.NET 26.5.0 | PILOT_COMPLETE | 5 | 3 | 3 | 3 | 0 | 2 | None | aspose-slides-net (bbe7e68) | PILOT_COMPLETE | VERIFIED | Monitor for drift |
| ocr | Aspose.OCR | DISCOVERY_ONLY | - | - | - | 0 | 0 | - | Aspose.AI.LLM missing from NuGet | N/A | BLOCKED | NOT_STARTED | Escalation ready |
| psd | Aspose.PSD | DISCOVERY_ONLY | - | - | - | 0 | 0 | - | Aspose.JavaAttributes missing | N/A | BLOCKED | NOT_STARTED | Escalation ready |

## Denominator Fixes Applied in Sprint 38

1. **Email**: Fixed stale discovery-only metadata. Updated allowed_pilot_types=["Converter"], runnable_scenarios=1, runnable_scenario_ids=["email-converter"], coverage_pct_of_workflow_root=100%, excluded_count=2.
2. **Slides**: Fixed stale discovery-only metadata. Updated allowed_pilot_types=["Compress","Convert","Merger"], runnable_scenarios=3, runnable_scenario_ids, coverage_pct_of_workflow_root=100%, excluded_count=2.
3. **Words**: Added missing "words-report-builder" to runnable_scenario_ids (was 7 entries, should be 8 to match runnable_scenarios=8 and allowed_pilot_count=8).
4. **PDF**: Corrected coverage_pct_of_pilot_allowed from 27.78% (5/18) to 26.32% (5/19). Updated pr_dry_run_ready_count from 9 to 14 to include PR#7-PR#10 examples.

## Totals

- **Published:** 28 (9+8+5+2+1+3)
- **PR dry-run ready:** 14 (all PDF)
- **Total ready or published:** 42
- **Blocked families:** 2 (OCR, PSD — dependency blockers)
- **Target repos verified:** 6/6
