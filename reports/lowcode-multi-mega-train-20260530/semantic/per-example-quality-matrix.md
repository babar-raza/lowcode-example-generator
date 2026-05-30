# Per-Example Quality Matrix — Multi-Mega-Train 20260530

Sprint: `lowcode-multi-mega-train-20260530`
Lane: B1 (No-op Detector)
Date: 2026-05-30
Total examples: 42

## Legend
- **CLEAN**: No no-op markers; real API called
- **REPAIRED**: Had no-op issue; template_first fix applied
- **REAL+COMMENT**: Real API called; stray comment present but not a blocker

## Quality Ratings (pre-repair)

| # | Family | Scenario ID | Type | Pre-Repair Status | Issue | Post-Repair |
|---|--------|-------------|------|-------------------|-------|-------------|
| 1 | cells | cells-image-converter | ImageConverter | CLEAN | — | CLEAN |
| 2 | cells | cells-json-layout-serializer | JsonLayoutSerializer | CLEAN | — | CLEAN |
| 3 | cells | cells-spreadsheet-locker | SpreadsheetLocker | CLEAN | — | CLEAN |
| 4 | cells | cells-spreadsheet-merger | SpreadsheetMerger | CLEAN | — | CLEAN |
| 5 | cells | cells-spreadsheet-splitter | SpreadsheetSplitter | CLEAN | — | CLEAN |
| 6 | cells | cells-spreadsheet-to-db | SpreadsheetToDb | CLEAN | — | CLEAN |
| 7 | cells | cells-spreadsheet-to-pdf-converter | SpreadsheetToPdfConverter | CLEAN | — | CLEAN |
| 8 | cells | cells-text-replacer | TextReplacer | CLEAN | — | CLEAN |
| 9 | cells | cells-watermarker | Watermarker | CLEAN | — | CLEAN |
| 10 | diagram | diagram-diagram-converter | DiagramConverter | CLEAN | — | CLEAN |
| 11 | diagram | diagram-pdf-converter | PdfConverter | CLEAN | — | CLEAN |
| 12 | email | email-email-converter | Converter | PURE_NO_OP | no suitable overload; prints Done. only | REPAIRED |
| 13 | pdf | pdf-doc-converter | DocConverter | CLEAN | template_first already set | CLEAN |
| 14 | pdf | pdf-form-editor | FormEditor | CLEAN | template_first already set | CLEAN |
| 15 | pdf | pdf-form-exporter | FormExporter | CLEAN | template_first already set | CLEAN |
| 16 | pdf | pdf-form-flattener | FormFlattener | CLEAN | template_first already set | CLEAN |
| 17 | pdf | pdf-html | Html | CLEAN | template_first already set | CLEAN |
| 18 | pdf | pdf-image-extractor | ImageExtractor | CLEAN | template_first already set | CLEAN |
| 19 | pdf | pdf-jpeg | Jpeg | CLEAN | template_first already set | CLEAN |
| 20 | pdf | pdf-pdf-aconverter | PdfAConverter | PURE_NO_OP | no suitable overload; prints Done. only | REPAIRED |
| 21 | pdf | pdf-pdf-merger | Merger | PURE_NO_OP | no suitable overload; prints Done. only | REPAIRED |
| 22 | pdf | pdf-pdf-optimizer | Optimizer | PURE_NO_OP | no suitable overload; prints Done. only | REPAIRED |
| 23 | pdf | pdf-pdf-splitter | Splitter | PURE_NO_OP | no suitable overload; prints Done. only | REPAIRED |
| 24 | pdf | pdf-png | Png | CLEAN | template_first already set | CLEAN |
| 25 | pdf | pdf-security | Security | CLEAN | template_first already set | CLEAN |
| 26 | pdf | pdf-signature | Signature | CLEAN | template_first already set | CLEAN |
| 27 | pdf | pdf-table-generator | TableGenerator | CLEAN | template_first already set | CLEAN |
| 28 | pdf | pdf-text-extractor | TextExtractor | PURE_NO_OP | no suitable overload; prints Done. only | REPAIRED |
| 29 | pdf | pdf-tiff | Tiff | CLEAN | template_first already set | CLEAN |
| 30 | pdf | pdf-toc-generator | TocGenerator | CLEAN | template_first already set | CLEAN |
| 31 | pdf | pdf-xls-converter | XlsConverter | CLEAN | template_first already set | CLEAN |
| 32 | slides | slides-slides-compress | Compress | PURE_NO_OP | no suitable overload; prints Done. only | REPAIRED |
| 33 | slides | slides-slides-convert | Convert | CLEAN | template_first already set | CLEAN |
| 34 | slides | slides-slides-merger | Merger | CLEAN | — | CLEAN |
| 35 | words | words-words-comparer | Comparer | PARTIAL_STUB | Comparer.Create() only; no Compare() | REPAIRED |
| 36 | words | words-words-converter | Converter | REAL+COMMENT | real Converter.Convert(); stray comment | NO CHANGE |
| 37 | words | words-words-mail-merger | MailMerger | PARTIAL_STUB | no API call; all overloads 'no suitable' | REPAIRED |
| 38 | words | words-words-merger | Merger | CLEAN | template_first already set | CLEAN |
| 39 | words | words-words-replacer | Replacer | REAL+COMMENT | real Replacer.Replace(); stray comment | NO CHANGE |
| 40 | words | words-words-report-builder | ReportBuilder | PARTIAL_STUB | ReportBuilder.Create() only; no BuildReport() | REPAIRED |
| 41 | words | words-words-splitter | Splitter | REAL+COMMENT | real Splitter.RemoveBlankPages(); stray comment | NO CHANGE |
| 42 | words | words-words-watermarker | Watermarker | CLEAN | template_first already set | CLEAN |

## Summary

| Status | Count |
|--------|-------|
| CLEAN (no issue) | 30 |
| PURE_NO_OP → REPAIRED | 6 |
| PARTIAL_STUB → REPAIRED | 3 |
| REAL+COMMENT (no change needed) | 3 |
| **Total** | **42** |

## Repair Approach

All 9 repaired examples use `template_first: true` in the family YAML `per_type_constraints` section, which causes the generator to use `_generate_deterministic_template_for_scenario()` in `src/plugin_examples/generator/code_generator.py` instead of LLM generation.

New deterministic templates added:
- **pdf**: merger, optimizer, splitter, pdfahconverter, textextractor (Process pattern with MergeOptions/OptimizeOptions/SplitOptions/PdfAConvertOptions/TextExtractorOptions)
- **slides**: compress (Compress.RemoveUnusedLayoutSlides(pres) static method, loads+saves Presentation)
- **email**: converter (async Converter.ConvertToHtml with MemoryStream + FolderOutputHandler)
- **words**: comparer (Comparer.Compare static), mailmerger (MailMerger.Execute static), reportbuilder (ReportBuilder.BuildReport with public ReportData class)

YAML files modified:
- `pipeline/configs/families/pdf.yml`: Merger, TextExtractor, Splitter, Optimizer, PdfAConverter → `template_first: true`
- `pipeline/configs/families/slides.yml`: Compress → `template_first: true`
- `pipeline/configs/families/email.yml`: Converter → `template_first: true`
- `pipeline/configs/families/words.yml`: Comparer, MailMerger, ReportBuilder → `template_first: true`
