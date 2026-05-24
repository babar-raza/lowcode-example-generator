# Validator Gap Analysis — Sprint 77

**Date:** 2026-05-24
**Purpose:** Identify why Sprint 76 EV/ECC (rules 1-101) allowed S76-C1 through S76-C4 to pass.

---

## Sprint 76 Defects That Passed EV/ECC

### Defect S76-C1 — Untracked output.pptx Omitted from Final Proof

**What passed:** Rule 97 (`final_clean_proof_contains_commit_sha`) — checked that a commit SHA appeared in proof
**What it MISSED:** No rule checked that the final proof enumerated ALL untracked files from `dirty-state-after.txt`
**Gap:** Rule 60 forbids `?? ` in final-clean-proof.txt, but no rule checked that untracked paths from dirty-state-after.txt were properly resolved

**Fix:** Rule 104 (`dirty_state_untracked_acknowledged`) fails if dirty-state-after.txt shows any untracked files.

---

### Defect S76-C2 — final-clean-proof.txt Narrative-Only

**What passed:** Rules 61 (nonzero), 62 (git header present), 97 (commit SHA)
**What it MISSED:** No rule required ACTUAL git command output to be embedded. A narrative like "Sprint bundle scope: clean" passes all three rules but cannot be independently verified.

**Fix:** Rule 103 (`final_clean_proof_has_raw_git_lines`) requires either raw ` M `/`?? ` lines OR "nothing to commit" — actual git output, not narrative prose.

---

### Defect S76-C3 — commands.log Has PENDING Entries

**What passed:** Rule `commands_log_complete` — checks for `IN_PROGRESS` (not `PENDING`)
**What it MISSED:** Sprint 76 used the word `PENDING` instead of `IN_PROGRESS`. The existing rule only blocked `IN_PROGRESS`.

**Fix:** Rule 102 (`commands_log_no_pending`) explicitly rejects `PENDING`.

---

### Defect S76-C4 — Ambiguous Validation Authority

**What passed:** All existing rules — no rule checked whether a `*-validation-result.json` with `overall_valid=false` was properly labeled
**What it MISSED:** `sprint76-bundle-validation-result.json` had `overall_valid=false` (61 non-applicable rule failures) but no `bundle_type` or `canonical_overall_valid` field explaining why.

**Fix:** Rule 105 (`validation_authority_unambiguous`) fails if any non-diagnostic, non-revalidation `*-validation-result.json` has `overall_valid=false` without an explanatory field.

---

## Sprint 77 Rule Additions (102-105)

| Rule # | Rule ID | What It Catches |
|--------|---------|----------------|
| 102 | `commands_log_no_pending` | PENDING entries in commands.log |
| 103 | `final_clean_proof_has_raw_git_lines` | Narrative-only final-clean-proof.txt (no raw git output) |
| 104 | `dirty_state_untracked_acknowledged` | Untracked files in dirty-state-after.txt (must be resolved post-commit) |
| 105 | `validation_authority_unambiguous` | *-validation-result.json with overall_valid=false and no explanatory field |

---

## Sprint 77 Revalidation of Sprint 76

Sprint 76 bundle fails all 4 new rules:
- Rule 102: FAIL (PENDING in commands.log)
- Rule 103: FAIL (narrative-only final-clean-proof.txt)
- Rule 104: FAIL (output.pptx untracked in dirty-state-after.txt)
- Rule 105: FAIL (sprint76-bundle-validation-result.json has overall_valid=false, no explanatory field)

Sprint 77 bundle passes all 105 rules.
