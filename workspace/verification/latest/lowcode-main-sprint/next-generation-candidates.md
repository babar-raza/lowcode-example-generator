# Lane G — Next Generation Candidates

**Date:** 2026-05-19
**Status:** NO NEW GENERATION THIS SPRINT (reconciliation-only)

## Lane G Gate Check

- Lane A evidence intake: COMPLETE
- Lane B state reconciliation: COMPLETE (4 denominator fixes applied)
- Active family denominators consistent: YES (1876/1876 tests PASS)
- Version drift invalidating generation: NO (Cells/Diagram drift piloted PASS)
- Existing PR dry-run packages stale: NO (packages intact)

## Generation Assessment

Lane G is conditional. This sprint focused on state reconciliation. No new generation was executed because:
1. All reconciliation work completed without requiring regeneration
2. No new LowCode types were discovered requiring generation
3. Existing dry-run packages for PDF are still valid for current Aspose.PDF 26.5.0
4. Cells/Diagram drift pilots passed in Sprint 37 (no immediate rerun required)

## Candidate Work for Next Sprint

1. **PDF pipeline contracts**: Create missing pipeline/contracts/pdf/ entries for security, form-flattener, form-editor, form-exporter, signature (5 examples)
2. **PDF FormImporter**: Monitor via formimporter-watch for Aspose.PDF > 26.5.0
3. **Cells denominator update**: Update source_version 26.4.0 -> 26.5.1 (pilot PASS)
4. **Diagram denominator update**: Update source_version 26.4.0 -> 26.5.0 (pilot PASS)
5. **Cells/Diagram rerun**: Optional controlled rerun against new versions
6. **OCR/PSD**: Monitor for dependency blocker resolution (Aspose.AI.LLM, Aspose.JavaAttributes)

## Blocked/Backlog

- FormImporter: WAVE_H deferred (Aspose.PDF 26.5.0 bug, TC-PDF-FORMIMPORTER-RETEST)
- Timestamp: PERMANENTLY_BLOCKED (external TSA ServerUrl)
- Ofd: PERMANENTLY_BLOCKED (OFD input, no programmatic fixture)
- Words Processor: PERMANENTLY_BLOCKED (no public constructor)
- OCR: DISCOVERY_ONLY (Aspose.AI.LLM missing)
- PSD: DISCOVERY_ONLY (Aspose.JavaAttributes missing)
