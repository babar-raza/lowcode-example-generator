# LowCode Example Generator: All-Family Current State Board

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Status:** BOARD_CURRENT

---

## Quick Status Board

| Family | Status | Published | PR-Ready | Reviewed | Blocked | Deferred | Notes |
|--------|--------|-----------|----------|----------|---------|----------|-------|
| cells | COMPLETE | 9/9 | 0 | 0 | 0 | 0 | 100% FULL_SOT |
| words | PILOT_COMPLETE | 4/25 | 0 | 0 | 0 | 21 | workflow_root_types=NULL |
| pdf | IN_PROGRESS | 2/4 pilot | 1 | 1 | 0 | 97 | PR#3 ready; Optimizer needs 2nd PASS |
| email | DISCOVERY_BLOCKED | 0 | 0 | 0 | 0 | ? | Config in disabled/; reflection unproven |
| slides | DISCOVERY_BLOCKED | 0 | 0 | 0 | 0 | ? | DLL name mismatch |
| 20 others | DISCOVERY_NOT_ATTEMPTED | 0 | 0 | 0 | 0 | ? | No YAML config |

---

## Cells (COMPLETE)

- **Published:** HtmlConverter, ImageConverter, JsonConverter, PdfConverter, SpreadsheetConverter, SpreadsheetLocker, SpreadsheetMerger, SpreadsheetSplitter, TextConverter
- **Merge SHA:** f6e5515c070184e4b08a2cff647220bea1113b08 (2026-05-03)
- **README PRs:** PR#2 (backfill, SHA 55b4f190), PR#3 (aspose.net links, SHA 56601118), PR#4 (README API, SHA 6222d610)
- **Denominator:** FULL_SOT, 9+13=22, equation HOLDS
- **Next action:** R7 reconciliation (verify release-status includes PDF)

## Words (PILOT_COMPLETE)

- **Published (pilot 4):** Converter, Watermarker, Splitter, Replacer
- **Merge SHA:** b66fb43023d4d1af7162270ac9d3ef3ef881451f (2026-05-03)
- **Deferred 21:** Comparer (pair fixture), Merger (pair fixture), MailMerger (template fixture), SplitCriteria (enum strategy), ~17 others (classification gap or pilot scope)
- **Denominator:** PILOT_ALLOWED, 4+21=25, workflow_root_types=NULL
- **Next actions:** R7 (workflow_root classification), R9 (expansion)
- **Open taskcards:** followup-words-split-criteria-enumeration, followup-words-pair-fixture-strategy, followup-words-mail-merger-fixture-documentation, followup-words-docx-semantic-validation, followup-words-full-coverage-expansion, NEW-07

## PDF (IN_PROGRESS)

- **Published:** Merger (PR#1, 2026-05-06), TextExtractor (PR#1, 2026-05-06)
- **PR#3 ready (Splitter):** Package at workspace/pr-dry-run/pdf-controlled-pilot-wave1/
- **Optimizer:** 1st PASS achieved (pilot-pdf-20260508-155520); needs 2nd consecutive PASS for PR#4
- **PR blockers:** APPROVE_LIVE_PR not set; GITHUB_TOKEN write scope unverified
- **21 deferred WORKFLOW_ROOT types:** DocConverter, FormEditor, FormExporter, FormFlattener, FormImporter, Html, ImageExtractor, Jpeg, Ofd, + 12 others
- **76 non-runnable types:** OPTIONS (51), PROVIDER_CALLBACK (5), RESULT (6), DATA_SOURCE (3), SAVE_TARGET (2), BUILDER (4), ENUM (4)
- **Denominator:** PILOT_ALLOWED, 2+1+1+0+21+76=101, equation HOLDS
- **Open taskcards:** followup-pdf-pr3-review-and-merge (HIGH), followup-pdf-remaining-candidate-classification
- **Next actions:** R8 (PR#3 live), R10 (expansion)

## Email (DISCOVERY_BLOCKED)

- **Config:** pipeline/configs/families/disabled/email.yml
- **Contradiction C4:** enabled=true but not in active scan path
- **LowCode namespace:** CLAIMED (Aspose.Email.LowCode), not reflection-proven
- **Prior runs:** 2 template-mode examples 2026-04-29 (not production artifacts; used wrong strategy)
- **Next actions:** R2 (investigation), move config or document CONFIRMED_NO_LOWCODE

## Slides (DISCOVERY_BLOCKED)

- **Config:** pipeline/configs/families/disabled/slides.yml
- **Contradiction C5:** enabled=true but not in active scan path
- **Blocker:** DLL name mismatch - Aspose.Slides.NET package → Aspose.Slides.dll (not .NET suffix)
- **Prior runs:** FAIL_PACKAGE_UNSUPPORTED_TFM 2026-04-29
- **Next actions:** R2 (DLL fix), discovery attempt

## Group C Families (DISCOVERY_NOT_ATTEMPTED)

20 candidate families with no YAML config. Cannot discover or generate until R1.

- **Priority MEDIUM:** imaging, barcode, diagram, cad
- **Priority LOW:** ocr, omr, tasks, note, zip, page, psd, html, gis, finance, threed, tex, font, drawing, svg, epub

---

## Current Pipeline Health

| Gate | Status |
|------|--------|
| Unit tests | 1168 passing |
| Denominator schema validation | PASS (cells, words, pdf) |
| Completion queue (17 entries) | PASS |
| Evidence completeness gate | WARNING mode (non-blocking) |
| Code generator FORBIDDEN constraints | ACTIVE (pdf types) |
| Live publish approval gate | NOT SET (phase I blocked) |

---

## Environment Availability

| Capability | Available | Notes |
|-----------|-----------|-------|
| LLM generation | YES (GPT_OSS_ENDPOINT + API_KEY set) | GPT_OSS_MODEL not set; uses default |
| Discovery (NuGet reflection) | YES | .NET 9.0.200 available |
| Live PR creation | NO | APPROVE_LIVE_PR not set |
| Live merge | NO | APPROVE_MERGE_PR not set |
| Reviewer gate | NO | EXAMPLE_REVIEWER_PATH not set |
| GitHub API (read) | YES | GITHUB_TOKEN set |
| GitHub API (write) | UNVERIFIED | GITHUB_TOKEN set but write scope unknown |
