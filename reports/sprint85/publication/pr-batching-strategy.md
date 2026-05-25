Sprint 85 — PR Batching Strategy
=================================
Date: 2026-05-24
Author: Lane B (PR Strategy Agent)

## Strategy: FAMILY_BATCH_PR (carry-forward from Sprint 84)

One PR per family, 6 PRs total. This is the default strategy established in Sprint 84
and carried forward without change.

## Rationale
- Each family maps to one destination repo (e.g., Aspose.Cells, Aspose.Words).
- One PR per repo keeps review scope manageable.
- 42 PRs (one per example) would flood reviewers with no benefit.
- No conflict requires splitting within a family.

## Family → PR Mapping
| Family | Destination Repo | Examples | Branch |
|--------|-----------------|----------|--------|
| cells | Aspose.Cells | 9 | lowcode-examples-cells-sprint85 |
| words | Aspose.Words | 8 | lowcode-examples-words-sprint85 |
| pdf | Aspose.PDF | 19 | lowcode-examples-pdf-sprint85 |
| diagram | Aspose.Diagram | 2 | lowcode-examples-diagram-sprint85 |
| email | Aspose.Email | 1 | lowcode-examples-email-sprint85 |
| slides | Aspose.Slides | 3 | lowcode-examples-slides-sprint85 |

## Override Conditions
If any of these arise, the default may be overridden with documented justification:
- Conflict within a family requires splitting into sub-PRs.
- CI gating per-example requires atomic PRs.
- Reviewer requests separate PRs.

None of these conditions currently apply. Default strategy holds.
