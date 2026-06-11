# ADR-002: Gate Isolation — No AI/LLM Imports in Gate Modules

**Status:** Accepted
**Date:** 2026-06-01
**Deciders:** Pipeline architecture team
**RISK tag:** RISK-10

---

## Context

The pipeline uses gate evaluation to decide which generated examples are ready for PR creation. Gate decisions have direct downstream consequences: a false pass creates a bad PR; a false block silently drops a valid example.

Early in the pipeline design, there was a risk that gate logic could inadvertently import AI generation modules (`llm_router`, `healing_intelligence`, `generator`). This would make gate results non-deterministic and harder to audit — the same example could pass a gate on one run and fail on another depending on model state.

---

## Decision

Gate modules under `src/plugin_examples/gates/` **must never import** `llm_router`, `healing_intelligence`, or `generator` (or any transitively non-deterministic module).

This constraint is:
1. **Documented** — the `_GATE_ISOLATION_FORBIDDEN` frozenset in `example_gates.py` lists forbidden module names.
2. **CI-enforced** — `build-and-test.yml` runs a `grep` check that fails the build if any forbidden import appears in `gates/`.
3. **Test-enforced** — unit tests in `tests/unit/test_gates.py` verify the isolation invariant.

All gate logic must be deterministic: given the same inputs, the gate must return the same verdict.

---

## Consequences

**Positive:**
- Gate verdicts are reproducible and auditable.
- Evidence bundles containing gate results can be independently verified.
- CI failures are fast and clear when the invariant is violated.
- AI-model upgrades cannot silently change pass/fail behavior on existing examples.

**Negative:**
- Gate logic cannot use LLM-based heuristics (e.g., "this output looks right").
- All validation must be rule-based: regex, schema validation, exit code checks, deterministic parsing.

**Acceptable trade-off:** The gate layer is intentionally conservative. Advisory AI-based output review is implemented as a separate, clearly non-blocking reviewer gate that does not affect the hard pass/fail verdict.

---

## Alternatives Considered

| Option | Rejected Reason |
|--------|----------------|
| Allow LLM imports in gates with a flag | Non-determinism is invisible; makes evidence unreliable |
| Runtime check only (no CI enforcement) | Easy to forget; silently breaks on refactor |
| Separate process for AI gate | Too complex; blocked example flow already handles advisory feedback |
