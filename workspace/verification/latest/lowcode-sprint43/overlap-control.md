# Overlap Control — Sprint 43

## Principle
Each lane owns its files exclusively. No lane modifies files owned by another.

## File Ownership

| File/Area | Owner Lane |
|-----------|-----------|
| pipeline/contracts/ | D (portfolio) |
| tests/unit/test_scenario_contracts.py | D |
| tests/unit/test_portfolio_action_planner.py | A |
| src/plugin_examples/portfolio_action_planner.py | A |
| pipeline/configs/denominators/ | D |
| workspace/verification/latest/lowcode-sprint43/ | G (evidence) |
| PDF PR state | B |
| AI governance tests | F |

## Conflict Resolution
If two lanes need the same file, the lower-numbered lane commits first.
