# LowCode Example Generator: Dropped Planned Example Healing Model

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Status:** HEALING_MODEL_ACTIVE

---

## Example Lifecycle State Machine

```
PLANNED_NOT_ATTEMPTED
  -> (attempt generation) -> GENERATION_FAILED
  -> (fix LLM prompt or fixture) -> RELAUNCH_READY
  -> (relaunch) -> RELAUNCH_ATTEMPTED
    -> (pass build+run+reviewer) -> RELAUNCH_PASSED -> PR_READY -> PUBLISHED -> POST_MERGE_VERIFIED
    -> (fail after 3 attempts) -> RELAUNCH_FAILED -> BLOCKED (with exact evidence)
                                                   -> (product API limit proven) -> DROPPED_WITH_EVIDENCE

NON_RUNNABLE_WITH_SOURCE_OF_TRUTH (permanent exclusion; no relaunch)
DROPPED_WITH_EVIDENCE (no relaunch unless evidence is challenged)
```

---

## Dropped/Deferred Example Audit Table

### Cells (22 total types) - ALL ACCOUNTED FOR

| Type | State | Root Cause | Relaunch |
|------|-------|-----------|---------|
| HtmlConverter | POST_MERGE_VERIFIED | n/a | n/a |
| ImageConverter | POST_MERGE_VERIFIED | n/a | n/a |
| JsonConverter | POST_MERGE_VERIFIED | n/a | n/a |
| PdfConverter | POST_MERGE_VERIFIED | n/a | n/a |
| SpreadsheetConverter | POST_MERGE_VERIFIED | n/a | n/a |
| SpreadsheetLocker | POST_MERGE_VERIFIED | n/a | n/a |
| SpreadsheetMerger | POST_MERGE_VERIFIED | n/a | n/a |
| SpreadsheetSplitter | POST_MERGE_VERIFIED | n/a | n/a |
| TextConverter | POST_MERGE_VERIFIED | n/a | n/a |
| AbstractLowCodeLoadOptionsProvider | NON_RUNNABLE_WITH_SOT | LOWCODE_API_NOT_STANDALONE | NOT_RELAUNCHED |
| AbstractLowCodeProtectionProvider | NON_RUNNABLE_WITH_SOT | LOWCODE_API_NOT_STANDALONE | NOT_RELAUNCHED |
| AbstractLowCodeSaveOptionsProvider | NON_RUNNABLE_WITH_SOT | LOWCODE_API_NOT_STANDALONE | NOT_RELAUNCHED |
| LowCodeHtmlSaveOptions | NON_RUNNABLE_WITH_SOT | WRONG_OPTIONS_CLASS | NOT_RELAUNCHED |
| LowCodeImageSaveOptions | NON_RUNNABLE_WITH_SOT | WRONG_OPTIONS_CLASS | NOT_RELAUNCHED |
| LowCodeLoadOptions | NON_RUNNABLE_WITH_SOT | WRONG_OPTIONS_CLASS | NOT_RELAUNCHED |
| LowCodeMergeOptions | NON_RUNNABLE_WITH_SOT | WRONG_OPTIONS_CLASS | NOT_RELAUNCHED |
| LowCodePdfSaveOptions | NON_RUNNABLE_WITH_SOT | WRONG_OPTIONS_CLASS | NOT_RELAUNCHED |
| LowCodeSaveOptions | NON_RUNNABLE_WITH_SOT | WRONG_OPTIONS_CLASS | NOT_RELAUNCHED |
| LowCodeSplitOptions | NON_RUNNABLE_WITH_SOT | WRONG_OPTIONS_CLASS | NOT_RELAUNCHED |
| LowCodeSaveOptionsProviderOfAssembling | NON_RUNNABLE_WITH_SOT | REQUIRES_STATEFUL_CONTEXT | NOT_RELAUNCHED |
| LowCodeSaveOptionsProviderOfPlaceHolders | NON_RUNNABLE_WITH_SOT | REQUIRES_STATEFUL_CONTEXT | NOT_RELAUNCHED |
| SplitPartInfo | NON_RUNNABLE_WITH_SOT | WRONG_RESULT_CLASS | NOT_RELAUNCHED |

**Cells equation: 9 + 13 = 22 HOLDS. No gaps.**

---

### Words (25 total types) - GOVERNANCE GAPS IDENTIFIED

| Type | State | Root Cause | Relaunch Allowed | Prerequisite |
|------|-------|-----------|-----------------|-------------|
| Converter | POST_MERGE_VERIFIED | n/a | n/a | n/a |
| Watermarker | POST_MERGE_VERIFIED | n/a | n/a | n/a |
| Splitter | POST_MERGE_VERIFIED | n/a | n/a | n/a |
| Replacer | POST_MERGE_VERIFIED | n/a | n/a | n/a |
| Comparer | DROPPED_WITH_EVIDENCE (pilot scope) | RC-007: MISSING_PAIR_FIXTURE | NO | Pair fixture strategy (taskcard followup-words-pair-fixture-strategy) |
| Merger | DROPPED_WITH_EVIDENCE (pilot scope) | RC-007: MISSING_PAIR_FIXTURE | NO | Pair fixture strategy |
| MailMerger | DROPPED_WITH_EVIDENCE (pilot scope) | RC-008: MISSING_TEMPLATE_FIXTURE | NO | Template DOCX fixture (taskcard followup-words-mail-merger-fixture-documentation) |
| SplitCriteria (Splitter.Split) | DROPPED_WITH_EVIDENCE (pilot scope) | RC-009: MISSING_ENUM_STRATEGY | NO | Enum discovery strategy (taskcard followup-words-split-criteria-enumeration) |
| Processor | DROPPED_WITH_EVIDENCE (pilot scope) | CLASSIFICATION_GAP | NO | Full classification (taskcard followup-words-full-coverage-expansion) |
| ReportBuilder | DROPPED_WITH_EVIDENCE (pilot scope) | CLASSIFICATION_GAP | NO | Full classification |
| *Context classes (8 estimated)* | *NON_RUNNABLE_PENDING_CLASSIFICATION* | RC-010: unproven | NO | NEW-07: formal DllReflector classification |
| *ENUM/OPTIONS types (5 estimated)* | *NON_RUNNABLE_PENDING_CLASSIFICATION* | CLASSIFICATION_GAP | NO | NEW-07: formal classification |
| *Others (~6)* | *PENDING_CLASSIFICATION* | workflow_root_types=NULL | NO | NEW-07 |

