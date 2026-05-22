# Root README Cardinality Fix Proof — Sprint 67

Date: 2026-05-22
Sprint: sprint67-final-pre-publication-repair-legacy-plan-reconciliation-readme-io-live-pr-readiness

## Defect Closed

**S66-D1**: Root README tables showed `xlsx → xlsx` for merger and splitter types without
cardinality annotations. Users could not distinguish N→1 mergers from 1→N splitters.

## Fix Applied

Script: `scripts/build_sprint67_root_readmes.py`
Source: `reports/sprint66/root-readme/per-family/` (Sprint 66 versions)
Output: `reports/sprint67/root-readme/per-family/` (Sprint 67 versions)
Total rows patched: 7

### Annotation Format

- **N→1 operations** (merger, comparer): Input column uses `×N` suffix — e.g., `xlsx (×N)`
- **1→N operations** (splitter, extractor, jpeg/png converters): Output column uses `×N` suffix — e.g., `xlsx (×N)`
- **Exactly 2 inputs** (Comparer): Input column uses `2×` prefix — e.g., `2× docx`
- **Directory output** (email Converter): Output column uses `html dir`

A cardinality key legend is inserted below each patched table:
> **Cardinality key:** `×N` in the Input column means the operation merges N input files into one.
> `×N` in the Output column means the operation splits or extracts into N output files.
> `2×` prefix means exactly two inputs are required.

## Per-Family Results

| Family | Changes | Rows Patched | Status |
|--------|---------|-------------|--------|
| cells | spreadsheet-merger (N→1), spreadsheet-splitter (1→N) | 2 | FIXED |
| words | comparer (2→1), merger (N→1), splitter (1→N) | 3 | FIXED |
| pdf | merger, splitter, jpeg, png, image-extractor (table truncation issue) | 0 patched (table truncated — Sprint 66 PDF README only shows 3/19 examples) | PARTIAL — TABLE_TRUNCATION_KNOWN_ISSUE |
| diagram | no multi-cardinality types | 0 | NO_CHANGE_NEEDED |
| email | converter (1→html dir) | 1 | FIXED |
| slides | merger (N→1) | 1 | FIXED |

## PDF Table Truncation Known Issue

Sprint 66 PDF root README only shows 3 of 19 examples in the Included Examples table
(doc-converter, html, xls-converter). The 16 remaining examples (including merger, splitter,
jpeg, png, image-extractor) are missing from the table.

This is a separate issue from S66-D1 cardinality. Rebuilding the full PDF table requires
reading all 19 handoff packages to extract the correct API/format data.

**Sprint 67 decision**: PDF table truncation is a KNOWN ISSUE documented in cardinality-audit.json.
The sprint67 PDF root README inherits the Sprint 66 table (3/19 rows) with no cardinality changes
applied (since the multi-cardinality examples aren't in the table). Full PDF table rebuild is a
follow-up task for Sprint 68.

## Format Authority Contract Alignment

All cardinality annotations are derived from `pipeline/format-authority/contracts/*.json`:

| Type | Contract input_cardinality | Contract output_cardinality | Sprint 67 Display |
|------|--------------------------|---------------------------|-------------------|
| cells/SpreadsheetMerger | multi | single | xlsx (×N) → xlsx |
| cells/SpreadsheetSplitter | single | multi | xlsx → xlsx (×N) |
| words/Comparer | multi | single | 2× docx → docx |
| words/Merger | multi | single | docx (×N) → docx |
| words/Splitter | single | multi | docx → docx (×N) |
| email/Converter | single | multi | eml → html dir |
| slides/Merger | multi | single | pptx (×N) → pptx |

## Verdict

S66-D1 CLOSED for cells, words, email, slides families.
PDF cardinality fix DEFERRED (table truncation requires full rebuild).
