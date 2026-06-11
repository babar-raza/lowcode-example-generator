# Service Level Objectives (SLOs)

Last verified: 2026-06-10
Source of truth: CI pipeline results + test suite + monthly refresh logs

## Pipeline SLOs

| Metric | Target | Measurement | Current |
|--------|--------|-------------|---------|
| Test pass rate | >= 99.5% | `passed / (passed + failed)` from pytest | 100% (4152/4152) |
| CI build success rate | >= 95% | Green builds / total builds on main | Monitored via GitLab CI |
| Monthly refresh cadence | 1x per month | `monthly-package-refresh.yml` run count | Scheduled 1st of month |
| Doctor health check | 0 required failures | `python -m plugin_examples doctor` | 7/7 OK |
| Gate false-positive rate | < 5% | Manual review of blocked scenarios | Tracked per wave |

## Publication SLOs

| Metric | Target | Measurement |
|--------|--------|-------------|
| PR creation turnaround | Within same wave sprint | Time from BUILD_PASS to PR_CREATED |
| PR merge turnaround | External approval dependent | Tracked in wave reports |
| Evidence bundle completeness | 100% required fields | Evidence validators (EVC, RBC rules) |

## Availability

This is a batch pipeline, not a service. Availability targets apply to:
- CI pipeline: should complete within 10 minutes per run
- Monthly refresh: should complete within 2 hours per family
- Doctor command: should complete within 5 seconds

## Monitoring

- CI status: GitLab CI pipeline dashboard
- Test trends: tracked in wave sprint reports (tests passed count)
- Evidence integrity: SHA-256 sidecars on all evidence bundles

## Review Cadence

SLOs reviewed at each wave sprint closeout. Targets adjusted if consistently exceeded or missed.
