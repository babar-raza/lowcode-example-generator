# Contract-First Codegen Action Resolution

## Action: CONTRACT_FIRST_CODEGEN
- Sprint 51 classification: gate=none (ungated, safe)
- Sprint 51 description: "Implement contract-first codegen to unblock WIP tests"

## Investigation

### Current state:
1. Contract-first format inference is ALREADY IMPLEMENTED in the planner:
   - `_infer_input_format()` and `_infer_output_format()` use `allow_legacy_format_inference=False`
   - Committed in 43ff580 and 5e66c8b
2. Contract-first adoption tests ALREADY PASS (10/10):
   - `tests/unit/test_planner_contract_consumption.py` (committed 33beb18)
3. The remaining work is implementing contract-first CODE GENERATION:
   - The code generator (`src/plugin_examples/generator/code_generator.py`) still uses hardcoded format maps
   - Changing it to use format contracts requires:
     - Modifying LLM prompt templates
     - Updating code generation constraints
     - Integration testing across all 6 families
     - Ensuring generated code matches contract expectations

### Assessment:
- This is a **multi-file design initiative**, not a single safe action
- It cannot be completed atomically in a single sprint
- It requires design review for LLM prompt changes
- No immediate blocker — the current hardcoded format maps work correctly
- The planner-side contract consumption is already done

## Decision: RECLASSIFY AS NOT-SAFE-NOW

- Reason: Multi-file design initiative requiring LLM prompt changes and cross-family integration testing
- Risk: Medium — LLM prompt changes can cause format drift regression
- Taskcard: TC-CONTRACT-FIRST-CODEGEN
- Dependencies: None blocking current pipeline operation
- Priority: Medium — current hardcoded maps work correctly

## Gap Status: CLOSED
