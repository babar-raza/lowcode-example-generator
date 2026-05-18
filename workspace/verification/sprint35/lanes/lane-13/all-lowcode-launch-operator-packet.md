# All-LowCode Launch Operator Packet — Sprint 35

**Generated:** 2026-05-18
**Verdict:** PORTFOLIO_RELEASE_CANDIDATE_APPROVAL_BLOCKED
**Total Published:** 28 | **Pending Approval:** 14

## Portfolio Status

| Family | Status | Published | PR-Ready | Target Repo |
|--------|--------|-----------|----------|-------------|
| Cells | FAMILY_COMPLETE | 9/9 | 0 | aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples |
| Words | PILOT_COMPLETE | 8/8 | 0 | aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples |
| PDF | PARTIAL_CANARY | 5/19 | 14 | aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples |
| Diagram | PILOT_COMPLETE | 2/2 | 0 | aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples |
| Email | PILOT_COMPLETE | 1/1 | 0 | aspose-email-net/Aspose.Email.LowCode-for-.NET-Examples |
| Slides | PILOT_COMPLETE | 3/3 | 0 | aspose-slides-net/Aspose.Slides.LowCode-for-.NET-Examples |

## PDF Pending Packages (14 examples)
| PR | Package | Examples | Audit |
|----|---------|----------|-------|
| PR#3 | pdf-controlled-pilot | doc-converter, html, xls-converter | CLEAN, DRY_RUN_PASS |
| PR#5 | pdf-controlled-pilot-pr5 | jpeg, tiff, png | CLEAN, DRY_RUN_PASS |
| PR#6 | pdf-controlled-pilot-pr6 | image-extractor, table-generator, toc-generator | CLEAN, DRY_RUN_PASS |
| PR#7 | pdf-controlled-pilot-pr7 | security, form-flattener | CLEAN, DRY_RUN_PASS |
| PR#8 | pdf-controlled-pilot-pr8 | form-editor, form-exporter | CLEAN, DRY_RUN_PASS |
| PR#9 | pdf-controlled-pilot-pr9 | signature | CLEAN, DRY_RUN_PASS |

## Step 1: Map Classic PAT to GITHUB_TOKEN
```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
```

## Step 2: Publish All Pending PDF Packages
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr-batch \
  --family pdf \
  --publish \
  --approval-token APPROVE_LIVE_PR
```
OR set env var approach:
```bash
PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR \
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr-batch --family pdf --publish
```

## Step 3: Verify Created PRs
```bash
gh pr list --repo aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples
```

## Step 4: Merge PRs (after review)
```bash
PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR \
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family pdf \
  --approval-token APPROVE_MERGE_PR
```

## Step 5: Post-Publication Verification
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples post-publication-verify --family pdf
```

## Step 6: Update Release Status
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples release-status --promote-latest
```

## Expected Totals After Approval
- Published: 28 + 14 = **42 examples**
- PDF coverage: 19/19 pilot types = **100% of pilot scope**
- PDF workflow root coverage: 19/22 = **86.4%**

## Remaining Blockers After Approval
| Blocker | Status |
|---------|--------|
| FormImporter | WAVE_H_DEFERRED — library bug in Aspose.PDF 26.5.0 |
| Timestamp | PERMANENTLY_BLOCKED — external TSA required |
| Ofd | PERMANENTLY_BLOCKED — no OFD fixture possible |
| Words Processor | PERMANENTLY_BLOCKED — no public constructor |
| OCR reflection | BLOCKED — Aspose.AI.LLM not on NuGet |
| PSD reflection | BLOCKED — Aspose.JavaAttributes not on NuGet |

## Rollback Commands (if PR creation fails)
```bash
# Close any created PRs
gh pr close <PR_NUMBER> --repo aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples
```
