# Final Proof Template Rule

**Lane:** 1 — Final Authority and Proof Healing
**Rule ID:** PROOF-TEMPLATE-001
**Date:** 2026-05-27

## Rule Statement

> A final-clean-proof.txt file MUST contain the actual HEAD SHA at the time of commit.
> Placeholder text such as "This file will be updated with final HEAD after the proof commit."
> is PROHIBITED in any committed proof file.

## Rationale

The 3-commit pattern for sprint closeout is:
1. Evidence commit (source_sha)
2. Finalize proof (proof commit — captures HEAD of step 1)
3. Update proof with step 2 SHA (head_sha)

In the historical execution of the Final Publication Sprint, commit `0f5b09c` (step 2)
contained the placeholder "This file will be updated with final HEAD after the proof commit."
This was immediately corrected in commit `adcf3dc` (step 3), but the placeholder existed
briefly in git history.

## Corrected Procedure

### Step 2 — Finalize Proof Commit

The proof file at commit time (step 2) MUST contain:
- The actual HEAD SHA from `git rev-parse HEAD` captured after step 1
- The actual git log output (no placeholders)
- The actual git status output (no placeholders)

If the step-3 SHA is not yet known at step-2 commit time, the file should say:
  `head_sha: [to be captured in step 3]`

NOT:
  `This file will be updated with final HEAD after the proof commit.`

### Step 3 — Update Proof with Step-2 SHA

The proof file is updated to replace `[to be captured in step 3]` with the actual SHA.

## Enforcement

- Pre-commit check: grep for `will be updated` in any `final-clean-proof.txt` file staged for commit.
- If found: ABORT commit and require correction.

## Compliance Status

- Sprint 91 final-clean-proof.txt: COMPLIANT (no placeholder text)
- Final Publication final-clean-proof.txt (HEAD): COMPLIANT (placeholder removed in adcf3dc)
- Healing Sprint 1 final-clean-proof.txt: COMPLIANT (follows this rule)

**Rule Status:** ACTIVE
