Sprint 84 — PR Batching Risk Matrix
=====================================
Date: 2026-05-24

## Risk Assessment by Family

| Family | Examples | Root README Conflict? | Merge Risk | Split Required? | Notes |
|--------|---------|-----------------------|------------|-----------------|-------|
| email  | 1       | No                    | LOW        | No              | Trivial; single example |
| slides | 3       | No                    | LOW        | No              | Small batch |
| diagram| 2       | Yes (PR #2 open)      | MEDIUM     | No (root excluded) | Root excluded per conflict strategy |
| cells  | 9       | Yes (PR #5 open)      | MEDIUM     | No (root excluded) | Root excluded per conflict strategy |
| words  | 8       | Yes (PR #7 open)      | MEDIUM     | No (root excluded) | Root excluded; words drift in PR #7 |
| pdf    | 19      | No                    | LOW-MEDIUM | No              | Largest batch but all example-only |

## Overall Risk: LOW
All families proceed as example-only batch (root README excluded for cells/words/diagram).
No exception conditions met. Strategy: 6 PRs.

## Residual Risks
1. pdf 19-file PR may take longer to review — mitigated by merge-order (last)
2. Root README for cells/words/diagram still pending open PRs — not resolved this sprint
3. Approval gate remains NOT_SET — all PRs blocked regardless of batching strategy
