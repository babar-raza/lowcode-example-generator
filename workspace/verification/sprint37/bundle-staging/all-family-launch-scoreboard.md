# All-Family LowCode Launch Scoreboard — Sprint 35

**Generated:** 2026-05-18
**Verdict:** PORTFOLIO_RELEASE_CANDIDATE_APPROVAL_BLOCKED

## Portfolio Totals
| Metric | Value |
|--------|-------|
| Published Examples | **28** |
| PR-Ready (pending approval) | **14** |
| Total After Approval | **42** |
| Confirmed LowCode Families | **6** |
| Families PILOT_COMPLETE or higher | **5** |

## Family Status
| Family | Namespace | Status | Published | Workflow Roots | Coverage | Target Repo |
|--------|-----------|--------|-----------|----------------|----------|-------------|
| Cells | Aspose.Cells.LowCode | FAMILY_COMPLETE | 9 | 9 | 100% | aspose-cells-net |
| Words | Aspose.Words.LowCode | PILOT_COMPLETE | 8 | 9 | 88.9% WRT | aspose-words-net |
| PDF | Aspose.Pdf.LowCode | PARTIAL_CANARY | 5+14 ready | 22 | 86.4% after PRs | aspose-pdf-net |
| Diagram | Aspose.Diagram.LowCode | PILOT_COMPLETE | 2 | 2 | 100% | aspose-diagram-net |
| Email | Aspose.Email.LowCode | PILOT_COMPLETE | 1 | 1 | 100% | aspose-email-net |
| Slides | Aspose.Slides.LowCode | PILOT_COMPLETE | 3 | 3 | 100% | aspose-slides-net |

## Blocked Families
| Family | Blocker |
|--------|---------|
| OCR | Aspose.AI.LLM private assembly not on NuGet |
| PSD | Aspose.JavaAttributes private assembly not on NuGet |
| EPUB | No standalone NuGet package |

## Families Confirmed No LowCode (16)
barcode, cad, drawing, finance, font, gis, imaging, note, page, tasks, tex, threed, zip, html, svg, omr

## Next Action
Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` and run:
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr-batch --family pdf --publish --approval-token APPROVE_LIVE_PR
```
