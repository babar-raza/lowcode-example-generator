# Validation Target Audit

## Finding: PROOF_TARGET_MISMATCH

Sprint 47's `evidence-contract-validation-proof.json` names Sprint 46's bundle as the validated target. The Sprint 47 bundle was validated in-session but the proof artifact records the wrong path.

## Root Cause

No automated proof generator exists. Proof files are hand-crafted JSON. Nothing enforces that the proof names the current sprint's ZIP.

## Fix Plan (Lane A)

Create `generate_validation_proof()` function that:
1. Takes explicit ZIP path as input
2. Runs `PlannerSprintEvidenceContract.validate_zip()`
3. Computes ZIP SHA256
4. Writes proof JSON with all required fields
5. Enforces proof path matches input path

Add regression tests to prevent recurrence.
