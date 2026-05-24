Sprint 84 — Validator Gap Analysis
=====================================
Date: 2026-05-24
Author: Lane G

## Sprint 83 Gaps Identified (S83-C1 and S83-C2)

### Gap G1: No rule enforcing PR batching strategy documentation
Sprint 83 caveats identified that a 42-PR bulk plan was created without any documented
batching strategy. The validator had no rule requiring pr-batching-strategy.md before
PR creation.

Closed by: Rule 116 `pr_batching_strategy_present_if_pr_creation_attempted`

### Gap G2: No rule enforcing PR batching plan documentation
Pairs with G1 — the structured JSON plan (pr-batching-plan.json) was also undocumented.

Closed by: Rule 117 `pr_batching_plan_present_if_pr_creation_attempted`

### Gap G3: No rule enforcing root README file plan before PR creation
Sprint 83 excluded root READMEs for cells/words/diagram with a global strategy, but
did not require a per-family file plan documenting exactly which files go in each PR.

Closed by: Rule 118 `root_readme_file_plan_present_before_pr_creation`

### Gap G4: No rule preventing bulk 42-PR plan without justification
The default is 1 PR per family (6 PRs). Sprint 83 accidentally planned 42 PRs.
No rule caught this.

Closed by: Rule 119 `no_bulk_42pr_plan_without_justification`

## Rules Added This Sprint

| Rule ID | Name | Rule # | Closes |
|---------|------|--------|--------|
| pr_batching_strategy_present_if_pr_creation_attempted | Strategy doc required before PR creation | 116 | S83-G1 |
| pr_batching_plan_present_if_pr_creation_attempted | Plan JSON required before PR creation | 117 | S83-G2 |
| root_readme_file_plan_present_before_pr_creation | Root README file plan required before PR creation | 118 | S83-G3 |
| no_bulk_42pr_plan_without_justification | 42-PR bulk plan requires bulk_justification | 119 | S83-G4 |

## Rule Count
- Sprint 83: 115 rules
- Sprint 84: 119 rules (+4)

## Test Count
- Sprint 83: 163 tests
- Sprint 84: 167 tests (+4 in TestSprint84ValidatorHardeningRules)

## No Further Gaps Identified
All Sprint 83 caveats (C1-C4) are now closed:
- C1 (PR batching): Closed by rules 116-119 + Lane B documentation
- C2 (root README): Closed by rule 118 + Lane C documentation
- C3 (stale labels): Closed by Lane H + Lane I (non-validator fix)
- C4 (approval gate): By design — blocked, no validator action needed
