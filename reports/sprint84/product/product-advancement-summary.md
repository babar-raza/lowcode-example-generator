Sprint 84 — Product Advancement Summary
=========================================
Date: 2026-05-24
Author: Lane F

## Product State

### Publication Readiness
- 42 examples with README I/O: READY (pending approval)
- 6 families with sprint72 handoff: STABLE
- Publication blocked: PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=NOT_SET

### Governance Maturity
- EV rules: 119 (Sprint 84 adds 4 new PR lifecycle rules)
- ECC categories: 59 (Sprint 84 adds 9 new categories)
- Test suite: 167 tests
- PR batching strategy: FORMALIZED (1 PR per family default)
- Root README strategy: FORMALIZED (per-family, explicit rationale)

### Sprint 84 Advancements
1. **PR Batching Governance**: First sprint with formally documented PR batching strategy.
   Prevents the Sprint 83 S83-C1 caveat (42-PR noise) from recurring.
2. **Root README Governance**: First sprint with per-family root README strategy.
   Resolves S83-C2 ambiguity in Sprint 83.
3. **Stale Label Cleanup**: Sprint 83 taskcard stale labels normalized.
   Resolves S83-C3 from Sprint 83.
4. **EV Hardening**: 4 new EV rules enforce PR lifecycle governance going forward.

### Carry-Forward Items
- FormImporter: BLOCKED_EXTERNAL (Aspose.PDF 26.5.0 bug). Wave H deferred.
- Words version drift: 26.4.0 remote vs 26.5.0 handoff. Bundled in PR #7 (unmerged).
- Open root-README PRs: cells#5, words#7, diagram#2. Independent of sprint84 PRs.
- Sprint 27 governance exception: PRE_CONTRACT_ERA_BUNDLE (grandfathered).

### Next Milestone
Sprint 85: Execute live publication when approval gates are lifted.
All pre-publication conditions met as of Sprint 84.
