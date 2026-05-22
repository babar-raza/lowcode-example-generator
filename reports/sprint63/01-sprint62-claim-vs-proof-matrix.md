# Sprint 62 Claim vs. Proof Matrix

**Sprint:** 63
**Subject:** Sprint 62 claims
**Date:** 2026-05-22

Status codes:
- VERIFIED — claim is proven by evidence in the bundle
- PARTIALLY_VERIFIED — some evidence exists but not fully proven
- CONTRADICTED — evidence contradicts the claim
- INVALID_CLOSURE — claim is false and blocks sprint closure
- REPAIRED_IN_SPRINT63 — will be corrected in Sprint 63
- CARRIED_FORWARD_WITH_TASKCARD — tracked but not repaired this sprint

---

## Claim 1: SPRINT62_COMPLETE verdict

**Status: CONTRADICTED / INVALID_CLOSURE**

The verdict name claims COMPLETE. But:
- Evidence contract has 31/37 PENDING categories — contract says PENDING=INVALID_CLOSURE
- Validator result is internally self-contradictory
- Publication did not occur (body correctly notes BLOCKED_BY_APPROVAL, but verdict name says COMPLETE)
- Dry-run packages not in evidence bundle

**Repair:** REPAIRED_IN_SPRINT63 — downgraded to truthful status.

---

## Claim 2: 42/42 README correction ledger

**Status: PARTIALLY_VERIFIED**

Evidence:
- `readme-corrections/example-readme-update-ledger.json` exists and has 42 entries
- Each entry has correction text with authority-derived I/O descriptions

Not proven:
- Correction text was not applied to actual README files in destination repos
- No diff between current README content and proposed correction
- Dry-run packages not verified to contain updated READMEs

**Repair:** REPAIRED_IN_SPRINT63 — Phase 3 includes actual README diffs from dry-run packages.

---

## Claim 3: 6/6 destination package ledger

**Status: PARTIALLY_VERIFIED**

Evidence:
- `destination-packages/package-ledger.json` exists with 6 entries
- Per-family markdown files exist in `destination-packages/per-family/`

Not proven:
- Actual package files are not in the evidence bundle
- Package contents cannot be audited from bundle alone

**Repair:** REPAIRED_IN_SPRINT63 — Phase 3 includes package artifact index and per-family content manifests.

---

## Claim 4: Actual destination PR package presence in bundle

**Status: MISSING**

Evidence: None. All packages are in `workspace/pr-dry-run/` which is gitignored.

**Repair:** REPAIRED_IN_SPRINT63 — Phase 3 creates package artifact index with file lists and hashes.

---

## Claim 5: Evidence contract status

**Status: CONTRADICTED / INVALID_CLOSURE**

Evidence: Contract file exists but 31/37 categories are PENDING.
Contract says PENDING=INVALID_CLOSURE.
No process computed or updated statuses after file creation.

**Repair:** REPAIRED_IN_SPRINT63 — Phase 1 adds computed status generation.

---

## Claim 6: Bundle validation status (overall_valid=true)

**Status: CONTRADICTED**

Evidence: `evidence/sprint62-bundle-validation-result.json` says `overall_valid=true`, `failed=0`.
But the rules array inside it contains `bundle_validation_result_present_and_valid` with `passed=false`.
The note field admits `pre_bootstrap_failed=1`.

The stored result was manually overridden, not produced by an honest EV run.

**Repair:** REPAIRED_IN_SPRINT63 — Phase 2 fixes bootstrap logic; Sprint 63 result will be produced by two-phase validation.

---

## Claim 7: Validator self-consistency

**Status: CONTRADICTED**

Evidence: See Claim 6. A result cannot claim `failed=0` while containing a `passed=false` rule.
The EV aggregation code is correct; the problem is the manual bootstrap override.

**Repair:** REPAIRED_IN_SPRINT63 — Phase 2 adds two-phase validation and tests.

---

## Claim 8: Final clean proof

**Status: PARTIALLY_VERIFIED**

