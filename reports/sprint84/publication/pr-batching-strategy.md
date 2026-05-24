Sprint 84 — PR Batching Strategy
==================================
Date: 2026-05-24
Author: Lane B

## Decision: 1 PR Per Family (DEFAULT)

### Rationale
Sprint 83 S83-C1 identified that a 42-PR plan (1 per example) is too noisy:
- 42 open PRs make review and merge tracking unmanageable
- GitHub notification volume overwhelming for maintainers
- Atomic merge guarantees harder to reason about across 42 branches
- Post-merge verification must be done 42 times vs 6 times

### Adopted Strategy: FAMILY_BATCH_PR

Each PR contains ALL example READMEs for one family in a single branch:
- cells: up to 9 example READMEs
- words: up to 8 example READMEs
- pdf: up to 19 example READMEs
- diagram: up to 2 example READMEs
- email: 1 example README
- slides: up to 3 example READMEs

Total: 6 PRs (one per family).

### Root README Handling
Root READMEs are NOT included in family batch PRs (deconflict with open PRs cells#5, words#7, diagram#2).
See conflicts/root-readme-file-plan.json for per-family root README strategy.
For families without open root-README PRs (pdf, email, slides): root README MAY be included in
family batch PR if root README change is needed; this sprint no root README changes are required.

### Exception Conditions (when split IS allowed)
1. Open root-README conflict that cannot be resolved before PR creation → exclude root README,
   proceed with example-only batch.
2. PR diff > 500 files → split at sub-family level (unlikely; max 19 files for pdf).
3. CI gate specific to one example fails → that example may be deferred to a follow-up PR.

No exceptions apply this sprint. 1 PR per family = 6 PRs total.

### Branch Naming Convention
  lowcode-examples-{family}-{sprint_id}
  e.g. lowcode-examples-cells-sprint84

### Merge Order
Recommended: email → slides → diagram → cells → words → pdf
(smallest first, least conflict risk first, largest last)

## Status
Sprint 84 publication is APPROVAL_BLOCKED. This strategy is documented for next approved sprint.
PR creation: 0/6. PRs exist: 0.
