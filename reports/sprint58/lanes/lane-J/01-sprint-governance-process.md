# Process: Sprint Governance and Evidence Contract

**Process ID:** LANE-J-01
**Version:** Sprint 58
**Date:** 2026-05-21

---

## Overview

Every sprint must produce a signed evidence contract (`evidence-contract.json`) before closure. The contract lists all evidence categories, whether each is blocking, and its current status. A sprint CANNOT be closed while any blocking category is PENDING.

---

## Phase Structure

| Phase | Name | Blocking EC Categories |
|-------|------|----------------------|
| 0 | Previous sprint audit | EC01, EC02, EC03 |
| 1 | Lane setup | EC06, EC07 |
| 2 | Known bug fixes | EC08 (type-specific) |
| 3 | Package authority proof | EC09, EC10, EC11, EC12 |
| 4 | Consistency scan | EC13 |
| 5 | Per-example regeneration | EC14, EC15 |
| 6 | Destination audit | EC16, EC17 |
| 7 | README gate / branch delete | EC18 |
| 8 | Hygiene audits | EC19, EC20 (non-blocking) |
| 9 | Lane J docs | EC21 |
| 10 | Test suite + git status | EC22, EC23 |
| 11 | Final bundle + verdict | EC24, EC25 |

---

## Evidence Contract Rules

1. **bundle_min_files:** Bundle must contain ≥25 meaningful files
2. **no_pending_blocking_categories:** Any blocking EC with status PENDING = INVALID_CLOSURE
3. **no_metadata_only_bundle:** Bundle cannot contain only sprint-state.json + bundle-manifest.json
4. **test_log_required:** Test counts claimed without log file = FAILURE
5. **regeneration_ledger_per_example:** Per-family totals without per-example directory = FAILURE
6. **package_authority_no_contract_only:** No authority_source=contract_only in io-authority-evidence-matrix.json
7. **lane_j_not_pending:** Lane J PENDING at closure = FAILURE
8. **git_status_end_required:** End-of-sprint git status required
9. **commands_log_complete:** commands.log must not be IN_PROGRESS at closure

---

## Sprint State Machine

The sprint governance state machine (`sprint-state.json`) tracks 11 lanes:

```
lane-0: Sprint framework setup
lane-A: Sprint 57 audit
lane-B: Package authority proof
lane-C: Consistency scan
lane-D: Bug fixes (pdf-aconverter)
lane-E: 42/42 regeneration
lane-F: Destination audit
lane-G: README / branch-auto-delete
lane-H: Hygiene
lane-I: Final tests + git status
lane-J: Process documentation
```

**Closure rule:** ALL lanes must be COMPLETE before issuing sprint verdict.

---

## Commands Log Requirement

Sprint 58 introduced `commands.log` — a running log of all commands executed during the sprint. Format:

```
[TIMESTAMP] [PHASE] COMMAND
  OUTPUT: ...
```

The commands.log must be finalized (not IN_PROGRESS) before closure.
