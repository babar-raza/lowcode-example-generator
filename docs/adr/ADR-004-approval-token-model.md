# ADR-004: Dual Approval Token Model for Live Operations

**Status:** Accepted
**Date:** 2026-06-04
**Deciders:** Pipeline architecture team

---

## Context

The pipeline can perform two distinct live operations that affect external shared state:

1. **Live PR creation** — Creates a branch and pull request on a GitHub plugin repository.
2. **Live merge** — Merges an approved PR into the target repository's `main` branch.

Both operations are irreversible in practice (PRs are visible externally; merges change the production codebase). Automated agents running in CI or locally could accidentally trigger these operations if not properly gated.

Early pipeline versions used a single boolean flag (`--publish`). This meant a misconfigured dry-run flag could accidentally create live PRs.

---

## Decision

Live operations require **explicit string approval tokens** that must be passed at runtime:

| Operation | Token | Where set |
|-----------|-------|-----------|
| Live PR creation | `--approval-token APPROVE_LIVE_PR` | CLI flag or `APPROVE_LIVE_PR` env var |
| Live merge | `APPROVE_LIVE_MERGE=1` | Environment variable only |

Rules:
- `--dry-run` and `--publish` are mutually exclusive at the CLI level.
- The approval token is validated before any network call is made.
- If `GITHUB_TOKEN` is absent, live publishing is blocked at startup with a clear error.
- The `verify-remote` command can be run post-merge to confirm remote state matches local expectations.

---

## Consequences

**Positive:**
- A misconfigured `--dry-run=False` flag cannot accidentally create live PRs.
- Tokens are explicit: CI logs show exactly when a live operation was authorized.
- Separate tokens for PR creation vs. merge allow staged authorization (reviewer approves PR, release manager approves merge).

**Negative:**
- Live operations require an extra explicit step; developers cannot run them without deliberately passing the token.
- Token management must be handled securely (env vars, not hardcoded in scripts).

**Security note:** The approval token (`APPROVE_LIVE_PR`) is not a secret — it is a confirmation string. The actual authentication to GitHub is via `GITHUB_TOKEN`, which must be a scoped PAT stored securely.

---

## Alternatives Considered

| Option | Rejected Reason |
|--------|----------------|
| Boolean --publish flag only | Accidental triggering risk; no audit trail |
| Interactive confirmation prompt | Not CI-compatible; blocks automation |
| Separate deployment pipeline | Overengineered for current scale; adds pipeline fragmentation |
