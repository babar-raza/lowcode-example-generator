Sprint 87 — Sprint 86 Evidence Hygiene Normalization
======================================================
Date: 2026-05-25
Author: Lane 1

## Items Documented

### S86-G1: commands.log incomplete exit codes
- **File**: reports/sprint86/commands.log lines 27-29
- **Issue**: "result pending" instead of explicit exit codes
- **Patch**: None applied (Sprint 86 artifact is historical)
- **Prevention**: EV Rule 127 (commands_log_no_result_pending)

### S86-G2: Approval variable naming inconsistency
- **File**: reports/sprint86/final-verdict.md line 28
- **Issue**: Uses PLUGIN_EXAMPLES_README_PUSH_APPROVAL (deprecated name)
- **Patch**: None applied (Sprint 86 is historical)
- **Prevention**: EV Rule 130 (approval_vars_consistent_naming)
- **Resolution**: Sprint 87 normalizes to PLUGIN_EXAMPLES_MERGE_PR_APPROVAL

### S86-G3: Words version drift MEMORY contradiction
- **File**: MEMORY.md Sprint 81 entry
- **Issue**: Claimed "RESOLVED (remote=26.5.0 = handoff=26.5.0)" but drift persists
- **Patch**: MEMORY.md corrected in Sprint 87
- **Prevention**: EV Rule 131 (words_drift_status_consistent)

### S86-G4: final-clean-proof.txt missing diff/log
- **File**: reports/sprint86/git/final-clean-proof.txt
- **Issue**: Only git status output, no diff or log sections
- **Patch**: None applied (Sprint 86 is historical)
- **Prevention**: EV Rule 132 (final_clean_proof_has_diff_and_log)
