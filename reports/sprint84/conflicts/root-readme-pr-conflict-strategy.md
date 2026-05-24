Sprint 84 — Root README PR Conflict Strategy
=============================================
Date: 2026-05-24
Author: Lane C

## Context
Three open root-README PRs exist from prior sprints:
- cells PR #5: root README with IO section
- words PR #7: root README with IO section + version drift fix
- diagram PR #2: root README with IO section

Sprint 83 resolved this by globally excluding root READMEs from all 6 families.
Sprint 84 makes this decision explicit and per-family.

## Per-Family Strategy

### cells — EXCLUDE_ROOT_README
Open PR #5 is unmerged. Including root README in sprint84 batch PR would create divergence.
Strategy: EXCLUDE root README from sprint84 batch PR.
Root README path: (remote) README.md at repo root
When to include: After PR #5 is merged or closed.

### words — EXCLUDE_ROOT_README
Open PR #7 is unmerged. PR #7 also carries Words version drift fix (26.4.0→26.5.0).
Strategy: EXCLUDE root README from sprint84 batch PR.
Do NOT modify Directory.Packages.props in sprint84 batch PR (version bump lives in PR #7).
When to include: After PR #7 is merged or closed.

### diagram — EXCLUDE_ROOT_README
Open PR #2 is unmerged.
Strategy: EXCLUDE root README from sprint84 batch PR.
When to include: After PR #2 is merged or closed.

### pdf — INCLUDE_ROOT_README_IF_CHANGED
No open root-README PR. Root README not changed this sprint.
Strategy: no root README change needed; exclude by default (no change = no commit).

### email — INCLUDE_ROOT_README_IF_CHANGED
No open root-README PR. Root README not changed this sprint.
Strategy: no root README change needed; exclude by default.

### slides — INCLUDE_ROOT_README_IF_CHANGED
No open root-README PR. Root README not changed this sprint.
Strategy: no root README change needed; exclude by default.

## Sprint 84 Decision
EXCLUDE_ROOT_README_FROM_SPRINT84_BATCH_PRS for cells, words, diagram.
No root README changes required for pdf, email, slides this sprint.
Net effect: Sprint 84 batch PRs contain ONLY example-level README changes (42 files).

## Open PR Resolution Path
These PRs are not blocked by Sprint 84 pipeline. They should be merged independently
when approval is granted. After merge, subsequent sprints may include root README in batch.

## Comparison to Sprint 83
Sprint 83 excluded root README for all 6 families without distinguishing reason.
Sprint 84 explicitly states: cells/words/diagram = conflict deconflict; pdf/email/slides = no change needed.
