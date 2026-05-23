# Sprint 71 — EvidenceValidator Gap Analysis

## Sprint 70 Validator Gaps (leading to S70-D1, S70-D2)

Sprint 70 rules 68–72 correctly checked that:
- `handoff-index.json` root_readme.source_path uses current sprint paths
- root README files are physically present
- root README hashes match

But Sprint 70 rules did NOT check:
1. **`destination/content-audit-final.json`** for stale sprint paths → S70-D1 passed silently
2. **`publication/publication-truth-matrix-final.json`** for stale sprint paths → S70-D2 passed silently
3. **`remote/remote-vs-handoff-final.json`** for stale sprint paths → also stale (sprint69)

## Sprint 71 New Rules (73–78)

Sprint 71 adds 6 new rules to close S70-D1, S70-D2, S70-D3:

| Rule # | Rule ID | What It Checks |
|--------|---------|----------------|
| 73 | `content_audit_final_no_stale_paths` | `destination/content-audit-final.json` must have no stale sprint paths |
| 74 | `publication_matrix_no_stale_paths` | `publication/publication-truth-matrix-final.json` must have no stale sprint paths |
| 75 | `handoff_index_no_stale_paths` | All `handoff-index.json` files must have no stale sprint paths |
| 76 | `remote_vs_handoff_no_stale_paths` | `remote/remote-vs-handoff-final.json` must have no stale sprint paths |
| 77 | `content_audit_final_files_exist` | All `handoff_path` in content-audit-final.json must physically exist |
| 78 | `publication_matrix_files_exist` | All `handoff_package_path` in publication-truth-matrix-final.json must physically exist |

## Sprint-Aware Stale Path Detection

The `_get_stale_paths_in_content(content)` method is sprint-aware:
- Reads `sprint_id` from `sprint-state.json` or `evidence-contract.json`
- Computes current prefix as `reports/{sprint_id}/`
- Flags any `reports/sprintN/` path where `sprintN != current_sprint_id`
- Also flags `workspace/pr-dry-run`

This prevents false positives in test fixtures where the sprint_id differs from production.

## Sprint 70 Revalidation

Under Sprint 71 rules, Sprint 70 bundle fails 3 rules (exactly matching the 3 defects):
- `content_audit_final_no_stale_paths`: FAIL (reports/sprint69/ in content-audit-final.json)
- `publication_matrix_no_stale_paths`: FAIL (reports/sprint69/ in publication-truth-matrix-final.json)
- `remote_vs_handoff_no_stale_paths`: FAIL (reports/sprint69/ in remote-vs-handoff-final.json)

## Sprint 71 Validator Summary

| Phase | Rules | Status |
|-------|-------|--------|
| All phases total | 78 | All PASS for sprint71 bundle |
| Phase A (bootstrap, excl. rule 21) | 77 | Used for ECC bootstrap |
| Phase B (all 78 rules) | 78 | Final validation |
