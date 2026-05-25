Sprint 86 — Operator Command Sheet
====================================
Date: 2026-05-25

## Purpose
This document provides the exact commands to unfreeze publication and create
README I/O PRs. No further readiness proof is needed — the baseline is frozen
at Sprint 85 state (42/42 remote, 0/42 README I/O, all validation passing).

## Step 1: Set Approval Gate
```bash
# In your shell session (or add to system environment variables):
export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
```

## Step 2: Run Publication Sprint
The next sprint after approval is set will:
1. Detect APPROVE_LIVE_PR gate
2. Create 6 README I/O PRs (1 per family: cells, words, pdf, diagram, email, slides)
3. Each PR updates example READMEs with Input/Output sections from sprint72/handoff/per-family/
4. Root README PRs excluded (cells#5, words#7, diagram#2 already open)

## Step 3: Merge (requires separate approval)
```bash
export PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH
```

## Prerequisites Already Met
- 42/42 remote examples accessible (verified Sprint 85)
- 42/42 handoff READMEs have I/O sections (verified Sprint 81)
- Format authority contracts: 42/42 api_verified
- Evidence validator: 124 rules, 182 tests, all passing
- Full test suite: 3123 pass, 0 fail
- FormImporter: BLOCKED_EXTERNAL (Aspose.PDF 26.5.0 bug — does not affect other families)
- Words version drift: 26.4.0→26.5.0 bump bundled with README I/O PR

## What Will NOT Happen Without Approval
- No PRs will be created
- No code will be pushed to remote repositories
- No branches will be modified
- The pipeline will continue to report APPROVAL_BLOCKED