**Words governance gap (RC-012):** 16 of 21 deferred types are labeled NON_RUNNABLE but have not been formally classified via DllReflector. FULL_SOT denominator equation cannot be evaluated until NEW-07 completes.

---

### PDF (101 total types) - COMPLETION QUEUE GAP IDENTIFIED

| Type | State | Root Cause | Notes |
|------|-------|-----------|-------|
| Merger | POST_MERGE_VERIFIED | n/a | PR#1 |
| TextExtractor | POST_MERGE_VERIFIED | n/a | PR#1 |
| Splitter | PR_READY | RC-004: resolved | PR#3 package ready |
| Optimizer | REVIEWED_AWAITING_PR | RC-001/RC-002/RC-003: resolved | Needs 2nd PASS for PR#4 |
| DocConverter | PLANNED_NOT_ATTEMPTED (pilot deferred) | format-specific DOC validation | RC-011: not in completion queue |
| FormEditor | PLANNED_NOT_ATTEMPTED (pilot deferred) | MISSING_FIXTURE (form fields PDF) | RC-011: not in completion queue |
| FormExporter | PLANNED_NOT_ATTEMPTED (pilot deferred) | MISSING_FIXTURE + CLASSIFICATION_GAP | RC-011 |
| FormFlattener | PLANNED_NOT_ATTEMPTED (pilot deferred) | MISSING_FIXTURE | RC-011 |
| FormImporter | PLANNED_NOT_ATTEMPTED (pilot deferred) | MISSING_PAIR_FIXTURE | RC-011 |
| Html | PLANNED_NOT_ATTEMPTED (pilot deferred) | WRONG_FIXTURE_SHAPE | RC-011 |
| ImageExtractor | PLANNED_NOT_ATTEMPTED (pilot deferred) | CLASSIFICATION_GAP | RC-011 |
| Jpeg | PLANNED_NOT_ATTEMPTED (pilot deferred) | CLASSIFICATION_GAP | RC-011 |
| Ofd | PLANNED_NOT_ATTEMPTED (pilot deferred) | MISSING_FIXTURE (OFD format) | RC-011 |
| *8 more WORKFLOW_ROOT converters* | PLANNED_NOT_ATTEMPTED (pilot deferred) | CLASSIFICATION_GAP | RC-011 |
| *Barcode, QrCode* | PLANNED_NOT_ATTEMPTED (pilot deferred) | CLASSIFICATION_GAP | RC-011 |
| *SignatureValidator* | PLANNED_NOT_ATTEMPTED (pilot deferred) | MISSING_FIXTURE (signed PDF) | RC-011 |
| *76 non-runnable types* | NON_RUNNABLE_WITH_SOT | OPTIONS/RESULT/CALLBACK/etc | Formally classified |

**PDF governance gap (RC-011):** 21 WORKFLOW_ROOT types classified in pdf-type-role-classification.json with pilot_deferred_reason but NO entry in completion queue. These are "phantom planned scenarios" -- planned but not tracked.

---

## Relaunch Governance Rules

1. No relaunch attempt without a documented root cause
2. No relaunch attempt without a specific fix applied
3. Maximum 3 relaunch attempts before escalating to BLOCKED or DROPPED
4. Every relaunch attempt recorded in backlog with attempt_count and last_failure_stage
5. RELAUNCH_PASSED examples must go through full PR dry-run packaging before publishing
6. RELAUNCH_PASSED examples must update denominator published_count after merge
7. DROPPED_WITH_EVIDENCE requires governance documentation (backlog entry with evidence file path)

---

## Healing Priority Queue

| Priority | Type | Family | Root Cause | Prerequisite |
|----------|------|--------|-----------|-------------|
| HIGH | PDF PR#3 | pdf | Blocked on APPROVE_LIVE_PR | Token must be set |
| HIGH | Words completion queue gap | words | RC-014 | R6.5 audit |
| HIGH | PDF completion queue gap (21 types) | pdf | RC-011 | R6.5 audit |
| HIGH | Words workflow_root classification | words | RC-012 | NEW-07 |
| MEDIUM | Words Comparer/Merger | words | RC-007 | Pair fixture strategy |
| MEDIUM | Words MailMerger | words | RC-008 | Template DOCX |
| MEDIUM | Words SplitCriteria | words | RC-009 | Enum discovery |
| MEDIUM | Stale PDF Splitter runtime failure | pdf | RC-005 | Mark superseded |
| LOW | Backlog-to-taskcard bridge | all | RC-013 | Implementation |
