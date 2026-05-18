# All LowCode Launch Operator Packet v3

**Sprint:** sprint36
**Date:** 2026-05-18
**Version:** v3

---

## Required Approval Gates

```bash
export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
export PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
export GITHUB_TOKEN=$GH_TOKEN   # map classic PAT
```

---

## Publish All 6 PDF Packages (one command)

```bash
PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR \
  PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr-batch \
  --family pdf --publish --approval-token APPROVE_LIVE_PR
```

---

## Per-Package Publish Commands

```bash
# PR#3: DocConverter, Html, XlsConverter
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf \
  --package-path workspace/pr-dry-run/pdf-controlled-pilot --publish --approval-token APPROVE_LIVE_PR

# PR#5: Jpeg, Png, Tiff
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf \
  --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr5 --publish --approval-token APPROVE_LIVE_PR

# PR#6: ImageExtractor, TableGenerator, TocGenerator
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf \
  --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr6 --publish --approval-token APPROVE_LIVE_PR

# PR#7: Security, FormFlattener [SECURITY PRESENT - VERIFIED]
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf \
  --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr7 --publish --approval-token APPROVE_LIVE_PR

# PR#8: FormEditor, FormExporter
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf \
  --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr8 --publish --approval-token APPROVE_LIVE_PR

# PR#9: Signature [/ByteRange verified]
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr --family pdf \
  --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr9 --publish --approval-token APPROVE_LIVE_PR
```

---

## Merge PRs (after publication)

```bash
PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR \
  PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family pdf --pr-number <N> --approval-token APPROVE_MERGE_PR
```

---

## Post-Merge Verification

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples post-publication-verify --family pdf
```

---

## Version Drift Check

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples version-drift
```

**Current drift (Sprint 36):**
- Cells: 26.4.0 -> 26.5.1 (MAJOR — non-blocking)
- Diagram: 26.4.0 -> 26.5.0 (MAJOR — non-blocking)

---

## Target Repo Health Check

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples target-repo-health
```

---

## Family Status

| Family | Status | Published | Target Repo |
|--------|--------|-----------|-------------|
| Cells | FAMILY_COMPLETE | 9/9 | aspose-cells-net |
| Words | PILOT_COMPLETE | 8/8 | aspose-words-net |
| PDF | PARTIAL_CANARY | 5+14 pending | aspose-pdf-net |
| Diagram | PILOT_COMPLETE | 2/2 | aspose-diagram-net |
| Email | PILOT_COMPLETE | 1/1 | aspose-email-net |
| Slides | PILOT_COMPLETE | 3/3 | aspose-slides-net |

---

## Rollback / Close PR

```bash
gh pr close <PR_URL>
gh api repos/OWNER/REPO/git/refs/heads/BRANCH -X DELETE
```

---

## Expected Counts After Approval

- PDF after publish: 5 + 14 = 19 examples
- Total portfolio: 28 + 14 = 42 examples
