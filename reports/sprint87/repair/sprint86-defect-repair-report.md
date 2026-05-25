Sprint 87 — Sprint 86 Defect Repair Report
=============================================
Date: 2026-05-25
Author: Lane 1

## S86-D1: commands.log has "result pending" entries

**Root Cause**: Lines 27-29 of reports/sprint86/commands.log end with "result pending"
instead of actual exit codes. EV Rule 102 checks for `(?:Exit|Status):\s*PENDING`.
While these say "result pending" (not exactly "Exit: PENDING"), the pattern is sloppy.

**Sprint 87 Fix**: Sprint 87 commands.log will use explicit exit codes for all entries.
No "pending" or "TBD" entries will remain at bundle close.

**EV Rule**: Rule 127 — `commands_log_no_result_pending` — blocks any line containing
"pending" (case-insensitive) in the result/exit position.

## S86-D2: Placeholder validation result before real EV run

**Root Cause**: sprint86-final-validation-result.json was written as a placeholder
before the real EV Phase B run, then updated. The intermediate file with estimated
values existed in the commit history.

**Sprint 87 Fix**: Sprint 87 validation result will only be written AFTER the actual
EV Phase B run completes. No placeholder values.

**EV Rule**: Rule 128 — `validation_result_not_placeholder` — checks that
applicable + diagnostic = total_rules, and neither field is 0 when total > 100.

## S86-D3: SHA consistency in multi-commit pattern

**Root Cause**: Sprint 86 used 4 commits (ec76d26, 8b5cb89, 961621d, 6060ed7).
bundle-manifest.json references source_sha "ec76d26" but final-clean-proof.txt
references HEAD 961621d. The SHA chain is not explicitly reconciled.

**Sprint 87 Fix**: bundle-manifest.json will include both `source_sha` (first commit)
and `head_sha` (final commit). final-clean-proof.txt will reference the actual HEAD.

**EV Rule**: Rule 129 — `sha_chain_reconciled_in_manifest` — if bundle-manifest.json
has source_sha, it must appear in git log between source_sha and HEAD.

## S86-D4: Approval variable naming inconsistency

**Root Cause**: Sprint 86 final-verdict.md uses `PLUGIN_EXAMPLES_README_PUSH_APPROVAL`
but Sprint 84 MEMORY references `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL`. The spec mentions
both names. No canonical normalization exists.

**Sprint 87 Fix**: Normalize to two canonical variables:
- `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` (for PR creation)
- `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` (for PR merge)
Document `PLUGIN_EXAMPLES_README_PUSH_APPROVAL` as a deprecated alias.

**EV Rule**: Rule 130 — `approval_vars_consistent_naming` — final-verdict.md must not
mix old and new approval variable names without a deprecation note.

## S86-D5: Words version drift contradiction

**Root Cause**: Sprint 81 MEMORY entry stated "RESOLVED (remote=26.5.0 = handoff=26.5.0)"
but Sprint 86 words-version-drift-current.json shows drift=true, remote=26.4.0,
handoff=26.5.0, drift_type=NEEDS_REPAIR_APPROVAL_BLOCKED.

**Investigation**: The Sprint 81 MEMORY entry was incorrect. Sprint 83 scoreboard shows
"Words version drift: NEEDS_REPAIR_APPROVAL_BLOCKED" which contradicts the Sprint 81
MEMORY claim. The drift was never actually resolved — the remote repo still has 26.4.0.

**Sprint 87 Fix**: MEMORY corrected. words-version-drift-current.json carries forward
with drift=true, remote=26.4.0, handoff=26.5.0. Resolution requires approval gate.

**EV Rule**: Rule 131 — `words_drift_not_contradictory` — if words-version-drift-current.json
exists with drift=true, sprint-state.json must not claim drift is resolved.

## S86-D6: final-clean-proof.txt lacks raw git status/diff/log output

**Root Cause**: reports/sprint86/git/final-clean-proof.txt contains git status output
but no git diff or git log output. Rule 103 only requires ` M ` lines or "nothing to commit",
but best practice (established Sprint 77) is to include raw diff and log context.

**Sprint 87 Fix**: final-clean-proof.txt will include:
1. Raw `git status --short` output
2. Raw `git diff --stat` output
3. Raw `git log --oneline -5` output

**EV Rule**: Rule 132 — `final_clean_proof_has_diff_and_log` — final-clean-proof.txt
must contain both "diff" and "log" sections or keywords.
