# Commit Plan — LANE 11

**Sprint**: lowcode-final-closure-pass3-20260530

## Artifact-Staging Convention

Per the convention established in Healing Sprint 1F:
1. All tracked files committed first (no tracked file modified after final commit)
2. Artifact-metadata generated POST-COMMIT to `.local/` (gitignored)
3. ZIP built last (no commit after ZIP)
4. `git status --short` MUST be clean before ZIP build

## Files to Stage in Final Evidence Commit

### Modified tracked files (from sprint work):
- `tests/unit/test_programmatic_fixture_fewshots.py` — DEF-004 test fix (DrawEllipse assertion)
- `workspace/pr-dry-run/pdf-controlled-pilot/README.md` — updated by Lane 9 dry-run
- `workspace/verification/latest/cells-readme-backfill-simulation.json` — Lane 9 dry-run
- `workspace/verification/latest/cells-root-readme-audit.json` — Lane 9 dry-run
- `workspace/verification/latest/cells-root-readme-render-result.json` — Lane 9 dry-run
- `workspace/verification/latest/families/diagram/gate-results.json` — Lane 6 promotion
- `workspace/verification/latest/families/diagram/pr-candidate-manifest.json` — Lane 6 promotion
- `workspace/verification/latest/families/diagram/publishing-report.json` — Lane 6 promotion
- `workspace/verification/latest/families/diagram/validation-results.json` — Lane 6 promotion
- `workspace/verification/latest/family-publish-readiness.json` — Lane 9 dry-run
- `workspace/verification/latest/release-status.json` — Lane 9 dry-run
- `workspace/verification/latest/words-readme-backfill-simulation.json` — Lane 9 dry-run
- `workspace/verification/latest/words-root-readme-audit.json` — Lane 9 dry-run
- `workspace/verification/latest/words-root-readme-render-result.json` — Lane 9 dry-run

### Untracked files to add:
- `docs/development/open-taskcard-closure-matrix.md` — Lane 0+11 deliverable
- `reports/lowcode-final-closure-pass3-20260530/` — all Pass 3 sprint reports
- `scripts/collect_lane2_lane4_evidence.py` — Lane 2/4 collection script

## Commit Message Plan

```
feat(pass3): LOWCODE FINAL CLOSURE PASS 3 — raw evidence, full pytest, strict replay, diagram promotion

14-lane sprint providing complete evidence chain for reviewer acceptance:
- Lane 0: Preflight, run ID selection, dirty state classification
- Lane 1: Prior bundle acceptance normalization (11 accepted/not-accepted)
- Lane 2: 42/42 raw Program.cs snapshots with SHA256 hash verification
- Lane 3: Strict replay contract (denominator/catalog/generator/output hash proofs)
- Lane 4: Raw dotnet restore/build/run logs for all 42 examples
- Lane 5: Full pytest 3209/3227 pass (0 failed, 18 skipped), DEF-004 test fix
- Lane 6: Diagram stale BLOCKED_GENERATION promotion from canonical durable-fix run
- Lane 7: Reviewer unavailable — fallback human audit 42/42 PASS
- Lane 8: 42 validated vs 41 PR-candidate truth model (words-comparer excluded)
- Lane 9: Publication dry-run — 3/6 packages ready, approval gate only blocker
- Lane 10: External blocker NuGet recheck — epub/ocr/psd confirmed unchanged
- Lane 11: Artifact integrity, open-taskcard-closure-matrix.md committed
- Lane 12: Work-ahead preparation
- Lane 13: AI/LLM accounting
- Lane 14: IV/adversarial review

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## ECC Note

ECC must be run after all evidence files are written but before the final commit.
The ECC script for this sprint must be created or an existing one adapted.
