# ADR-008: pip-audit Advisory-Only Policy

**Status:** Accepted
**Date:** 2026-06-16

## Context

The CI pipeline runs `pip-audit` to scan Python dependencies for known vulnerabilities. This job currently uses `allow_failure: true`, meaning it does not block the pipeline on failure.

Two categories of false failures have been observed:

1. **Transient PyPI index failures** — network timeouts or index unavailability cause pip-audit to exit non-zero even when no vulnerabilities exist.
2. **False positives on pre-release versions** — pip-audit may flag versions that have been patched upstream but whose advisory metadata is not yet updated in the PyPI vulnerability database.

Blocking the pipeline on pip-audit would cause unrelated work to stall when these transient conditions occur.

## Decision

pip-audit remains advisory (`allow_failure: true`) with the following compensating controls:

- **Monthly review cadence:** The team reviews pip-audit output on the first Monday of each month during the monthly-refresh cycle.
- **CI visibility:** pip-audit output is always visible in the GitLab CI job log. Failures are flagged with a yellow warning indicator.
- **Escalation:** Any HIGH or CRITICAL vulnerability that persists across two consecutive monthly reviews must be escalated and resolved within 7 days.
- **Blocking path:** If pip-audit achieves zero false positives for three consecutive months, it will be promoted to a blocking gate.

## Consequences

- Known vulnerabilities may persist for up to one review cycle (30 days).
- The pipeline is never blocked by PyPI index outages.
- Advisory status is explicitly governed, not silently ignored.
- Monthly review creates an audit trail in sprint evidence.

## Alternatives Considered

1. **Make pip-audit blocking immediately** — rejected due to transient failure rate.
2. **Remove pip-audit entirely** — rejected; even advisory scanning provides value.
3. **Pin pip-audit to a specific version** — does not address PyPI index transient failures.
