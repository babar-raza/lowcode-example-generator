# Live Publishing

Audience: Operator

Live publishing creates GitHub pull requests. It does not push directly to `main`.

## Preconditions

- Family run has a publishable gate verdict.
- Dry-run package exists under `workspace/pr-dry-run/`.
- Repo access and publish permission probes are ready.
- `GITHUB_TOKEN` is set.
- Human supplies `APPROVE_LIVE_PR`.

## Probe First

```powershell
python -m plugin_examples validate-publish-targets --families cells --promote-latest
python -m plugin_examples resolve-repo-access --families cells --promote-latest
python -m plugin_examples probe-publish-permissions --families cells --promote-latest
```

## Simulate PR

```powershell
python -m plugin_examples publish-pr --family cells --dry-run --approval-token APPROVE_LIVE_PR --promote-latest
```

## Create Live PR

```powershell
python -m plugin_examples publish-pr --family cells --publish --approval-token APPROVE_LIVE_PR --promote-latest
```

## Merge

Merge requires a separate approval token:

```powershell
python -m plugin_examples merge-pr --family cells --pr-number 1 --merge --approval-token APPROVE_MERGE_PR --promote-latest
```

See [Publishing and GitHub](../reference/publishing-and-github.md).
