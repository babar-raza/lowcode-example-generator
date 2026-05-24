# Validator Gap Analysis — Sprint 83

## Sprint 82 Carry-Forward Items (S82-F1 through S82-F4)

Sprint 82 identified 4 validator gaps. Sprint 83 closes all 4.

### S82-F1: Stale PASS_PENDING_COMMIT label

**Problem**: After the two-commit bundle pattern, `final-consistency-check.json` still said `PASS_PENDING_COMMIT` — a provisional label. No rule existed to detect this stale state.

**Fix**: EV Rule 114 `final_consistency_check_not_stale_after_commit`
- Fires when `final-consistency-check.json` has status `PASS_PENDING_COMMIT` AND `final-clean-proof.txt` has a real 40-char SHA
- Returns FAIL with evidence showing the contradiction
- Sprint 83 commits to using plain `"PASS"` — Rule 114 will confirm

### S82-F2: Publication truth matrix count drift

**Problem**: No rule enforced that the flat-array publication-truth-matrix-final.json had exactly 42 records with correct per-family distribution. A corrupted or partial matrix could pass validation silently.

**Fix**: EV Rule 112 `publication_truth_matrix_has_expected_count`
- Enforces: total=42, cells=9, words=8, pdf=19, diagram=2, email=1, slides=3
- Only applies to flat-array format (Sprint 82+)

### S82-F3: Root README conflict strategy not documented

**Problem**: The deconflict strategy for cells#5, words#7, diagram#2 was implicit. No rule required documenting it.

**Fix**: EV Rule 113 `root_readme_conflict_strategy_documented`
- When `remote-repo-state-before.json` shows open PRs, requires `remote/remote-conflict-check.md` or `conflicts/root-readme-pr-conflict-strategy.md` to exist and be non-empty
- Sprint 83 Lane B creates `conflicts/root-readme-pr-conflict-strategy.md`

### S82-F4: No publication-file-plan.json required when PRs were claimed

**Problem**: If any record in publication-truth-matrix-final.json had a non-null `pr_url`, no rule required `publication-file-plan.json` to exist as supporting evidence.

**Fix**: EV Rule 115 `publication_file_plan_present_if_pr_creation_claimed`
- Scans flat-array matrix for any non-null `pr_url`
- If found, requires `publication-file-plan.json` to exist
- Trivially passes when all pr_urls are null (approval-blocked sprint)

## Compatibility Fixes

Three existing rules needed flat-array format compatibility:

| Rule | Fix Applied |
|------|-------------|
| `_rule_publication_state_not_mixed` | `isinstance(data, list)` guard; accept `remote_readme_io_classification` OR `remote_readme_has_io_docs` |
| `_rule_publication_truth_no_stale_remote_claimed` | Early return for flat-array: "rule not applicable for flat-array format" |
| `_rule_publication_truth_matrix_has_expected_count` | Returns `passed=True` for non-list (wrapped format) — rule only validates Sprint 82+ |

## EV Rule Count

| Sprint | Added | Total |
|--------|-------|-------|
| Sprint 80 | 79-85 | 85 |
| Sprint 75 | 86-93 | 93 |
| Sprint 80 | 94-111 | 111 |
| **Sprint 83** | **112-115** | **115** |

---
*Lane E — Sprint 83 — 2026-05-24*
