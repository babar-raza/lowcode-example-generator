# Legacy Reconciliation Index — Sprint 68

Date: 2026-05-22
Sprint: sprint68

## Purpose

Sprint 68 extends Sprint 67's high-level legacy reconciliation with per-type splitter
cardinality analysis. Sprint 67 defect S67-D2 found that reconciliation-index.md was
high-level only — no per-type decisions were documented for splitter cardinality.

## Items Reconciled in Sprint 68

### 1. Splitter Output Cardinality (S67-D2 repair)

Three splitter types had `output_cardinality=multi` in contracts but Program.cs uses
single-output patterns. Full per-type analysis performed:

| Type | Contract | Program.cs | Resolution |
|------|----------|------------|------------|
| cells/SpreadsheetSplitter | multi | single output | SINGLE_OUTPUT_VALID |
| words/Splitter | multi | single output (ExtractPages) | SINGLE_OUTPUT_VALID |
| pdf/Splitter | multi | single AddOutput | SINGLE_OUTPUT_VALID |

**Decision**: Single-output usage is valid for all three. The contract `output_cardinality=multi`
describes maximum API capability. No regeneration required.

See: `splitter-cardinality-matrix.json`, `splitter-resolution.md`

### 2. Merger N-to-1 Cardinality

Three merger types confirmed:
- cells/SpreadsheetMerger: README shows N→1, contract `input_cardinality=multi` — CONFIRMED
- words/Merger: README shows N→1 — CONFIRMED
- pdf/Merger: README shows N→1 — CONFIRMED

### 3. All Other Type Cardinality

36 remaining types are converters, extractors, or single-I/O operations — no cardinality
discrepancy exists. Confirmed by contract inspection and Program.cs review.

See: `cardinality-reconciliation-final.json`

## Items Carried Forward from Sprint 67

The following sprint67 reconciliation items remain valid and are not re-examined:

| Item | Sprint 67 Verdict | Sprint 68 Status |
|------|------------------|-----------------|
| Sprint 62 format capability plan | PARTIALLY_VERIFIED / SUPERSEDED | Carried forward |
| Sprint 61 README sync plan | PARTIALLY_VERIFIED | Carried forward |
| items-already-proven.json | VERIFIED | Carried forward |
| items-to-carry-forward.json | VERIFIED | Carried forward |
| items-superseded.json | VERIFIED | Carried forward |
| items-contradicted.json | VERIFIED | Carried forward |

## Final Status

All 42 type cardinality decisions are now documented with explicit per-type rationale.
Sprint 68 closes S67-D2 (splitter cardinality mismatch).
