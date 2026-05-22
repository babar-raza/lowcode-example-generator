# Next Action Planner Report — Sprint 43

## Implementation

- **Module**: `src/plugin_examples/portfolio_action_planner.py`
- **Tests**: `tests/unit/test_portfolio_action_planner.py` (26 tests, all PASS)
- **CLI**: `python -m plugin_examples next-actions [--output PATH] [--markdown PATH] [--json]`
- **Commit**: f6a9376

## Features

1. Reads denominators, contracts, configs, dirty state, approval gates
2. Produces ranked JSON action board sorted by impact
3. Renders human-readable markdown
4. Dirty state = highest priority (impact 100)
5. PDF merge = first when gate present, blocked when absent
6. OCR/PSD/FormImporter visible as blocker retests
7. Permanently blocked roots visible
8. No silent drop — all families represented

## Test Coverage

- Action model serialization and roundtrip
- Gate-dependent behavior (approval present/absent via mock)
- Dirty state ranking (first position via mock)
- Contract conservation feed (no backfill when contracts match pilot)
- Markdown rendering
- Constants (family counts, blocked roots)
