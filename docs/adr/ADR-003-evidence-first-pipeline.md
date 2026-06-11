# ADR-003: Evidence-First Pipeline Architecture

**Status:** Accepted
**Date:** 2026-06-01
**Deciders:** Pipeline architecture team

---

## Context

The pipeline generates, validates, and publishes code examples autonomously. Without a structured audit trail, it is impossible to:
- Verify that a generated example actually passed the build gate.
- Reproduce a specific pipeline run to investigate a failure.
- Prove that a PR was created from an example that met all quality bars.
- Detect silent regressions where a previously passing example is no longer generated.

Early pipeline versions (before Wave 10) wrote results only to ephemeral stdout. Post-run investigations were blocked because no artifacts were preserved.

---

## Decision

Every pipeline stage **must write JSON evidence** to `evidence/` before the next stage begins. No stage may advance past a gate without persisting a result record.

Evidence artifacts include:
- `catalog-hash-validation.json` — reflection catalog identity
- `fixture-strategy-plan.json` — fixture resolution decisions
- `gate-results.json` — per-example verdict records
- `pr-candidate-manifest.json` — PR inclusion/exclusion with reasons
- `validation-summary.json` — build/run/output pass rates
- Evidence bundles (ZIP + SHA-256 sidecar) for sprint closeout

Evidence requirements:
- Must be written even on partial failure (blocked scenarios are evidence too).
- SHA-256 sidecars on sprint bundles for integrity verification.
- Evidence validators (`EVC`, `RBC`, `CCV` rule families) check completeness at sprint closeout.

---

## Consequences

**Positive:**
- Full audit trail for every pipeline run.
- Reproducible: prior run artifacts can be replayed via `--replay-from`.
- Regression protection: `merge_pr_candidate_manifests()` preserves previously-passing examples.
- Claim verification: adversarial review can check every sprint against evidence.

**Negative:**
- `.local/` directory grows large (NuGet cache, reflection cache, evidence bundles).
- Evidence must be managed: old runs are not auto-purged.
- Sprint closeout requires all evidence validators to pass.

**Mitigation:**
- `.gitignore` excludes `.local/` to avoid accidentally committing large artifacts.
- `workspace/verification/latest/` holds promoted evidence for human review.
- Evidence bundle ZIP protocol (v3) keeps attestation external to the ZIP.

---

## Alternatives Considered

| Option | Rejected Reason |
|--------|----------------|
| Log-only (no persistent evidence) | Non-reproducible; no cross-run comparison |
| Database-backed state | Overengineered for a batch pipeline; JSON files are portable |
| Evidence only at sprint closeout | Too late to detect mid-run failures; no stage-level replay |
