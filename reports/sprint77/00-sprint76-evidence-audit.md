# Sprint 76 Evidence Audit — Sprint 77

**Date:** 2026-05-24
**Purpose:** Identify evidence consistency gaps in Sprint 76 that prevent full closure acceptance.

---

## Sprint 76 Technical Progress (ACCEPTED)

The following Sprint 76 technical work is accepted and carries forward:

1. **Slides Compress runtime validation** — VERIFIED. Real `input.pptx` (34,242 bytes), `output.pptx` produced (19,807 bytes, 42.2% compression). `dotnet restore/build/run` all exit 0. `post_merge_validated=true`, `output_confirmed=true`.
2. **Post-merge validation matrix** — VERIFIED. All 4 Email/Slides examples runtime validated.
3. **S75-B1 repair** — VERIFIED. Slides Compress overclaim corrected.
4. **S75-B2 repair** — VERIFIED. Dirty-state contradiction documented.
5. **8 new EV rules (94-101)** — VERIFIED. All 3052 tests pass.

---

## Sprint 76 Evidence Consistency Blockers

### Blocker S76-C1 — Untracked `output.pptx` Omitted from Final Proof

**What happened:** `dotnet run` produced `reports/sprint75/handoff/per-family/slides/compress/output.pptx` as runtime output. This file remained untracked in the working tree after the Sprint 76 bundle commit.

**What was documented:** `reports/sprint76/git/dirty-state-after.txt` correctly shows:
```
?? reports/sprint75/handoff/per-family/slides/compress/output.pptx
```

**What was missing:** `final-clean-proof.txt` and `final-verdict.md` acknowledge only 7 `workspace/verification/latest/` dirty files. The untracked `output.pptx` is silently omitted from the final exception accounting.

**Impact:** Final verdict says "only workspace/latest files remain dirty" — this is FALSE. An untracked file also exists.

**Fix in Sprint 77:** Option B — copy `output.pptx` to `reports/sprint77/post-merge-runtime/artifacts/` (committed as bundle artifact), then remove the original untracked file. Sprint 77 dirty-state-after.txt will show no untracked files.

---

### Blocker S76-C2 — `final-clean-proof.txt` is Narrative-Only

**What happened:** Sprint 76 `final-clean-proof.txt` contains only narrative text:
```
On branch main
Sprint 76 bundle committed: 47c584d
reports/sprint76/ -- 39 files added...
```

**What was missing:** No raw `git status --short` or `git status` output embedded. A reviewer cannot verify the final state from this file alone.

**Fix in Sprint 77:** `final-clean-proof.txt` must include raw `git status --short` and `git status` output embedded within it.

---

### Blocker S76-C3 — `commands.log` Has `PENDING` Entries

**What happened:** Sprint 76 `commands.log` has two entries with `Exit: PENDING`:
```
[Phase 4] EV hardening
  CMD: ...pytest tests/unit/ -q --tb=short
  Exit: PENDING

[Phase 6] Full test suite
  CMD: ...pytest tests/ -q --tb=short
  Exit: PENDING
```

**Impact:** A log with `PENDING` entries is not a closed log. Rule `commands_log_complete` checks for `IN_PROGRESS` (which Sprint 76 did not use), but the spirit of the rule clearly requires no unresolved entries.

**Fix in Sprint 77:** New EV Rule 102 (`commands_log_no_pending`) explicitly prohibits `PENDING` in commands.log. Sprint 77 commands.log is written fresh with all entries complete.

---

### Blocker S76-C4 — Validation Authority Ambiguity

**What happened:** Two validation result files exist in Sprint 76 evidence/:

1. `sprint76-final-validation-result.json`: `overall_valid: true` (17 applicable rules pass)
2. `sprint76-bundle-validation-result.json`: `overall_valid: false` (39/100 pass, 61 non-applicable)

A reader seeing the second file (which lacks a `bundle_type` or `canonical_overall_valid` field explaining the failures) would incorrectly conclude the bundle failed validation.

**Fix in Sprint 77:** New EV Rule 105 (`validation_authority_unambiguous`) requires that any `*-validation-result.json` with `overall_valid: false` must have either `bundle_type: REPAIR_BUNDLE` OR `canonical_overall_valid` field. Sprint 77 introduces `diagnostic-full-rules-non-applicable.json` for the full-rule diagnostic run.

---

## Sprint 76 Revalidation Under Sprint 77 Rules

Sprint 76 bundle fails 4 of 4 new Sprint 77 rules:
- Rule 102 (`commands_log_no_pending`): FAIL — `PENDING` entries in commands.log
- Rule 103 (`final_clean_proof_has_raw_git_lines`): FAIL — no raw git status lines in proof
- Rule 104 (`dirty_state_untracked_acknowledged`): FAIL — output.pptx untracked, not in final-verdict.md
- Rule 105 (`validation_authority_unambiguous`): FAIL — sprint76-bundle-validation-result.json has overall_valid=false, no canonical_overall_valid field

Sprint 76 passes rules 1-101 (existing rules).
