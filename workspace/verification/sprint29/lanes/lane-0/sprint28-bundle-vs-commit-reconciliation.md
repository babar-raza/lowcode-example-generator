# Sprint 28 Bundle vs Commit Reconciliation

**Sprint:** 29
**Date:** 2026-05-17
**Prepared by:** Lane 0

## The Question

Supervisor noted: *"Sprint 28 bundle's `git-log-proof.txt` stops at `774f516`"*. Did this prove that commit `20686d3` was never made, or is there another explanation?

## Resolution

**Commit `20686d3` IS HEAD.** It is fully committed and confirmed.

### Why the Bundle Log Stopped at `774f516`

The Sprint 28 evidence bundle was constructed **during** the sprint, **before** the final commit. The workflow was:

1. All Sprint 28 lane evidence written to `workspace/verification/sprint28/`
2. `git-log-proof.txt` captured at that moment → stopped at `774f516` (prior sprint)
3. `bundle-contract-validation-report.json` written
4. Bundle ZIP built, validated → `BUNDLE_CONTRACT_PASSED`
5. **All files staged with exact paths**
6. **`git commit` executed** → creates commit `20686d3`

The bundle ZIP file itself **is inside** commit `20686d3`. Therefore, the git log inside the bundle necessarily cannot reference `20686d3` — the commit that adds the bundle hasn't happened yet when the bundle is built.

This is the standard bootstrap pattern for any evidence bundle. The bundle proves work done during a sprint; the commit proves the bundle was delivered.

**Sprint 29 `git-log-proof.txt` shows `20686d3` as the first entry**, proving the chain is intact.

## Dirty State at Sprint 29 Start

All dirty files are binary build artifacts, generated manifests, or trivial line-ending changes. **No source/config/test files are dirty.** No staged files. Sprint 28 source work is fully committed.

| Category | Files | Action |
|----------|-------|--------|
| Binary build (bin/obj) | 13 | Preserve — .NET harness compile output |
| Binary fixture | 3 (input.pdf, output-signed.pdf, test.pfx) | Preserve — harness run artifacts |
| Generated manifest | 2 | Stage with Sprint 29 |
| Generated release-status | 6 | Stage with Sprint 29 |
| Trivial (.gitignore) | 1 | Stage with Sprint 29 |
| Untracked (plans/) | 1 dir | Preserve untracked |

## Verdict

SPRINT28_COMMIT_VERIFIED — commit `20686d3` is HEAD, all Sprint 28 source/test/evidence is committed, dirty state is expected and classified.
