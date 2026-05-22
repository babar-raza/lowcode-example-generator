# Sprint 41 — Taskcard State Machine

## Active Taskcards

| ID | Description | State | Assignee | Evidence |
|----|-------------|-------|----------|----------|
| TC-S41-HEAD-MISMATCH | Resolve Sprint 40 HEAD mismatch (0a4e695 vs 1add673) | CLOSED_VERIFIED | Lane 0 | head-mismatch-report.md |
| TC-S41-EVIDENCE-REPAIR | Repair Sprint 40 thin evidence trail | CLOSED_VERIFIED | Lane A | evidence-repair-report.md |
| TC-S41-PDF-CONTRACT-IV | Deep-verify all 19 PDF contracts | CLOSED_VERIFIED | Lane A | pdf-contract-iv-report.md |
| TC-S41-PDF-PR-MERGE | Merge PDF PRs #5-#10 under approval gate | BLOCKED | Lane B | pdf-pr-merge-preflight.md |
| TC-S41-PDF-POST-MERGE | Reconcile PDF state after merge | BLOCKED | Lane C | Depends on TC-S41-PDF-PR-MERGE |
| TC-S41-FORMAT-COMMIT | Commit format-capability display refinements | CLOSED_VERIFIED | Lane F | format-capability-decision.md |
| TC-S41-DIRTY-STATE | Classify all dirty/untracked files | CLOSED_VERIFIED | Lane 0 | dirty-state-classification.md |
| TC-S41-CONSERVATION | Verify conservation equations for all families | CLOSED_VERIFIED | Lane E | conservation-check-report.md |
| TC-S41-PORTFOLIO | Build whole-portfolio matrix with all families | CLOSED_VERIFIED | Lane E | portfolio-family-plugin-matrix.md |
| TC-S41-PDF-EXPANSION | Identify PDF workflow root gaps and next candidates | CLOSED_VERIFIED | Lane D | pdf-next-expansion-report.md |

## Inherited Taskcards (from Previous Sprints)

| ID | Description | State | Since |
|----|-------------|-------|-------|
| TC-PDF-FORMIMPORTER-RETEST | Retest FormImporter when Aspose.PDF > 26.5.0 | BLOCKED | Sprint 15 |
| TC-PDF-TIMESTAMP-PERMANENTLY-BLOCKED | Timestamp requires external TSA | PERMANENTLY_BLOCKED | Sprint 4 |
| TC-PDF-OFD-PERMANENTLY-BLOCKED | Ofd requires OFD input format | PERMANENTLY_BLOCKED | Sprint 4 |
| TC-WORDS-PROCESSOR-API-INVESTIGATION | Processor has no public constructor | PERMANENTLY_BLOCKED | Sprint 13 |
| TC-OCR-DEPENDENCY-BLOCKED | Aspose.AI.LLM NuGet 404 | BLOCKED | Sprint 10 |
| TC-PSD-DEPENDENCY-BLOCKED | Aspose.JavaAttributes NuGet 404 | BLOCKED | Sprint 10 |
| TC-EMAIL-SLIDES-CONTRACT-BACKFILL | Create retroactive pipeline contracts | PROPOSED | Sprint 41 |
