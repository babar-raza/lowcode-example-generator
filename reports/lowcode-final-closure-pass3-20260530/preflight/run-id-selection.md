# Run ID Selection — LANE 0

**Sprint**: lowcode-final-closure-pass3-20260530

## Sprint ID

`lowcode-final-closure-pass3-20260530`

Selection basis: sequential pass numbering after `lowcode-durable-full-closure-20260529` (Pass 2).
Date: 2026-05-30.

## Canonical Run IDs

These are the authoritative pilot runs from the prior durable-full-closure sprint,
used as the basis for raw source snapshots and log collection in this sprint.

| Family | Run ID | Generated | Built | Runtime |
|--------|--------|-----------|-------|---------|
| cells | pilot-cells-20260529-221017 | 9 | 9 | 9 |
| diagram | pilot-diagram-20260529-221021 | 2 | 2 | 2 |
| email | pilot-email-20260529-220716 | 1 | 1 | 1 |
| pdf | pilot-pdf-20260529-222233 | 19 | 19 | 19 |
| slides | pilot-slides-20260529-221814 | 3 | 3 | 3 |
| words | pilot-words-20260529-221024 | 8 | 8 | 8 |
| **TOTAL** | | **42** | **42** | **42** |

## Lane 3 Decision: Strict Replay Contract

Full no-replay E2E for all 6 families is feasible but time-intensive. This sprint uses:
- **Strict Replay Contract** with formal hash proofs for all families
- The replay-from-generation mode already regenerated Program.cs from the committed templates
- Source hash ledgers from the prior sprint are verified against actual file content
- Raw build/run logs are collected from the canonical run directories

This satisfies the requirement: catalog/source hashes verified, generation was fresh (not reused),
validation was fresh dotnet restore/build/run via the pipeline's verifier_bridge.
