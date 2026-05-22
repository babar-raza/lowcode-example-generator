# Final Next Actions — Sprint 45

Generated from HEAD: 13f4e93

## Priority Actions

1. **Recreate PDF PRs** — Set `APPROVE_LIVE_PR` to close and recreate PRs #5-#10 with fresh branches against current main. All 6 currently CONFLICTING.

2. **Merge PDF PRs** — After PR recreation, set `APPROVE_MERGE_PR` to merge conflict-free PRs. 14 examples awaiting publication.

3. **FormImporter retest** — Retest when Aspose.PDF > 26.5.0 released (TC-PDF-FORMIMPORTER-RETEST).

4. **OCR/PSD recheck** — Both dependencies still 404 on NuGet. Periodic recheck.

5. **Loop idempotency** — Add change-detection to planner_loop.py so it stops when actions produce identical results across cycles.
