# Sprint 75 — Weekly Review Claim vs Proof Matrix

**Date:** 2026-05-23
**Sprint:** sprint75

This matrix records each of the 6 independent review items with their claim, the evidence
consulted, and the final classification determined during sprint75 investigation.

---

## Item 1 — 14 PDF Examples Blocked by Approval Gate

| Field | Value |
|-------|-------|
| Claim | 14 PDF examples (PR#3/PR#5/PR#6/PR#7/PR#8/PR#9) were blocked by approval gate |
| Claim source | Commit `a0319bb` (Sprint 21, 2026-05-16), mega-train-005 report |
| Evidence consulted | reports/sprint75/remote/remote-example-inventory.json (42 records, 19 PDF) |
| Evidence consulted | reports/sprint75/publication/publication-truth-matrix-final.json (19 PDF records) |
| Evidence consulted | GitHub API: all 19 PDF records show readme_sha and programcs_sha populated |
| Current state | All 19 PDF examples: `remote_example_present: true`, `remote_programcs_status: PRESENT_VERIFIED` |
| Historical context | At Sprint 21, only 5 PDF examples were published. PRs #3/5/6 covered later examples. Subsequent sprints (57-74) published all 19 via PRs #11, #17-#21 and later bulk publication. |
| **Final classification** | **VERIFIED_HISTORICAL_BUT_SUPERSEDED** |
| Resolution | The "14 blocked" claim was accurate at Sprint 21. All 19 PDF examples are now remotely present and verified. The old PRs (3/5/6) were superseded by later PRs. |
| PDF README I/O | Still 0/19 remote README I/O — this is the current open work item (not example-code publication) |

---

## Item 2 — FormImporter Upstream Aspose.PDF 26.5.0 Bug

| Field | Value |
|-------|-------|
| Claim | FormImporter blocked by NullReferenceException in Aspose.PDF 26.5.0 |
| Claim source | mega-train-005 pdf-formimporter-retest-report.md, formimporter_watch.py |
| Evidence consulted | workspace/defect-repros/pdf-formimporter-nullref/formimporter-repro.csproj |
| Evidence consulted | formimporter-repro.csproj shows `<PackageReference Include="Aspose.PDF" Version="26.5.0" />` |
| Evidence consulted | mega-train-005 report: "Latest NuGet version: 26.5.0 — Version advanced beyond defect: false" |
| Evidence consulted | Repro artifacts (Program.cs, minimal-form.pdf, minimal-form-data.json) confirmed present |
| Current state | Repro exists. Package 26.5.0 is still latest. No newer version available. Bug not fixed. |
| **Final classification** | **BLOCKED_EXTERNAL** |
| Resolution | FormImporter remains blocked by upstream library bug. Retest trigger: Aspose.PDF > 26.5.0 on NuGet. Taskcard TC-PDF-FORMIMPORTER-RETEST maintained with current evidence. |

---

## Item 3 — Words Version Drift 26.4.0 vs 26.5.0

| Field | Value |
|-------|-------|
| Claim | Words published at 26.4.0; NuGet target is 26.5.0; no regeneration performed |
| Claim source | Prior sprint MEMORY.md, sprint75 version-truth-matrix.json |
| Evidence consulted | reports/sprint75/version/version-truth-matrix.json |
| Evidence consulted | reports/sprint75/handoff/per-family/words/handoff-index.json |
| Current state (remote) | `remote_published_version: 26.4.0` |
| Current state (handoff) | `handoff_version: 26.5.0`, `canonical_version: 26.5.0` |
| Drift confirmed | YES — `drift: "REMOTE_DRIFT — remote published at 26.4.0; handoff and local at 26.5.0"` |
| **Final classification** | **NEEDS_REPAIR** |
| Resolution | Version drift is real and current. Resolution requires README I/O PR (includes version bump from 26.4.0 to 26.5.0 in Words csproj). Blocked by `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` absent. |

---

## Item 4 — Email and Slides Post-Merge Runtime Validation Deferred

| Field | Value |
|-------|-------|
| Claim | Email PR#1 and Slides PR#1 merged; runtime validation deferred; `all_post_merge_validated=false` |
| Claim source | Commit `afca831` (sprint unblock activation), commit `a0319bb` |
| Evidence consulted | `git show afca831` — confirms Email PR#1 merged (`023ad66970d2`) and Slides PR#1 merged (`bf05fc43124f`) |
| Evidence consulted | `git show a0319bb` — confirms "Lane I: Email PR#1 and Slides PR#1 files confirmed on…" |
| Evidence consulted | reports/sprint75/publication/post-merge-verification.json — `merges_to_verify: 0` (sprint75 made no new merges) |
| Current state | Email and Slides examples are merged on remote. Post-merge runtime validation never performed since merge (confirmed deferred across sprints 21–74). |
| **Final classification** | **NEEDS_REPAIR** |
| Resolution | Email converter and Slides (compress/convert/merger) need end-to-end runtime validation. Results documented in Phase 5. Runtime validation requires .NET SDK and Aspose packages available locally. |

---

## Item 5 — Working Tree Has Uncommitted Modifications

| Field | Value |
|-------|-------|
| Claim | evidence_validator.py, two test files, 7 workspace/latest JSON files, untracked reports/sprint72/ |
| Claim source | Weekly review snapshot |
| Evidence consulted | `git status` at sprint75 start (captured in git/dirty-state-before.txt) |
| Current state | Modified: 7 workspace/verification/latest/*.json only. NO source or test files. Untracked: reports/sprint75/ only (not sprint72/). |
| **Final classification** | **VERIFIED_HISTORICAL_BUT_SUPERSEDED** |
| Resolution | The source/test modifications and sprint72 untracked state were present at review time but committed in sprint73/74. Remaining 7 workspace files are pre-existing runtime state (known governance exception since sprint66). |

---

## Item 6 — Sprint 27 Bundle Fails StrictEvidenceContract V1

| Field | Value |
|-------|-------|
| Claim | Sprint 27 bundle retroactively fails StrictEvidenceContract V1 (≥10 missing categories) |
| Claim source | Commit `20686d3` message: "Sprint 27 thin bundle retroactively FAILS contract (≥10 missing categories)" |
| Evidence consulted | git log confirms commit `20686d3` exists (Sprint 28 bundle) |
| Evidence consulted | `ls reports/` — sprint27 bundle NOT present locally. Earliest is sprint57. |
| Current state | Sprint 27 bundle is an extremely old historical artifact (2026 era, pre-sprint57 cleanup). The bundle does not exist locally. The StrictEvidenceContract V1 failure was documented in Sprint 28 and is a historical fact. |
| **Final classification** | **GOVERNANCE_EXCEPTION_REQUIRED** |
| Resolution | Sprint 27 cannot be rebuilt (no local bundle). Sprint 28 already documented the failure in commit `20686d3`. Sprint 75 creates a formal historical-evidence exception policy. EV rules will not validate sprint27 retroactively — they will instead require explicit historical-exception annotation for sprints prior to sprint57. |

---

## Summary Table

| Item | Claim | Final Classification | Phase |
|------|-------|---------------------|-------|
| 1 | 14 PDF examples blocked | VERIFIED_HISTORICAL_BUT_SUPERSEDED | 2 |
| 2 | FormImporter blocked by 26.5.0 bug | BLOCKED_EXTERNAL | 3 |
| 3 | Words version drift 26.4.0 vs 26.5.0 | NEEDS_REPAIR | 4 |
| 4 | Email/Slides runtime validation deferred | NEEDS_REPAIR | 5 |
| 5 | Working tree dirty (source/test/workspace) | VERIFIED_HISTORICAL_BUT_SUPERSEDED | 1 |
| 6 | Sprint 27 fails StrictEvidenceContract V1 | GOVERNANCE_EXCEPTION_REQUIRED | 6 |

All 6 items classified. No item dropped. No item blindly accepted.
