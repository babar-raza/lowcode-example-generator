# Post-Merge Verification

Audience: Operator

After a PR is merged, verify that published examples still build from a clean checkout.

## Published Build Regression

```powershell
python scripts/validate_published_examples_build.py
```

Default report:

```text
workspace/verification/latest/monthly-build-regression-report.json
```

## Release Status

```powershell
python -m plugin_examples release-status --families cells words pdf --promote-latest
```

See [File Contracts](../reference/file-contracts.md) and [Publishing and GitHub](../reference/publishing-and-github.md).
