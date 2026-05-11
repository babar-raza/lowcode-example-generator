# Family-Scoped Evidence Promotion Result

**Date:** 2026-05-05
**Sprint:** Family-Scoped Evidence Promotion and Latest-State Isolation
**Verdict:** `FAMILY_SCOPED_EVIDENCE_PROMOTION_COMPLETE`

---

## Re-Promotion Results

| Family | Run ID | Files Promoted | Validation | Status |
|---|---|---|---|---|
| cells | pilot-cells-20260430-175422 | 23 | 9/9 PASS | PROMOTED |
| words | pilot-words-20260501-150103 | 20 | 4/4 PASS | PROMOTED |

## Directory Structure

```
workspace/verification/latest/
  families/
    cells/
      _evidence_metadata.json     ← scope=family, family=cells, run_id=...
      validation-results.json     ← 9 Cells scenarios, all PASS
      pr-candidate-manifest.json  ← 9 Cells candidates
      example-gate-results.json   ← 9 Cells examples
      example-reviewer-results.json ← Cells reviewer workspace
      gate-results.json           ← PR_DRY_RUN_READY
      ... (23 files total)
    words/
      _evidence_metadata.json     ← scope=family, family=words, run_id=...
      validation-results.json     ← 4 Words scenarios, all PASS
      pr-candidate-manifest.json  ← 2 Words candidates
      example-gate-results.json   ← 4 Words examples
      example-reviewer-results.json ← Words reviewer workspace
      gate-results.json           ← PR_DRY_RUN_READY
      ... (20 files total)
  _last_promoted_by.json          ← deprecated_latest_alias=true, warning
  all-family-lowcode-discovery.json  ← global (untouched)
  open-taskcard-closure-matrix.json  ← global (untouched)
  family-generation-readiness-rank.json ← global (untouched)
  validation-results.json         ← backward-compat alias (words, last writer)
  ... (backward-compat aliases for all family-specific files)
```

## Isolation Verification

- `families/cells/validation-results.json`: total=9, passed=9
- `families/words/validation-results.json`: total=4, passed=4
- Content differs: YES
- Cross-family contamination: NONE
- Cells does not overwrite Words: VERIFIED
- Words does not overwrite Cells: VERIFIED

## Backward Compatibility

- Top-level `verification/latest/` files still written (for legacy readers)
- `_last_promoted_by.json` marks last writer (words, pilot-words-20260501-150103)
- All existing tests pass — no breaking changes
- `release-status` command reads `{family}`-prefixed and global files — unaffected
- `render-root-readme` reads from `package_path` — unaffected
- `publish-pr` uses in-memory `gate_verdict`; `_verify_evidence` updated to prefer `families/{family}/`
