# Previous Bundle Normalization — LANE 1

**Sprint**: lowcode-final-closure-pass3-20260530
**Previous bundle**: lowcode-durable-full-closure-20260529-evidence.zip
**Reviewer verdict**: DURABLE_GENERATOR_REPAIR_PROGRESS_ACCEPTED_FULL_CLOSURE_NOT_YET_ACCEPTED

## What Is Accepted from Prior Bundle

| Item | Status |
|------|--------|
| Durable generator fixes committed in source (code_generator.py + family YAMLs) | ACCEPTED |
| template_first: true for 7 example types across 5 families | ACCEPTED |
| DEF-001: cells-spreadsheet-merger File.Copy + SpreadsheetMerger.Process | ACCEPTED |
| DEF-002: words-merger Merger.Merge static call | ACCEPTED |
| DEF-003: words-watermarker programmatic BMP + Watermarker.SetImage | ACCEPTED |
| DEF-004: diagram-diagram-converter DrawEllipse + DiagramConverter.Process | ACCEPTED |
| DEF-005: diagram-pdf-converter DrawEllipse + PdfConverter.Process | ACCEPTED |
| DEF-008: pdf-table-generator new TableOptions() pattern | ACCEPTED |
| DEF-009: slides-convert fully-qualified Aspose.Slides.LowCode.Convert.ToPdf() | ACCEPTED |
| 35/35 durable-fix unit tests pass | ACCEPTED |
| gate_generation passed for all 6 families (examples_generated > 0) | ACCEPTED |
| Prior workspace-only patches promoted to generator source | ACCEPTED |
| ECC 75/75 sprint evidence files | ACCEPTED |

## What Remains Unaccepted

| Gap | Required Action |
|-----|----------------|
| No raw command logs bundled | Lane 0 raw-commands.log required |
| No raw dotnet restore/build/run logs for all 42 examples | Lane 4 e2e-raw/ required |
| No actual Program.cs snapshots (only tree lists + hashes) | Lane 2 generated-source/ required |
| Full pytest not run; only 35 durable-fix unit tests | Lane 5 full-pytest.log required |
| --replay-from generation used; no strict replay contract | Lane 3 replay-contract/ required |
| Diagram publisher blocked by stale workspace/verification/latest | Lane 6 promotion required |
| Publication dry-run shows 41 PR candidates vs 42 examples | Lane 8 + Lane 9 required |
| gate_reviewer failed; treated as non-required without fallback semantics | Lane 7 required |
| final-clean-proof listed .kilo/ as unresolved | Lane 0+11: classified and resolved |
| External blocker recheck is summary-only; no raw NuGet logs | Lane 10 required |
| docs/development/open-taskcard-closure-matrix.md untracked non-ignored | Lane 0+11: will commit |

## Reclassification of Prior Sprint

The prior sprint `lowcode-durable-full-closure-20260529` is reclassified from
"LOWCODE_DURABLE_FULL_CLOSURE_ACCEPTED" (self-assessed) to:

**DURABLE_GENERATOR_REPAIR_PROGRESS_ACCEPTED_FULL_CLOSURE_NOT_YET_ACCEPTED**

per the external reviewer's verdict. All agent-internal claims of "ACCEPTED" for that sprint
are superseded by this reclassification. Future sprints must reference this verdict.
