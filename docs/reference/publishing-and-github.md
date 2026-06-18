# Publishing and GitHub

Audience: Operator, Contributor

Source of truth: `src/plugin_examples/__main__.py`, `src/plugin_examples/publisher/`

Last verified: 2026-06-17

## Publishing Model

Publishing is PR-based. The pipeline must not push directly to `main`.

Family publish targets come from `github.published_plugin_examples_repo` in family configs. See [Configuration Reference](config.md).

## Token Model

The pipeline reads `GITHUB_TOKEN`. Operators store the PAT in `GH_TOKEN` and map it before each live command.

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
```

Use a classic PAT with `repo` scope. Fine-grained PATs owned by a personal account can fail for org-owned repos at the Git Data API layer.

## Approval Tokens

| Operation | Required token | Env fallback |
|---|---|---|
| Live PR creation | `APPROVE_LIVE_PR` | `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` |
| README-only PR creation | `APPROVE_LIVE_PR` | `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` |
| Live PR merge | `APPROVE_MERGE_PR` | `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` |

Merge rejects `APPROVE_LIVE_PR`.

## Publish Readiness Commands

| Command | Remote mutation | Purpose |
|---|---:|---|
| `validate-publish-targets` | No | Check family config publish targets. |
| `resolve-repo-access` | No | Probe GitHub API read access for publish targets. |
| `probe-publish-permissions` | No | Probe push/publish permission readiness. |
| `publish-pr --dry-run` | No | Simulate PR creation and write evidence. |
| `publish-pr --publish` | Yes | Create a live PR. Requires `GITHUB_TOKEN` and `APPROVE_LIVE_PR`. |
| `publish-pr-batch --dry-run` | No | Simulate all PR packages for a family. |
| `publish-pr-batch --publish` | Yes | Create live PRs for all packages selected by batch publisher. |
| `merge-pr --dry-run` | No | Verify merge preconditions. |
| `merge-pr --merge` | Yes | Merge a PR. Requires `GITHUB_TOKEN` and `APPROVE_MERGE_PR`. |
| `publish-readme --publish` | Yes | Create README-only PR. Requires `GITHUB_TOKEN` and `APPROVE_LIVE_PR`. |

## Live PR Preconditions

Live PR creation requires:

- `GITHUB_TOKEN`
- `APPROVE_LIVE_PR`
- Publishable gate verdict
- Existing dry-run package under `workspace/pr-dry-run/`
- Repo access readiness
- Publish permission readiness
- Branch name different from the target branch
- README audit gate pass when README publishing is part of the flow

## Merge Preconditions

Live merge requires:

- `GITHUB_TOKEN`
- `APPROVE_MERGE_PR`
- PR number and family
- Open PR in the expected target repo
- Expected file set
- Clean-checkout evidence where required by the merge precondition checker
- CI/check status acceptable to the merge code path

## Evidence

Common publishing evidence files include:

- `family-publish-readiness.json`
- `family-repo-access-resolution.json`
- `publish-permission-probe.json`
- `{family}-live-pr-result.json`
- `{family}-merge-result.json`
- `publishing-report.json`
- `release-status.json`
- README backfill/render/audit result files

See [File and Evidence Contracts](file-contracts.md) for paths.

## Related Runbooks

- [Live Publishing](../operations/live-publishing.md)
- [README Publishing](../operations/readme-publishing.md)
- [Post-Merge Verification](../operations/post-merge-verification.md)
