# Monthly Maintenance

Audience: Operator
Frequency: monthly and on demand

The monthly GitHub Actions workflow is `.github/workflows/monthly-package-refresh.yml`. It runs on the first day of each month at 06:00 UTC and can be manually dispatched.

## Manual Dry Run

```powershell
python -m plugin_examples run --family cells --dry-run --promote-latest
```

## CI Flow

The workflow:

1. Checks out the repo.
2. Installs Python 3.12.
3. Installs .NET 8.0.
4. Installs the package.
5. Builds DllReflector.
6. Runs `python -m plugin_examples run --family ...`.
7. Runs selected evidence integrity tests.
8. Runs published example build regression.

## Evidence

Inspect:

- `workspace/runs/{run_id}/pilot-report.json`
- `workspace/runs/{run_id}/evidence/latest/`
- `workspace/verification/latest/families/{family}/`
- `workspace/verification/latest/monthly-build-regression-report.json`

See [File Contracts](../reference/file-contracts.md).
