# Blocker Watch Report — Sprint 42

Generated: 2026-05-19

## HIGH Severity

1. **BLOCKER-PDF-PR-MERGE** (pdf)
   - 6 PDF PRs (#5-#10) awaiting human merge
   - Gate: `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR` — NOT SET
   - Impact: 14 examples stuck at PR_DRY_RUN_READY
   - Since: 2026-05-17

## MEDIUM Severity

2. **BLOCKER-PDF-FORMIMPORTER** (pdf)
   - Aspose.PDF 26.5.0 bug blocks FormImporter
   - Impact: 1 Wave H scenario deferred
   - Since: 2026-05-17

3. **BLOCKER-OCR-DEPENDENCY** (ocr)
   - Aspose.AI.LLM internal assembly not on NuGet
   - Impact: LowCode namespace existence UNKNOWN
   - Since: 2026-05-09

4. **BLOCKER-PSD-DEPENDENCY** (psd)
   - Aspose.JavaAttributes internal assembly not on NuGet
   - Impact: LowCode namespace existence UNKNOWN
   - Since: 2026-05-09

## LOW Severity (Permanently Blocked)

5. **BLOCKER-PDF-TIMESTAMP** — external TSA ServerUrl required
6. **BLOCKER-PDF-OFD** — no OFD programmatic fixture
7. **BLOCKER-WORDS-PROCESSOR** — no public constructor (CS1729+CS0120)

## Concurrent Work

5 new untracked test files appeared (from inter-session commit `b0fee12`):
- test_healing_intelligence_loader.py
- test_llm_router_preflight.py
- test_metrics_collector.py
- test_provider_policy.py
- test_safety_governance.py

Classified as CONCURRENT_WORK — not touched by Sprint 42.
