Sprint 84 — Live Publication Operator Checklist
=================================================
Date: 2026-05-24
Author: Lane F

## Gate 1: Source Readiness
- [x] 42 examples generated (sprint72 handoff)
- [x] README I/O verified for all 42
- [x] Remote vs handoff: in_sync=true
- [x] PR batching strategy: 1 PR per family (documented)
- [x] Root README conflict strategy: per-family (documented)
- [ ] PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR ← NOT SET

## Gate 2: PR Creation (requires Gate 1)
```bash
# Set approval token:
export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
# Resolve repo access first:
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples resolve-repo-access --families cells words pdf diagram email slides
# Create PRs (1 per family):
for family in email slides diagram cells words pdf; do
  .venv/Scripts/python.exe -c "import os,sys; os.environ['GITHUB_TOKEN']=os.environ['GH_TOKEN']; sys.path.insert(0,'src'); sys.argv=['plugin_examples','publish-pr','--family',\"$family\",'--publish','--approval-token','APPROVE_LIVE_PR','--promote-latest']; from plugin_examples.__main__ import main; main()"
done
```

## Gate 3: PR Merge (requires Gate 2 + maintainer review)
- [ ] PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR ← NOT SET
```bash
# After CI passes and maintainer approves:
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr --family email --pr-number <N> --merge --approval-token APPROVE_MERGE_PR
# Repeat for slides, diagram, cells, words, pdf in order
```

## Gate 4: Post-Merge Verification
- [ ] Verify 42 READMEs present on remote
- [ ] Run email/slides runtime smoke test
- [ ] Update publication-truth-matrix
- [ ] Run release-status

## Current Status
GATE_1_PARTIAL (all conditions met EXCEPT approval token)
Action needed: Set PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR to proceed.
