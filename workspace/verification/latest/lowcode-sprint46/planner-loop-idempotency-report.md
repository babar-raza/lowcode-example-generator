# Planner Loop Idempotency Report — Sprint 46

## Fix: VERIFIED

Sprint 45 ran the same 6 actions 3 times with no state change. Sprint 46 fixes this.

## New Behavior
1. Cycle 1: Execute 6 safe actions, all return `changed=false`
2. Cycle 2: Board fingerprint unchanged, all handlers noop
3. Verdict: `IDEMPOTENT_NO_CHANGE`
4. Loop stops at cycle 2 (was cycle 3 + max_cycles before)

## Implementation
- `board_fingerprint()`: SHA-256 of stable board state (excludes volatile `generated_at`)
- Handler `changed` flag: read-only handlers return `changed=False`
- Stop when: fingerprint unchanged AND no changed handlers
- 12 new tests covering fingerprinting, stop conditions, rerun idempotency
