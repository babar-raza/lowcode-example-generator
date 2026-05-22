# Conservation Check Report — Sprint 42

Generated: 2026-05-19

## Per-Family Conservation Equations

### Cells
- `workflow_roots + non_runnable = total`: 9 + 13 = 22 PASS
- `published + pending + blocked = pilot`: 9 + 0 + 0 = 9 PASS
- `contracts = pilot_allowed`: 9 = 9 PASS

### Words
- `workflow_roots + non_runnable = total`: 9 + 16 = 25 PASS
- `published + pending + blocked = pilot`: 8 + 0 + 0 = 8 PASS
- `contracts = pilot_allowed`: 8 = 8 PASS
- Note: Processor (1 root) permanently blocked, excluded from pilot

### PDF
- `workflow_roots + non_runnable = total`: 22 + 79 = 101 PASS
- `published + pr_ready = pilot`: 5 + 14 = 19 PASS
- `contracts = pilot_allowed`: 19 = 19 PASS
- Note: 3 roots outside pilot (Timestamp, Ofd: BLOCKED; FormImporter: DEFERRED)

### Diagram
- `workflow_roots + non_runnable = total`: 2 + 3 = 5 PASS
- `published + pending + blocked = pilot`: 2 + 0 + 0 = 2 PASS
- `contracts = pilot_allowed`: 2 = 2 PASS

### Email
- `workflow_roots + non_runnable = total`: 1 + 2 = 3 PASS
- `published + pending + blocked = pilot`: 1 + 0 + 0 = 1 PASS
- `contracts = pilot_allowed`: 1 = 1 PASS

### Slides
- `workflow_roots + non_runnable = total`: 3 + 2 = 5 PASS
- `published + pending + blocked = pilot`: 3 + 0 + 0 = 3 PASS
- `contracts = pilot_allowed`: 3 = 3 PASS

## Cross-Family Totals

| Check | Value | Status |
|-------|-------|--------|
| Total pilot allowed | 42 | — |
| Total contracts | 42 | — |
| Total published | 28 | — |
| Total PR ready | 14 | — |
| contracts = pilot_allowed | 42 = 42 | PASS |
| published + pr_ready = contracts | 28 + 14 = 42 | PASS |

## Silent Drop Check

**Result: PASS** — No planned runnable example silently dropped. All 42 pilot-allowed scenarios have pipeline contracts.
