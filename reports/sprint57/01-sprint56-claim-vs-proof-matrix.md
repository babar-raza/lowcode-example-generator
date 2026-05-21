# Sprint 56 Claim vs Proof Matrix

**Sprint 57 Phase 0 — Evidence Audit**
**Generated:** 2026-05-21

| # | Sprint 56 Claim | Proof Present? | Proof Type | Classification | Sprint 57 Action |
|---|----------------|---------------|------------|----------------|-----------------|
| 1 | 2815/2815 tests passed | NO | Background task summary only, no log file | UNVERIFIED | Re-run; capture log |
| 2 | 42/42 examples regenerated from scratch | NO | Background task summaries (3 tasks); no ledgers | PARTIALLY_VERIFIED | From-scratch regen with ledgers |
| 3 | 5 FA contract mismatches fixed | YES | Git diff HEAD a8655b7 shows all 5 contract changes | VERIFIED | Full drift scan for additional mismatches |
| 4 | Completion queue 42/42 POST_MERGE_VERIFIED | PARTIAL | 28 have ALL_PASS + merge_sha; 14 have CONTRACT_AUTHORITY only | INVALID_CLAIM (14 entries) | Downgrade 14 → MERGED with real GitHub SHAs |
| 5 | AI/HI matrix repaired | NOT_IN_SPRINT | Carried forward from Sprint 55 | UNVERIFIED_BY_SPRINT56 | Verify via Sprint 57 runs |
| 6 | Version drift current | PARTIAL | NuGet versions current; target repo words/diagram at 26.4.0 | PARTIALLY_VERIFIED | Phase 7 target repo audit |
| 7 | LaneG DEFERRED (target repo audit) | N/A | Explicitly deferred | VALID_DEFERRAL_INVALID_COMPLETE | Phase 7 in Sprint 57 |
| 8 | LaneI DEFERRED (README audit) | N/A | Explicitly deferred | VALID_DEFERRAL_INVALID_COMPLETE | Phase 7 in Sprint 57 |
| 9 | Evidence bundle complete | NO | Bundle contains 2 files; no logs, ledgers, diffs | CONTRADICTED | Sprint 57 creates real bundle |
| 10 | MissingFormatContractError "acceptable risk" | N/A | Code inspection shows silent catch in 4 locations | INVALID_CLAIM | Phase 4: fix to propagate error |
| 11 | 5 new FormatAuthority drift tests added | YES | Git log shows test_scenario_contracts.py modified | VERIFIED | Keep; add more coverage |
| 12 | Test file fixes for CONTRACT_AUTHORITY accepted | YES | Git log confirms test_completion_queue.py modified | VERIFIED (but wrong approach) | Fix tests to reflect MERGED state |
| 13 | Sprint 56 bundle SHA256 correct | CANNOT_VERIFY | Bundle manifest claimed SHA but bundle is defective | UNVERIFIABLE | Sprint 57 produces verified bundle |
| 14 | Denominator confirmed as 42 | PARTIAL | manifest.json shows 42; 2 blocked families (OCR/PSD) not assessed | NEEDS_RECONSTRUCTION | Phase 2: full denominator discovery |

---

## Critical Defects

### Defect D1: CONTRACT_AUTHORITY is not POST_MERGE_VERIFIED

14 PDF entries were promoted from PR_READY → POST_MERGE_VERIFIED via "CONTRACT_AUTHORITY."

**What CONTRACT_AUTHORITY means in the current queue:**
- Local `pipeline/contracts/pdf/*.json` has `publication_status: "MERGED"`
- Notes say "verified via GitHub API in sprint54"

**What POST_MERGE_VERIFIED requires:**
- GitHub API confirms PR is merged (state=closed, merged_at!=null) — GitHub API evidence
- Destination repo content verified: files exist in target repo with correct structure — destination repo proof
- Both are required

**GitHub API check (Sprint 57, real-time):**
| PR | merged_at | merge_commit_sha | Status |
|----|-----------|-----------------|--------|
| #11 | 2026-05-19T05:49:11Z | 20b858958d1df2965893eb305cb9ac418c3ea285 | MERGED |
| #17 | 2026-05-19T05:50:36Z | d793cbec89e2ed7d0a7a868551f9e5824dd332d7 | MERGED |
| #18 | 2026-05-19T05:51:49Z | a26a302ba43204309de52def7b4229bf932bd2c3 | MERGED |
| #19 | 2026-05-19T05:52:09Z | c354f633dec3b39133f813f150956bbbb0304b8c | MERGED |
| #20 | 2026-05-19T05:52:32Z | 3e6cf39a74345e200904cc56681ede1cf8d3631a | MERGED |
| #21 | 2026-05-19T05:52:52Z | 5aa0fa6f485be405f4c23e85162b68f31ec2a9cb | MERGED |

**Correct state:** MERGED (GitHub API confirmed, merge SHAs recorded)
**Destination repo content check:** REQUIRED for POST_MERGE_VERIFIED → Phase 7 Lane G

### Defect D2: Evidence Bundle Contains No Evidence

Bundle format requirement (Sprint 57):
- Minimum 25 meaningful files
- Must include: test logs, command outputs, source diffs, regeneration ledgers

Bundle actuality:
- 2 files (sprint-state.json, bundle-manifest.json)
- No test log
- No regeneration ledger
- No source diff
- No command log

### Defect D3: MissingFormatContractError Silently Swallowed

Locations:
- `src/plugin_examples/scenario_planner/planner.py` lines 451, 565, 605
- `src/plugin_examples/generator/code_generator.py` line 871

All use `except (KeyError, ImportError): pass` which catches MissingFormatContractError (subclass of KeyError) silently.

**Result:** A missing contract causes silent fallback to legacy maps or family_default (`.out`), which may be wrong and only gets caught later at the gate.

**Fix:** Change to `except ImportError:` to let MissingFormatContractError propagate.

### Defect D4: Regeneration "From Scratch" Not Actually From Scratch

Sprint 56 LaneF claims "42/42 regenerated from scratch." The background tasks that confirmed this ran against the same `workspace/runs/` and `workspace/pr-dry-run/` directories from prior sprints. "From scratch" means deleting previous outputs and regenerating. Sprint 57 Phase 6 will do explicit from-scratch regeneration.

### Defect D5: COMPLETE Verdict with Deferred Blocking Lanes

Sprint 56 issued `FORMAT_AUTHORITY_HARDENED_AND_FULL_REGENERATION_COMPLETE` while:
- LaneG (target repo audit) = DEFERRED
- LaneI (README audit) = DEFERRED

These lanes produce blocking evidence that affects publication correctness. A sprint is not COMPLETE while blocking lanes are deferred.

---

## Evidence Present in Sprint 56 (Confirmed)

| Item | Evidence Type | Location | Status |
|------|-------------|----------|--------|
| 5 FA contract fixes | git diff | Confirmed by git diff HEAD a8655b7 | VERIFIED |
| 5 new FA drift tests | git log | tests/unit/test_scenario_contracts.py | VERIFIED |
| Queue CONTRACT_AUTHORITY logic | git log | tests/unit/test_completion_queue.py | VERIFIED (approach wrong) |
| Background task: email 1/1 | task output | tasks/bkr5oumov.output | VERIFIED |
| Background task: words 8/8 | task output | tasks/b6mrlkwwe.output | VERIFIED |
| Background task: pdf 19/19 | task output | tasks/b53d4nd5g.output | VERIFIED |
