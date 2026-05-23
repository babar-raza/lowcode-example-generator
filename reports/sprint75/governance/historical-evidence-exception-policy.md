# Historical Evidence Exception Policy

**Version:** 1.0
**Created:** 2026-05-23 (Sprint 75)
**Applies to:** All evidence bundles from before sprint57

## Policy Statement

Evidence bundles from the pre-sprint57 era (sprint1 through sprint56 plus associated workspace
verification artifacts) are subject to a Historical Evidence Exception when evaluated against
the current EvidenceValidator + EvidenceContractComputer (EV/ECC) system.

## Rationale

The EV/ECC system was introduced in Sprint 61 and progressively hardened through Sprint 75.
Earlier sprints used different evidence structures:
- Sprints 1-26: Ad-hoc lane-based evidence in `workspace/verification/`
- Sprints 27-56: StrictEvidenceContract V1-V5 in `workspace/verification/sprint{N}/`
- Sprints 57+: PlannerSprintEvidenceContract in `reports/sprint{N}/` with EV/ECC validation

It is not feasible or meaningful to retroactively apply EV/ECC rules to pre-sprint57 bundles.

## Exception Classifications

### PRE_CONTRACT_ERA_BUNDLE (Sprints 1-27)
- Bundles predate any formal evidence contract.
- No validation possible.
- Historical compliance status: AS-DOCUMENTED.
- Example: Sprint 27 — HISTORICAL_NON_COMPLIANT (17 missing categories, documented in Sprint 28).

### STRICT_CONTRACT_ERA_BUNDLE (Sprints 28-56)
- Bundles used StrictEvidenceContract V1-V5.
- Validated against their contemporaneous contract.
- Downstream compliance: Sprints 28-32 verified compliant with V1-V5.
- No retroactive EV/ECC validation.

## Rules for Current EV/ECC System

1. EV/ECC validates ONLY `reports/sprint{N}/` bundles (sprint57 and later).
2. EV/ECC rules do NOT apply to `workspace/verification/sprint{N}/` bundles.
3. Final verdicts for sprint57+ must NOT cite pre-sprint57 bundles as fully compliant without
   this exception annotation.
4. If a sprint57+ report references a pre-sprint57 bundle as an authority source, it must
   include: "Note: pre-sprint57 bundle — Historical Evidence Exception Policy applies."

## Sprint 27 Specific Entry

| Field | Value |
|-------|-------|
| Sprint | 27 |
| Commit | 774f516084ff55e0701bf14feb90846cdce129c8 |
| Classification | HISTORICAL_NON_COMPLIANT |
| Failure documented | Sprint 28, commit 20686d3, Lane 0 |
| Missing categories | 17 (see sprint27-missing-categories.json) |
| Partial reconstruction | Sprint 28 Lane B — 11/17 artifacts reconstructed |
| Best-effort complete | YES (Sprint 28 is the canonical record) |
| Future action | None — grandfathered |

## Governance Notes

- This policy does not retroactively invalidate published examples (the 42 published examples
  were validated through the current EV/ECC system in sprints 57-75).
- The policy applies only to the evidence/compliance classification of old sprint bundles.
- No new sprints should reference pre-sprint57 evidence as primary authority for publication
  decisions.
