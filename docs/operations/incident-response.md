# Incident Response Plan

Last verified: 2026-06-10
Source of truth: this document + CI workflow definitions

## Severity Definitions

| Severity | Description | Response Time | Examples |
|----------|------------|---------------|----------|
| P1 — Critical | Pipeline cannot generate or validate any examples | 4 hours | NuGet API down, DllReflector broken, all CI failing |
| P2 — High | One or more families blocked, others operational | 24 hours | Family config schema violation, fixture source unavailable |
| P3 — Medium | Degraded output quality, non-blocking | 72 hours | LLM endpoint slow, one validator false-positive |
| P4 — Low | Cosmetic or documentation issue | Next sprint | README stale, evidence bundle metadata incomplete |

## Triage Steps

### 1. Identify Scope
```bash
# Check CI status
# Visit: https://gitlab.recruitize.ai/sialkot/cantt-smallize/lowcode-example-generator/-/pipelines

# Run doctor locally
PYTHONPATH=src python -m plugin_examples doctor --json

# Check which families are affected
PYTHONPATH=src python -m plugin_examples status
```

### 2. Classify Root Cause

| Symptom | Likely Cause | Check |
|---------|-------------|-------|
| NuGet fetch fails | API rate limit or package delisted | `curl https://api.nuget.org/v3/index.json` |
| DllReflector fails | .NET SDK missing or DLL incompatible | `dotnet --version` |
| LLM generation fails | Endpoint down or model unavailable | Check `llm.professionalize.com` status |
| Gate false-positive | Validator logic bug | Run specific validator test |
| Publication blocked | Approval gate not set | Check `APPROVE_LIVE_MERGE` env var |

### 3. Escalation Path

1. **Automated**: CI failure notifies pipeline owner via GitLab notification
2. **Manual triage**: Pipeline owner runs doctor + status commands
3. **External dependency**: If NuGet/GitHub/LLM endpoint is down, wait and document
4. **Code fix needed**: Create branch, fix, run tests, PR to main

## Recovery Procedures

### CI Pipeline Failure
1. Check the failed job logs in GitLab CI
2. Run the failing test locally: `python -m pytest tests/unit/<failing_test> -v`
3. If environment-specific, check Python version matrix (3.12, 3.13)
4. Fix and verify locally before pushing

### Monthly Package Refresh Failure
1. Check `reports/` for the latest run evidence
2. Run doctor to verify prerequisites
3. Re-run with `--dry-run` first: `python -m plugin_examples run --family <family> --dry-run`
4. If NuGet version changed, update family config

### Publication Gate Failure
1. Publication requires `APPROVE_LIVE_MERGE=1` — this is intentional
2. Never bypass the gate; verify all prerequisites first
3. Run `python -m plugin_examples verify-remote` after any live merge

## Post-Incident

1. Document the incident in `reports/incidents/YYYY-MM-DD-<slug>.md`
2. Update this runbook if new failure mode discovered
3. Add regression test if feasible
4. Update doctor checks if new prerequisite identified
