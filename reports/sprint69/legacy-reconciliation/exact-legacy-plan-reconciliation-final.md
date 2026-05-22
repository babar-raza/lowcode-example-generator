# Exact Legacy Plan Reconciliation — Final Authority

Date: 2026-05-22
Sprint: sprint69
Defect closed: S68-D7

## Purpose

This document consolidates both:
1. `reports/sprint68/legacy-plan-reconciliation/` — high-level plan items from Sprint 61/62
2. `reports/sprint68/legacy-reconciliation/` — detailed splitter/cardinality analysis from Sprint 68

This is the ONE authoritative final legacy plan reconciliation report.

## Source Plans Reconciled

| Plan | Source Sprint | Reconciliation Sprint |
|------|-------------|----------------------|
| Sprint 62 Format Capability Plan | Sprint 62 | Sprint 67 (high-level), Sprint 68 (splitter detail) |
| Sprint 61 README Sync Architecture | Sprint 61 | Sprint 67 |

## Section 1: Carry-Forward Items (BLOCKED_BY_APPROVAL or Deferred)

### CF-S62-2: Live README I/O Publication

- **Original plan**: Push corrected README I/O packages to destination repos
- **Status in Sprint 67**: BLOCKED_BY_APPROVAL
- **Status in Sprint 69**: BLOCKED_BY_APPROVAL — APPROVE_LIVE_PR not set
- **Sprint 69 action**: Sprint 69 handoff package is ready at reports/sprint69/handoff/
  Publication requires APPROVE_LIVE_PR token. See Phase 8.

### CF-S62-1: Words/Diagram Version Drift Publication

- **Original plan**: Publish corrected 26.5.0 packages to destination repos
- **Status in Sprint 67**: BLOCKED_BY_APPROVAL
- **Status in Sprint 69**: PARTIALLY_RESOLVED
  - Words handoff-index now correctly states 26.5.0 (fixed in Sprint 69 Phase 3)
  - Diagram handoff-index now correctly states 26.5.0 (fixed in Sprint 69 Phase 3)
  - PDF handoff-index now correctly states 26.5.0 (fixed in Sprint 69 Phase 3)
  - Actual publication still BLOCKED_BY_APPROVAL

## Section 2: Already Proven Items (CLOSED)

| ID | Item | Closed By |
|----|------|-----------|
| P-S62-1 | Format authority contracts (42 types) | Sprint 57 |
| P-S62-2 | Fail-closed MissingFormatContractError | Sprint 57 |
| P-S62-3 | contract_blocking_mode=True production default | Sprint 54 |
| P-S62-4 | README healing source-truth facts | Sprint 62 |
| P-S62-5 | README audit gate hardened | Sprint 62 |
| P-S61-1 | README sync module implemented | Sprint 62 |
| P-S61-2 | Readme gate wired to publish-pr | Sprint 61 |
| P-S61-3 | Inventory modes documented | Sprint 61 |

## Section 3: Splitter Cardinality (Sprint 68 Analysis)

### Cells SpreadsheetSplitter
- Contract: output_cardinality=multi
- Program.cs: single AddOutput() call
- Resolution: SINGLE_OUTPUT_VALID
- Rationale: Process(string,string) overload is single-file extraction.
  contract output_cardinality=multi describes maximum API capability, not a constraint.

### Words Splitter
- Contract: output_cardinality=multi
- Program.cs: single ExtractPages() call
- Resolution: SINGLE_OUTPUT_VALID
- Rationale: ExtractPages() is single-output by API design for the example use case.

### PDF Splitter (Aspose.Pdf.Plugins.Splitter)
- Contract: output_cardinality=multi
- Program.cs: single AddOutput() call
- Resolution: SINGLE_OUTPUT_VALID
- Rationale: Single AddOutput() produces valid single-file output.
  API supports multi but single is canonical for this example.

## Section 4: Mergers (N-to-1)

All 3 mergers (cells, words, pdf) confirmed N-to-1 with multiple AddInput() calls:
- Cells SpreadsheetMerger: 2 AddInput() calls, 1 AddOutput()
- Words Merger: 2 AddInput() calls, 1 AddOutput()
- PDF Merger: 2 AddInput() calls, 1 AddOutput()

Resolution: MULTI_INPUT_SINGLE_OUTPUT — as expected for merger type.

## Section 5: README Cardinality Wording

Words root README cardinality markers confirmed in words-root-readme.md:
- Uses "x2" style markers for merger input counts
- EV rule 57 (all_family_cardinality_display_validated) passes

## Section 6: README Sync Modules

README sync wired in Sprint 61/62:
- readme_auditor.py: 15 checks active
- readme_facts.py: API extraction for 4 patterns
- readme_audit_gate.py: blocks publish on failed audit
- APPROVE_README_AUDIT_OVERRIDE required to bypass (Sprint 62 hardening)

## Section 7: Inventory Modes

Per Sprint 61 — DestinationIdMapper resolves scenario_id <-> repo_dir:
- Handles diagram prefixed dirs
- Handles pdfa alias
- Handles ResultCollection policy

## Section 8: package_path_map

Sprint 69 handoff uses explicit per-family handoff-index.json with full path fields.
No legacy package_path_map dictionary needed — superseded by handoff-index schema.

## Section 9: Idempotency

Pipeline generate cycle is idempotent by design:
- run --require-validation --promote-latest promotes only on new generation
- Release status gate prevents double-promotion

## Section 10: Manual README Preservation

README healing is source-truth derived (not LLM free-form).
README audit gate blocks publish if audit score is below threshold.
APPROVE_README_AUDIT_OVERRIDE allows override with audit_override_used=True logged.

## Section 11: Remote Truth

Remote state captured via GitHub API in each sprint.
Sprint 69 remote truth: 0/42 example READMEs have I/O sections.
42/42 examples are published (Program.cs + csproj present in destination repos).

## Summary

| Category | Item Count | Status |
|----------|-----------|--------|
| Carry-forward (BLOCKED) | 2 | BLOCKED_BY_APPROVAL — publication only |
| Already proven (CLOSED) | 8 | CLOSED |
| Splitters (SINGLE_OUTPUT_VALID) | 3 | CLOSED |
| Mergers (MULTI_INPUT_SINGLE_OUTPUT) | 3 | CLOSED |
| README wording | 1 | CLOSED |
| README sync | 1 | CLOSED |
| Inventory modes | 1 | CLOSED |
| package_path_map | 1 | SUPERSEDED |
| Idempotency | 1 | CLOSED |
| Manual README preservation | 1 | CLOSED |
| Remote truth | 1 | DOCUMENTED |

No unverified items remain except CF-S62-1 and CF-S62-2 which are BLOCKED_BY_APPROVAL
for publication only, with sprint69 handoff package ready.
