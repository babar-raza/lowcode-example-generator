# Self-Review Healing Plan — Iteration 1

## Context

Phase 1 self-review identified 5 dimensions scoring below 4/5 in the TC-H hardening sprint.
Root causes: (1) top-level import couples planner_loop to state module; (2) no test for
deprioritization path; (3) no test for doctor ECV check.

## Gap → Taskcard Map

| Gap ID | Description | Taskcard |
|--------|-------------|----------|
| G-01 | RunHistory top-level import in planner_loop.py breaks on state-module import failure | SR-01 |
| G-02 | No test verifies should_deprioritize() causes action deferral in run_execution_loop | SR-02 |
| G-03 | check_evidence_chain() in doctor.py has no unit test | SR-03 |

---

## SR-01 — Make RunHistory import lazy in planner_loop.py

- **Status**: Done
- **Gap**: G-01
- **Role**: Senior engineer. Drop-in fix, no behavioral change.
- **Scope**:
  - Fix: Move `from plugin_examples.state.run_history import RunHistory, RunRecord` from module top-level (line 23) into the body of `run_execution_loop()`, guarded by `if history_path is not None`
  - Also move the `RunRecord` usage (in `history.record_run()`) inside the same guard
  - Allowed paths: `src/plugin_examples/planner_loop.py` only
  - Forbidden: changing public signature, default behavior, or adding new module-level names
- **Acceptance checks**:
  - `python -c "from plugin_examples.planner_loop import run_execution_loop"` succeeds even if state/ is deleted temporarily
  - `grep -n "from plugin_examples.state" src/plugin_examples/planner_loop.py` returns 0 lines at module level (only inside function body)
  - `ruff check src/plugin_examples/planner_loop.py` exits 0
  - Existing integration tests pass
- **Hard rules**: Keep `history_path: Path | None = None` signature. No new deps.
- **5/5 means**: Import only happens when history_path is provided; import error in state/ cannot break planner_loop import.

---

## SR-02 — Add test for RunHistory deprioritization in planner_loop

- **Status**: Done
- **Gap**: G-02
- **Role**: Senior engineer. New test in existing test file or new file.
- **Scope**:
  - Add tests to `tests/unit/test_run_history.py` OR create `tests/unit/test_planner_loop_history.py`
  - Test: create RunHistory with ≥3 consecutive failures for family "cells", save to tempfile, call run_execution_loop with history_path, verify deferred list contains entry with reason "deprioritized_consecutive_failures"
  - Must mock `compute_action_board` to return a controlled board with a "cells" action
  - Allowed: unittest.mock, tmp_path fixture
  - Forbidden: network calls, real repo filesystem access
- **Acceptance checks**:
  - `pytest tests/unit/test_planner_loop_history.py -v` all pass
  - Test explicitly asserts `reason == "deprioritized_consecutive_failures"` in deferred list
  - Test explicitly asserts action IS deferred (not executed) when family has ≥3 consecutive failures
  - Complementary test: action is NOT deferred when family has <3 consecutive failures
- **Hard rules**: No TODO stubs. Both happy + regression paths tested.
- **5/5 means**: Test fails if deprioritization logic is removed from planner_loop.py.

---

## SR-03 — Add unit tests for check_evidence_chain in doctor.py

- **Status**: Done
- **Gap**: G-03
- **Role**: Senior engineer. New test file.
- **Scope**:
  - Create `tests/unit/test_doctor_evidence_chain.py`
  - Test cases:
    1. No `.local/evidence-chain/` dir → SKIP
    2. Dir exists, no JSON files → SKIP
    3. Dir exists, JSON files present but no gate_id/id/verdict fields → SKIP
    4. Dir exists, valid gate results with all fields → PASS (ECV passes)
    5. Dir exists, gate results with mismatched verdicts → WARN
  - Use tmp_path for all filesystem operations
  - Allowed: monkeypatch repo_root to tmp_path
  - Forbidden: real `.local/` directory access
- **Acceptance checks**:
  - `pytest tests/unit/test_doctor_evidence_chain.py -v` all pass
  - Coverage of `check_evidence_chain` reaches ≥90%
  - `ruff check tests/unit/test_doctor_evidence_chain.py` exits 0
- **Hard rules**: No network. No production file access. Tests are hermetic.
- **5/5 means**: Test catches a bug where SKIP is incorrectly returned when valid evidence exists.
