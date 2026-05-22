# Publication State Model — Sprint 67

Date: 2026-05-22

## Per-Example Publication State (11 fields)

Each of the 42 examples has the following publication state:

| Field | State | Count |
|-------|-------|-------|
| `remote_example_present` | true | 42/42 |
| `remote_readme_has_io` | false | 0/42 |
| `local_corrected_package_ready` | true | 42/42 |
| `local_package_path_is_sprint67` | true | 42/42 |
| `pdf_version_consistent` | true (26.5.0) | 19/19 (PDF) |
| `root_readme_cardinality_annotated` | true/partial | 5/6 families |
| `live_pr_open` | false | 0/42 |
| `live_pr_merged` | false | 0/42 |
| `approval_token_present` | false | — |
| `publication_status` | REMOTE_PUBLISHED_STALE_IO | 42/42 |
| `final_readiness` | READY | 42/42 |

## State Definitions

| State | Meaning |
|-------|---------|
| `REMOTE_PUBLISHED_STALE_IO` | Example exists in remote repo, Program.cs is current, README has no I/O section |
| `BLOCKED_BY_APPROVAL` | Corrected package ready; live PR blocked by missing approval token |
| `READY` | Local handoff package is complete and self-contained |

## Separation of State

| Concern | State |
|---------|-------|
| Remote example existence | VERIFIED — 42/42 (Sprint 66 GH API audit) |
| Remote README I/O state | VERIFIED — 0/42 have I/O sections |
| Local corrected package | VERIFIED — 42/42 in sprint67/handoff/ |
| Live publication readiness | APPROVAL_BLOCKED |
| Sprint path hygiene | VERIFIED — no sprint64/sprint66 refs |

## Allowed Final Verdicts

This sprint targets: `LOWCODE_PREPUBLICATION_HANDOFF_READY_APPROVAL_BLOCKED`

Conditions met:
- 42/42 local handoff packages: READY
- 0/42 live PRs: consistent with APPROVAL_BLOCKED
- All 5 sprint66 defects addressed (4 closed, 1 partial for PDF table)
- Legacy plans reconciled
- EV/ECC hardened with new rules