Evidence:
- `git/final-clean-proof.txt` exists, nonzero, contains "nothing to commit, working tree clean"
- Captured after the first Sprint 62 commit

Concern:
- The clean proof was captured BEFORE the bootstrap bundle validation result was written
- Sprint 62 had two commits: the main commit, then `9810a1a` adding the clean proof + EV result + manifest
- The clean proof captured at time of writing shows clean state for the first commit, not the final commit

**Status: PARTIALLY_VERIFIED** — the file is valid but represents an intermediate state.

---

## Claim 9: Special-case I/O closure

**Status: VERIFIED**

Evidence:
- `io-special/special-case-authority.json` — 9 cases, all RESOLVED, with explicit authority sources
- `io-special/programcs-special-case-repair.json` — 5 repairs documented
- `io-special/readme-special-case-text.md` — 4 README special-case texts
- Authority verified from actual Program.cs files in workspace/runs/

No overclaim. Special cases documented with source paths and classification.

---

## Claim 10: Package authority (api_verified=CONFIRMED_FROM_PROGRAMCS)

**Status: CONTRADICTED**

Evidence: `package-authority/api-verification-ledger.json` sets `api_verified="CONFIRMED_FROM_PROGRAMCS"` for all 42.
The Sprint 62 summary calls this "package API authority".

This is incorrect. Program.cs usage:
- Proves generated code calls the API
- Does NOT prove the NuGet package contains the API member
- Does NOT prove signature, version, or documentation match

Correct label: `programcs_api_usage_verified=true`.

**Repair:** REPAIRED_IN_SPRINT63 — Phase 5 corrects labelling.

---

## Claim 11: Publication status (BLOCKED_BY_APPROVAL)

**Status: VERIFIED**

Evidence:
- `publication/live-approval-check.md` — correctly identifies all 4 missing approval tokens
- `publication/live-publication-result.json` — correctly says BLOCKED_BY_APPROVAL
- No GitHub API calls made, no remote mutation

---

## Claim 12: Version drift status

**Status: PARTIALLY_VERIFIED**

Evidence:
- `version-drift/words-version-drift.md` and `diagram-version-drift.md` exist
- Claim that dry-run Directory.Packages.props already at 26.5.0

Concern: The evidence does not include a diff showing the before/after change. The claim is
asserted but not proven via diff from destination repo.

---

## Claim 13: Dry-run package status

**Status: PARTIALLY_VERIFIED**

Evidence: Package ledger JSON files exist, describe 6 families.
Not proven: Actual package files (Program.cs, README.md) not in bundle.

**Repair:** REPAIRED_IN_SPRINT63 — Phase 3.

---

## Claim 14: Live approval blockers

**Status: VERIFIED**

Evidence: Approval check correctly identifies all required tokens and confirms none are set.
No secrets printed. No unauthorized mutation.

---

## Summary

| # | Claim | Status | Sprint 63 Action |
|---|-------|--------|-----------------|
| 1 | SPRINT62_COMPLETE verdict | INVALID_CLOSURE | Downgrade |
| 2 | 42/42 README corrections | PARTIALLY_VERIFIED | Phase 3 |
| 3 | 6/6 destination ledger | PARTIALLY_VERIFIED | Phase 3 |
| 4 | Actual package presence | MISSING | Phase 3 |
| 5 | Evidence contract status | INVALID_CLOSURE | Phase 1 |
| 6 | Bundle validation status | CONTRADICTED | Phase 2 |
| 7 | Validator self-consistency | CONTRADICTED | Phase 2 |
| 8 | Final clean proof | PARTIALLY_VERIFIED | Accepted |
| 9 | Special-case I/O closure | VERIFIED | Carried forward |
| 10 | Package authority | CONTRADICTED | Phase 5 |
| 11 | Publication status | VERIFIED | Carried forward |
| 12 | Version drift status | PARTIALLY_VERIFIED | Phase 3 |
| 13 | Dry-run package status | PARTIALLY_VERIFIED | Phase 3 |
| 14 | Live approval blockers | VERIFIED | Carried forward |
