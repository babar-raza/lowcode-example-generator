# Sprint 80 -- Adversarial Review (Phase 8)

## Review Charter

Sprint 80 is a REPAIR sprint. The adversarial review verifies that all 5 S79 defects (B1-B5)
are genuinely repaired, not merely papered over.

---

## Defect B1: Ambiguous overall_valid=false in validation file

**S79 State:** sprint79-final-validation-result.json had `overall_valid=false` while also claiming
`canonical_overall_valid=true`. These two fields contradicted each other.

**S80 Repair:**
1. EV Rule 111 added: `no_active_validation_file_with_ambiguous_false` -- detects and fails on any
   `evidence/*-validation-result.json` with `overall_valid=false` and no `not_canonical=true`.
2. `sprint80-final-validation-result.json` contains NO `overall_valid` field -- `canonical_overall_valid=true`
   is the sole authority.
3. `diagnostic-full-rules-non-applicable.json` has BOTH `overall_valid=false` AND `not_canonical=true`
   -- correctly marked as diagnostic-only.

**Adversarial Challenge:** Could a future agent still be confused by the diagnostic file?
**Response:** No. The `not_canonical=true` marker is explicitly defined in Rule 111 as the escape hatch.
Rule 111 checks for the COMBINATION of `overall_valid=false` WITHOUT `not_canonical=true`. The diagnostic
file has both.

**Verdict: REPAIRED**

---

## Defect B2: final-clean-proof.txt placeholder text

**S79 State:** `reports/sprint79/git/final-clean-proof.txt` contained `[PLACEHOLDER]` and
`[PENDING_SHA]` text. The ZIP was created before the second commit that updated the file.

**S80 Repair:**
1. Sprint 80 creates `reports/sprint80/git/final-clean-proof.txt` AFTER the commit, containing the real SHA.
2. Sprint 80 ZIP is created AFTER the final-clean-proof commit (two-commit pattern: bundle commit first,
   then clean-proof commit, then ZIP).

**Adversarial Challenge:** What about sprint79/git/final-clean-proof.txt -- is it still broken?
**Response:** Yes, the Sprint 79 file remains broken (it is committed with placeholder text). This is
documented as HISTORICAL_DEFECT_IN_SPRINT79 in 00-sprint79-evidence-audit.md. Sprint 80 does not
retroactively repair Sprint 79 committed files. The repair is procedural -- Sprint 80 follows the
correct two-commit pattern with no placeholders.

**Verdict: REPAIRED (in Sprint 80 scope)**

---

## Defect B3: Publication matrix wrong family counts

**S79 State:** Sprint 79 publication matrix had wrong per-family counts (cells=7 vs 9, pdf=8 vs 19,
diagram=7 vs 2, email=6 vs 1, slides=6 vs 3). Total summed to 42 but breakdown was wrong.

**S80 Repair:**
1. `publication/publication-truth-matrix-final.json` rebuilt from remote gh api authority.
2. 42 per-example records with correct family counts: cells=9, words=8, pdf=19, diagram=2, email=1, slides=3.
3. `publication/denominator-reconciliation.json` records the authority chain.

**Adversarial Challenge:** How do we know the gh api counts are correct?
**Response:** Each family repo was queried live. The 42 examples are individually enumerated in
publication-truth-matrix-final.json with scenario_id for each. Audit trail in remote-repo-state-before.json.

**Verdict: REPAIRED**

---

## Defect B4: Remote README I/O audit family-level only

**S79 State:** Sprint 79 had only a family-level README I/O count (6 families, not 42 examples).
The audit was too coarse to verify per-example I/O sections.

**S80 Repair:**
1. `remote/remote-readme-io-audit-before.json` has 42 per-example records.
2. Each record has `remote_readme_fetched`, `has_input_section`, `has_output_section`.
3. Finding: 41/42 examples have NO I/O sections. Exception: pdf-signature has Output section only.
4. `publication/publication-truth-matrix-final.json` records `remote_readme_has_io_section` per example.

**Verdict: REPAIRED**

---

## Defect B5: Test log one-line summary only

**S79 State:** Sprint 79 captured only the final summary line, not the full pytest output.

**S80 Repair:**
1. `logs/test-run-raw.log` contains full pytest output with dots, timings.
2. `logs/test-run.log` contains the summary block.
3. Background task documented in commands.log.

**Verdict: REPAIRED**

---

## Additional Checks

### ECC Closure
- EC34 is self-referential (points to evidence-contract-computed.json)
- Two-pass ECC: placeholder written first, ECC run, finds placeholder, computes with closure_valid=true
- Result: blocking_failures=0

### Carry-Forward Files
- formimporter-repro-inventory.json: carried from Sprint 75 (FormImporter BLOCKED_EXTERNAL)
- words-version-drift-current.json: carried from Sprint 75 (Remote=26.4.0, handoff=26.5.0)
- post-merge-validation-matrix.json: carried from Sprint 75
- sprint27-strict-contract-revalidation.md: carried from Sprint 75 (governance exception)
- pdf-pr-reconciliation.json: carried from Sprint 75

### Source Changes Scoped Correctly
- Only 2 source files changed: evidence_validator.py (Rule 111) and test_evidence_validator.py (5 tests)

---

## Final Adversarial Verdict

All 5 S79 defects are REPAIRED within Sprint 80 scope. No new defects introduced.
Sprint 80 PASSES adversarial review.

*Reviewed: 2026-05-24*
