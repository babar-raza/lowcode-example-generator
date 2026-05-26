# Post-Merge Verification

Audience: Operator

Purpose: verify that merged examples are healthy after publication.

Canonical references: [CLI](../reference/cli.md), [Publishing and GitHub](../reference/publishing-and-github.md), [File and Evidence Contracts](../reference/file-contracts.md)

## Preconditions

- PR was merged with `APPROVE_MERGE_PR`.
- Merge result evidence exists for the family.
- Target repo and branch are known from the family config.

## Verify Published Build Regression

```powershell
python scripts/validate_published_examples_build.py
```

Default report:

```text
workspace/verification/latest/monthly-build-regression-report.json
```

## Verify Local PR Packages

For local dry-run packages:

```powershell
python -m plugin_examples post-publication-verify --family <family>
```

Use `--output PATH` to write the report to a custom location.

## Refresh Release Status

```powershell
python -m plugin_examples release-status --families cells words pdf --promote-latest
```

Use `--validate-bundle BUNDLE_DIR` when validating a sprint/evidence bundle as part of release status.

## Stop Conditions

Stop and record evidence if:

- Build regression fails.
- Post-publication verification reports incomplete or failed package verification.
- Release status cannot read required evidence.
- The merged PR contains unexpected files.

## Evidence

Common evidence includes:

- `{family}-merge-result.json`
- `{family}-post-merge-clean-checkout-validation.json`
- `monthly-build-regression-report.json`
- `release-status.json`
- Post-publication verification report

See [File and Evidence Contracts](../reference/file-contracts.md).
