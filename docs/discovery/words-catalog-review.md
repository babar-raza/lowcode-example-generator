# Words Readiness Review

**Date:** 2026-04-30
**Sprint:** Words Readiness Review Sprint
**Verdict:** UNBLOCKED for controlled pilot (4 of 10 scenarios ready)

---

## Catalog Review

| Field | Value |
|---|---|
| Package | Aspose.Words 26.4.0 |
| Framework | netstandard2.0 |
| Dependencies | 17 |
| LowCode namespace | Aspose.Words.LowCode |
| Public types | 25 |
| Public methods | 230 |
| Reflection status | Clean — no errors |

Key dependency: SkiaSharp 3.119.0 (native assets required for image watermark operations using SKBitmap).

---

## Type Role Classification

| Type | Role | Standalone | Confidence |
|---|---|---|---|
| Comparer | operation_facade | YES | 0.95 |
| ComparerContext | settings_model | NO | 0.95 |
| Converter | operation_facade | YES | 0.98 |
| ConverterContext | settings_model | NO | 0.95 |
| **MailMergeDataSource** | **data_source_adapter** | **NO** | **0.95 (reclassified)** |
| MailMergeOptions | options | NO | 0.98 |
| MailMerger | operation_facade | YES | 0.75 |
| MailMergerContext | settings_model | NO | 0.95 |
| MergeFormatMode | enum | NO | 1.0 |
| Merger | operation_facade | YES | 0.90 |
| MergerContext | settings_model | NO | 0.95 |
| Processor | operation_facade | YES | 0.85 |
| ProcessorContext | abstract_base | NO | 1.0 |
| Replacer | operation_facade | YES | 0.95 |
| ReplacerContext | settings_model | NO | 0.95 |
| ReportBuilder | operation_facade | YES | 0.75 |
| ReportBuilderContext | settings_model | NO | 0.95 |
| ReportBuilderOptions | options | NO | 0.95 |
| SignerContext | settings_model | NO | 0.80 |
| SplitCriteria | enum | NO | 1.0 |
| SplitOptions | options | NO | 0.95 |
| Splitter | operation_facade | YES | 0.95 |
| SplitterContext | settings_model | NO | 0.95 |
| Watermarker | operation_facade | YES | 0.95 |
| WatermarkerContext | settings_model | NO | 0.95 |

### MailMergeDataSource Reclassification

**Prior classification:** `workflow_root` at confidence 0.70 (from type_classifier)
**New classification:** `data_source_adapter` at confidence 0.95

**Evidence:**
1. XML summary: "Mail merge data source used for using in [MailMerger]"
2. Has only static `Create()` factory methods — no `Execute()`, `Convert()`, or `Process()`
3. No MailMerger LowCode method accepts `MailMergeDataSource` as parameter — they take `fieldNames[]`, `DataRow`, `DataTable`, or `DataSet` directly
4. Creates `IMailMergeDataSource` for lower-level non-LowCode API usage

**Decision:** `standalone_allowed = false`. Must not appear as workflow_root in any generation scenario.

---

## Options Review

### MailMergeOptions
- 13 boolean/string properties, all optional
- Safe to instantiate with `new MailMergeOptions()` (all properties have sensible defaults)
- Consumer: MailMerger.Execute() (optional last parameter)
- Consumer is blocked — see WORDS-008

### ReportBuilderOptions
- 3 properties: KnownTypes, MissingMemberMessage, Options
- Safe to instantiate with `new ReportBuilderOptions()` (all optional)
- Consumer: ReportBuilder.BuildReport() (optional) and ReportBuilderContext
- Consumer is blocked — see WORDS-009

### SplitOptions
- 2 properties: SplitCriteria (required enum), SplitStyle (optional string)
- SplitCriteria is REQUIRED — no safe default
- SplitCriteria enum values NOT in API catalog
- Consumer: Splitter.Split() (required parameter)
- **Workaround: use Splitter.ExtractPages() instead — no options required**

---

## Generation Candidate Rank

| Scenario | Type | Method | Status |
|---|---|---|---|
| WORDS-001 | Converter | `Convert(inputFile, outputFile)` | **ready_for_controlled_pilot** |
| WORDS-002 | Watermarker | `SetText(inputFile, outputFile, text)` | **ready_for_controlled_pilot** |
| WORDS-003 | Splitter | `ExtractPages(inputFile, outputFile, 0, 1)` | **ready_for_controlled_pilot** |
| WORDS-004 | Replacer | `Replace(inputFile, outputFile, pattern, replacement)` | **ready_for_controlled_pilot** |
| WORDS-005 | Splitter | `Split(inputFile, outputFile, options)` | needs_options_strategy |
| WORDS-006 | Comparer | `Compare(v1, v2, output, author, dateTime)` | needs_fixture_strategy |
| WORDS-007 | Merger | `Merge(output, inputFiles[])` | needs_fixture_strategy |
| WORDS-008 | MailMerger | `Execute(template, output, fieldNames, fieldValues)` | blocked_unclear_semantics |
| WORDS-009 | ReportBuilder | `BuildReport(template, output, data)` | blocked_unclear_semantics |
| WORDS-010 | Processor | `new Processor().From().To().Execute()` | needs_options_strategy |

---

## Controlled Pilot Scope (4 Scenarios)

All 4 scenarios require:
- One `.docx` fixture file from the words fixture source
- No LowCode options types
- File-exists + non-empty output validation

**Approved for controlled pilot:**
1. `Converter.Convert(inputFile, outputFile)` — simplest possible conversion
2. `Watermarker.SetText(inputFile, outputFile, "CONFIDENTIAL")` — string constant watermark
3. `Splitter.ExtractPages(inputFile, outputFile, 0, 1)` — first page extraction
4. `Replacer.Replace(inputFile, outputFile, pattern, replacement)` — safe even with 0 matches

**Excluded from pilot:**
- `Watermarker.SetImage()` stream overloads (require SKBitmap — SkiaSharp native)
- `MailMerger.Execute()` (template+data coupling — merge field names unknown)
- `ReportBuilder.BuildReport()` (LINQ template+data coupling)
- `Splitter.Split()` (SplitCriteria enum values unknown)
- `MailMergeDataSource.Create()` (no LowCode consumer)

---

## Taskcards

### Closed in this sprint

- **followup-words-role-classification-review** — CLOSED_VERIFIED
- **followup-words-options-aware-review** — CLOSED_VERIFIED

### New open taskcards

- `followup-words-split-criteria-enumeration` — enumerate SplitCriteria enum values to unblock WORDS-005
- `followup-words-pair-fixture-strategy` — extend fixture strategy for 2+ fixtures (WORDS-006, WORDS-007)
- `followup-words-mail-merger-fixture-documentation` — document merge field names for WORDS-008

### Remain open (unchanged)

- `followup-pdf-reflection-dedup` — Priority 1
- `followup-family-readiness-ranker-trust` — observability only
- `followup-fixture-token-ci` — CI integration

---

## Next Sprint

**Words Controlled Pilot Sprint**

Prerequisites before running:
1. Change `words.yml` status from `discovery_only` to `active` in a separate PR
2. Run `discover-lowcode --families words --promote-latest` to refresh catalog
3. Run `run --family words --tier 4 --dry-run` with scope limited to WORDS-001 through WORDS-004

Do not expand scope until `followup-words-split-criteria-enumeration` and
`followup-words-pair-fixture-strategy` are closed.
