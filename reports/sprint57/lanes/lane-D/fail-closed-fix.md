# Lane D: Fail-Closed Fix — MissingFormatContractError

**Sprint 57 Phase 4a**
**Applied:** 2026-05-21

## Problem

`MissingFormatContractError` is a subclass of `KeyError` (defined in `src/plugin_examples/format_authority/store.py` line 32).

In 4 locations, the code used `except (KeyError, ImportError): pass` which silently caught `MissingFormatContractError` and fell back to legacy maps or family defaults.

## Locations Fixed

| File | Line | Old Handler | New Handler |
|------|------|-------------|-------------|
| `src/plugin_examples/scenario_planner/planner.py` | ~451 | `except (KeyError, ImportError)` | `except ImportError` |
| `src/plugin_examples/scenario_planner/planner.py` | ~565 | `except (KeyError, ImportError)` | `except ImportError` |
| `src/plugin_examples/scenario_planner/planner.py` | ~607 | `except (KeyError, ImportError)` | `except ImportError` |
| `src/plugin_examples/generator/code_generator.py` | ~871 | `except (KeyError, ImportError)` | `except ImportError` |

## Behavior Change

**Before:** Missing contract → silent KeyError catch → fallback to legacy map or `.out` → gate catches `.out` at the end
**After:** Missing contract → `MissingFormatContractError` propagates → caller handles explicitly → fail-closed at format resolution stage

## Risk Assessment

- All 42 active types have FA contracts (confirmed by drift scan)
- The `ImportError` catch remains (handles environments without FA module installed)
- For production active examples: no behavioral change (all have contracts)
- For new types without contracts: immediate clear error instead of silent fallback

## Test Coverage

The existing `test_format_authority_no_stale_maps.py` (181 tests) verifies all 42 contracts exist.
The new FA drift tests in `test_scenario_contracts.py` (5 tests) verify specific contract values.

## Verification

```python
# Verify the fix raises MissingFormatContractError for missing type
from plugin_examples.format_authority.store import get_contract, MissingFormatContractError
try:
    get_contract('cells', 'NonExistentType')
    assert False, "Should have raised"
except MissingFormatContractError as e:
    print("PASS: MissingFormatContractError raised correctly")
except KeyError:
    print("FAIL: Caught as generic KeyError")
```
