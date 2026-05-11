# CLI Reference

Audience: Operator, Contributor
Source of truth: `pyproject.toml`, `src/plugin_examples/__main__.py`

The package exposes the `plugin-examples` console script and can also be run as a module:

```powershell
plugin-examples --help
python -m plugin_examples --help
```

Global flag:

| Flag | Purpose |
|---|---|
| `--verbose`, `-v` | Enable debug logging. |

Shared metrics flags on most commands:

| Flag | Purpose |
|---|---|
| `--metrics` | Enable metrics collection in dry-run mode by default. |
| `--metrics-post` | POST metrics to the configured endpoint. Requires token. |
| `--metrics-job-type TYPE` | Override metrics job type. |
| `--metrics-strict` | Fail the command on metrics errors. |
| `--metrics-force-repost` | Bypass metrics duplicate ledger check. |
| `--metrics-config PATH` | Override metrics config path. |

## Commands

| Command | Purpose | Flags |
|---|---|---|
| `status` | Print implemented module list. | none |
| `run` | Run the full or tiered pipeline for one family. | `--family`, `--dry-run`, `--template-mode`, `--skip-run`, `--require-llm`, `--require-validation`, `--require-reviewer`, `--publish`, `--approval-token`, `--tier`, `--promote-latest`, `--allow-experimental`, `--compare-run` |
| `discover-lowcode` | Run source-of-truth discovery without generation. | `--all-families`, `--family`, `--families`, `--dry-run`, `--promote-latest`, `--allow-experimental`, `--rank` |
| `validate-publish-targets` | Check publish readiness for family configs. | `--families`, `--promote-latest` |
| `resolve-repo-access` | Read-only GitHub API access probe for publish targets. | `--families`, `--promote-latest` |
| `probe-publish-permissions` | Read-only push-permission probe for publish targets. | `--families`, `--dry-run`, `--promote-latest` |
| `publish-pr` | Simulate or create a live PR for a verified package. | `--family`, mutually exclusive `--dry-run` / `--publish`, `--approval-token`, `--promote-latest` |
| `merge-pr` | Simulate or perform a PR merge. | `--family`, `--pr-number`, mutually exclusive `--dry-run` / `--merge`, `--approval-token`, `--promote-latest` |
| `release-status` | Report family release state from evidence files. | `--families`, `--promote-latest` |
| `render-root-readme` | Render and audit a package README locally. | `--family`, `--package-path`, `--promote-latest` |
| `publish-readme` | Simulate or create a README-only PR. | `--family`, `--publish`, `--approval-token`, `--promote-latest` |
| `sync-taskcard-docs` | Generate the taskcard markdown matrix from JSON evidence. | `--promote-latest` compatibility flag |
| `check` | Package update check placeholder. | `--family` |

## Run Tiers

The `run --tier` flag accepts `0` through `5`.

| Tier | Max stage |
|---|---|
| `0` | No pipeline stage |
| `1` | Source-of-truth discovery through plugin detection |
| `2` | Scenario planning |
| `3` | Generation |
| `4` | Reviewer |
| `5` | Publisher |

## Live Operation Safety

`run --publish` and `publish-pr --publish` require `GITHUB_TOKEN` and approval token `APPROVE_LIVE_PR`.

`merge-pr --merge` requires a separate approval token `APPROVE_MERGE_PR`. The PR approval token is explicitly rejected for merge.

See [Publishing and GitHub](publishing-and-github.md).
