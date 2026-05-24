# Live Publication Operator Checklist — Sprint 83

## Pre-Publication Gate

Before running `publish-pr --publish`, confirm ALL items below:

### Environment
- [ ] `GH_TOKEN` set to valid classic PAT (ghp_*) with repo scope
- [ ] PAT is classic (NOT fine-grained — fine-grained PATs cannot push to org repos)
- [ ] `resolve-repo-access --families cells words pdf diagram email slides` run this session

### Approval Gates
- [ ] `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` set
- [ ] Operator has reviewed and accepted Sprint 83 publication file plan (42 examples, 0 root READMEs)

### Conflict Deconflict
- [ ] Confirmed strategy: Sprint 83 PRs target `examples/{family}/lowcode/{example}/README.md` ONLY
- [ ] Root README PRs cells#5, words#7, diagram#2 remain untouched

### Handoff Integrity
- [ ] Sprint 72 handoff at `reports/sprint72/handoff/` is intact (42/42 examples)
- [ ] Words version 26.5.0 matches remote — no drift

### Publication Scope
- [ ] All 6 families: cells (9), words (8), pdf (19), diagram (2), email (1), slides (3)
- [ ] FormImporter excluded (BLOCKED_EXTERNAL)
- [ ] publication-file-plan.json created and confirmed

## Post-Publication Verification

After PRs are created:
- [ ] Run `release-status --promote-latest` — confirm all 42 PRs listed
- [ ] Per-family PR URLs captured in `pr-creation-ledger.json`
- [ ] `publication-truth-matrix-final.json` updated with real `pr_url` values

## Merge Gate

Requires separate `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR`:
- [ ] PR reviews complete (no required reviewers on org repos, but verify)
- [ ] All CI checks pass (or no CI configured)
- [ ] Run `merge-pr --family {family} --pr-number N --merge --approval-token APPROVE_MERGE_PR` per family

## Current Gate Status

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`: **NOT_SET** — publication blocked.

---
*Lane D — Sprint 83 — 2026-05-24*
