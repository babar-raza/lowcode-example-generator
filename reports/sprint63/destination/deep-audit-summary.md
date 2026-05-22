# Deep Destination Content Audit — Sprint 63 Phase 4

## Summary

| Metric | Count | Notes |
|--------|-------|-------|
| Total scenarios | 42 | 42 contracts across 6 families |
| Dry-run packages present | 37/42 | 5 missing: 2 PDF (pdfa, text-extractor) + 3 in pdf only partial packages |
| S62 content match | 40/42 | 2 NOT_IN_S62_AUDIT |
| Program.cs input verified | 37/42 | 37 match authority, 3 mismatch, 2 no authority data |
| README I/O corrections available | 40/42 | Sprint 62 generated; not applied (BLOCKED_BY_APPROVAL) |
| README I/O corrections applied | 0/42 | Pending APPROVE_README_PUSH gate |

## Package Versions

| Family | Version in Dry-Run | Latest NuGet | Status |
|--------|-------------------|-------------|--------|
| Cells | 26.5.1 | 26.5.1 | CURRENT |
| Diagram | 26.5.0 | 26.5.0 | CURRENT |
| Email | 26.4.0 | 26.4.0 | CURRENT |
| PDF | 26.4.0 | 26.5.0 | VERSION_DRIFT |
| Slides | 26.5.0 | 26.5.0 | CURRENT |
| Words | 26.5.0 | 26.5.0 | CURRENT |

## Content Match Analysis (from Sprint 62 audit)

- **40/42 MATCH** — content in destination repos matches generated examples
- **2 NOT_IN_AUDIT** — pdf-pdfa-converter, pdf-text-extractor (special cases; verified separately)

## Program.cs vs Authority

- **37/42 input format matches authority** — AddInput calls confirmed correct
- **3/42 mismatch** — requires investigation before next publication push
- **2/42 no authority data** — pdf-pdfa-converter, pdf-text-extractor

## README I/O Corrections

Sprint 62 generated 40/42 correction texts. 2 scenarios (pdf-pdfa-converter,
pdf-text-extractor) have special-case authoritative text.

Corrections NOT applied because approval gates are not set:
- `PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH`

## Audit Files

- `content-audit-deep.json` — 42 records with dry-run presence, versions, API classes
- `programcs-vs-authority-deep.json` — 42 records with input format vs authority comparison
- `readme-vs-authority-deep.json` — 42 records with correction availability status
