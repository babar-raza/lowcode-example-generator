# Sprint 62 Baseline State

**Sprint:** 62
**Based on:** Sprint 61 commit eba2128
**Date:** 2026-05-21

---

## What Sprint 61 Delivered (Accepted)

| Item | State |
|------|-------|
| EvidenceValidator: 20 rules | Accepted |
| Sprint 60 bundle confirmed INVALID (7/20 FAIL) | Accepted |
| README gate wired into publish-pr --publish | Accepted |
| EvidenceValidator wired into release-status --validate-bundle | Accepted |
| 2945/2945 tests passing, 0 failed | Accepted |
| Final clean proof nonzero, "nothing to commit" | Accepted |
| README I/O audit separated from shallow presence checks | Accepted |
| Program.cs I/O improved from 0/42 to 37/42 BOTH_KNOWN | Accepted (with correction below) |
| Package authority 41/42 dual-source, 1/42 contract-only | Accepted (with correction below) |

## What Sprint 61 Did NOT Deliver

| Item | State |
|------|-------|
| README I/O push to destination repos | Not done — deferred |
| Special cases (4 README + 5 Program.cs) fully resolved | Not done — misclassified |
| Sprint 61 bundle validation result JSON | Absent |
| README gate approval semantics hardened | Not done — bypass too loose |
| EvidenceValidator integration made mandatory | Not done — optional flag only |
| Words/Diagram version drift in destination repos | Not done |
| pdf-pdf-aconverter Program.cs correctly found | Not done — misclassified as no local package |

## Sprint 62 Opening Corrections

### Program.cs Special Cases (corrected from Sprint 61)

| Scenario | Sprint 61 Classification | Correct Classification |
|----------|-------------------------|----------------------|
| pdf-pdf-aconverter | None (no local package) | Input: .pdf → Output: .pdf (PdfAConverter, Program.cs in workspace/runs/) |
| pdf-text-extractor | None (no local package) | Input: .pdf → Output: StringResult text to stdout |
| words-mail-merger | Input: None | Input: .docx template (code-generated) + in-memory merge data → Output: .docx |
| words-report-builder | Input: None | Input: .docx template (code-generated) + in-memory report data → Output: .docx |
| email-converter | INPUT_KNOWN_OUTPUT_SPECIAL | Input: .eml → Output: directory of .html files (confirmed) |

### Publication Status (unchanged from Sprint 61)

| Family | Status | Local Version | Published Version |
|--------|--------|--------------|-------------------|
| cells | PUBLISHED_CURRENT | 26.5.1 | 26.5.1 |
| words | VERSION_DRIFT | 26.5.0 | 26.4.0 |
| pdf | PUBLISHED_CURRENT | 26.5.0 | 26.5.0 |
| diagram | VERSION_DRIFT | 26.5.0 | 26.4.0 |
| email | PUBLISHED_CURRENT | 26.4.0 | 26.4.0 |
| slides | PUBLISHED_CURRENT | 26.5.0 | 26.5.0 |

Note: Local dry-run Directory.Packages.props already has 26.5.0 for both words and diagram.

---

## Sprint 62 Scope

Sprint 62 closes:
1. All 4 README I/O special cases
2. All 5 Program.cs I/O special/partial cases
3. 42/42 README correction packages
4. 6/6 destination dry-run update packages
5. Words/Diagram version drift (dry-run)
6. README gate approval semantics (hardened)
7. Mandatory EvidenceValidator integration
8. Package authority API backfill (partial)
9. Live publication (if approved)
10. Sprint 62 evidence bundle with validation result
