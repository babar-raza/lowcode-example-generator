# Portfolio Release Dashboard — sprint35

**Generated:** 2026-05-18T10:05:47.742519+00:00  
**Verdict:** `PORTFOLIO_RELEASE_CANDIDATE_APPROVAL_BLOCKED`  
**Evidence Contract:** V6 (67 categories)  
**Test Suite:** 1744/1744 PASS  
**Approval Gate:** `NOT_SET`

## Summary

| Metric | Value |
|--------|-------|
| Total Published | 28 |
| Total PR-Ready (pending approval) | 14 |
| Total Families | 6 |
| Families Complete/Pilot Complete | 5 |
| Families Partial Canary | 1 |

## Family Status

| Family | Status | Published | Pilot Scope | Coverage | PR-Ready | Version |
|--------|--------|-----------|-------------|----------|----------|---------|
| Cells | `FAMILY_COMPLETE` | 9 | 9 | 100.0% | 0 | 26.4.0 |
| Words | `PILOT_COMPLETE` | 8 | 8 | 100.0% | 0 | 26.5.0 |
| Pdf | `PARTIAL_CANARY` | 5 | 19 | 26.3% | 14 | 26.5.0 |
| Diagram | `PILOT_COMPLETE` | 2 | 2 | 100.0% | 0 | 26.4.0 |
| Email | `PILOT_COMPLETE` | 1 | 1 | 100.0% | 0 | 26.4.0 |
| Slides | `PILOT_COMPLETE` | 3 | 3 | 100.0% | 0 | 26.5.0 |

## System Health

| Component | Status |
|-----------|--------|
| TC-SYS-01 (per_type_constraints) | `COMPLETE` |
| TC-SYS-02 (generic validation) | `COMPLETE` |
| TC-SYS-03 (completeness gate) | `COMPLETE` |
| TC-SYS-04 (ENUM tracking) | `COMPLETE` |
| TC-SYS-05 (all-family release_status) | `COMPLETE` |
| evidence_contract_version | `V6 (67 categories)` |
| test_suite | `1744/1744 PASS` |
| approval_gate | `NOT_SET (publication blocked)` |
| github_token | `SET (classic PAT, repo scope)` |

## Notes

- **Words**: Processor (PERMANENTLY_BLOCKED)
- **Pdf**: PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL not set
- **Pdf**: 26.5.0 NullReferenceException — TC-PDF-FORMIMPORTER-RETEST

## Next Action

Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` and run:
```bash
python -m plugin_examples publish-pr-batch --family pdf --publish --approval-token APPROVE_LIVE_PR
```
