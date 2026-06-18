# CLI Reference

Audience: Operator, Contributor

Source of truth: `pyproject.toml`, `src/plugin_examples/__main__.py`

Last verified: 2026-06-17

The package exposes the `plugin-examples` console script and can also be run as a module:

```powershell
plugin-examples --help
python -m plugin_examples --help
```

## Global Flags

| Flag | Purpose |
|---|---|
| `--verbose`, `-v` | Enable debug logging. |

## Shared Metrics Flags

Most command parsers receive these flags from `_add_metrics_flags()`.

| Flag | Purpose |
|---|---|
| `--metrics` | Enable metrics collection. Metrics are dry-run by default. |
| `--metrics-post` | POST metrics to the configured endpoint. Requires `AGENT_METRICS_TOKEN`. |
| `--metrics-job-type TYPE` | Override metrics `job_type`. |
| `--metrics-strict` | Fail the command on metrics errors. |
| `--metrics-force-repost` | Bypass metrics duplicate ledger checks. |
| `--metrics-config PATH` | Override metrics config path. Default is `pipeline/configs/metrics.yml`. |

See [Metrics](metrics.md) and [Environment Variables](environment-variables.md).

## Commands

| Command | Purpose | Flags/options |
|---|---|---|
| `status` | Show pipeline status. | none |
| `run` | Run the full or tiered pipeline for one family. | `--family`, `--dry-run`, `--template-mode`, `--skip-run`, `--require-llm`, `--require-validation`, `--require-reviewer`, `--publish`, `--approval-token`, `--tier`, `--promote-latest`, `--allow-experimental`, `--compare-run`, `--replay-from`, `--reuse-run`, shared metrics flags |
| `discover-lowcode` | Run discovery-only source-of-truth sweep. | `--all-families`, `--family`, `--families`, `--dry-run`, `--promote-latest`, `--allow-experimental`, `--rank`, shared metrics flags |
| `validate-publish-targets` | Check publish readiness for family configs. | `--families`, `--promote-latest`, shared metrics flags |
| `resolve-repo-access` | Probe GitHub API access for publish targets. | `--families`, `--promote-latest`, shared metrics flags |
| `probe-publish-permissions` | Read-only push-permission probe for publish targets. | `--families`, `--dry-run`, `--promote-latest`, shared metrics flags |
| `publish-pr` | Simulate or create a live PR for a verified dry-run package. | `--family`, mutually exclusive `--dry-run` / `--publish`, `--approval-token`, `--package-path`, `--promote-latest`, shared metrics flags |
| `merge-pr` | Verify preconditions and simulate or execute PR merge. | `--family`, `--pr-number`, mutually exclusive `--dry-run` / `--merge`, `--approval-token`, `--promote-latest`, shared metrics flags |
| `release-status` | Report per-family release state from evidence files. | `--families`, `--promote-latest`, `--validate-bundle`, shared metrics flags |
| `render-root-readme` | Render and audit root README for a package. | `--family`, `--package-path`, `--promote-latest`, `--cumulative`, shared metrics flags |
| `publish-readme` | Create or simulate a README-only PR in a target repo. | `--family`, `--publish`, `--approval-token`, `--promote-latest`, shared metrics flags |
| `sync-taskcard-docs` | Generate the taskcard markdown matrix from JSON evidence. | `--promote-latest` compatibility flag, shared metrics flags |
| `check` | Package update check placeholder. | `--family` |
| `publish-pr-batch` | Batch publish all PR packages for a family. | `--family`, mutually exclusive `--publish` / `--dry-run`, `--approval-token`, `--promote-latest` |
| `formimporter-watch` | Check FormImporter defect status against latest NuGet version. | `--run-repro`, `--output` |
| `post-publication-verify` | Verify published examples in local PR dry-run packages. | `--family`, `--output` |
| `version-drift` | Check NuGet version drift for confirmed LowCode families. | `--family`, `--output`, `--json` |
| `target-repo-health` | Verify target repos for confirmed LowCode families. | `--family`, `--output`, `--json` |
| `next-actions` | Compute the portfolio action board. | `--output`, `--markdown`, `--json` |
| `execute-next-actions` | Execute safe next actions through the planner loop. | `--evidence-dir`, `--max-cycles`, `--dry-run-remote`, `--json` |
| `catalog-discover` | Scrape products.aspose.net to discover non-LowCode plugin slugs and NuGet packages. | `--family`, `--families`, `--all-families`, `--replay`, `--sitemap`, `--output`, `--delay-ms`, `--enrich-registry`, `--expand-registry`, shared metrics flags |
| `doctor` | Run startup health checks for the pipeline environment. | `--json` |
| `metrics-summary` | Show pipeline metrics summary from evidence files. | `--repo-root`, `--json` |
| `probe-registry` | Generate C# probe code from capability-registry entries, optionally run dotnet restore/build/run, and promote results. | `--family`, `--slug`, `--execute`, `--promote`, `--timeout`, `--json` |
| `psal-run` | Run PSAL multi-family autonomous governance loop across non-LowCode families. | `--families`, `--max-iterations`, `--dry-run`, `--template-mode`, `--repo-root`, `--json` |
| `sprint-governance` | Coordinate sprint loop: classify P3 summary, decide next stage (AUDIT/HARDEN/EXECUTE/ACCEPT/ESCALATE). | `--sprint-name`, `--summary-file`, `--max-iterations`, `--repo-root`, `--json` |
| `verify-remote` | Verify remote repository state against a publication record. | `--publication-record`, `--output` |

## `run` Tiers

`run --tier` accepts `0` through `5`.

| Tier | Max stage |
|---|---|
| `0` | No pipeline stage |
| `1` | Source-of-truth discovery through plugin detection |
| `2` | Scenario planning |
| `3` | Generation |
| `4` | Reviewer |
| `5` | Publisher |

## Replay Options

`run --replay-from` accepts:

- `generation`
- `validation`
- `reviewer`
- `publisher`

`--reuse-run RUN_ID` selects the prior run. If omitted with `--replay-from`, the runner auto-detects the most recent prior `pilot-{family}-*` run.

## Live Operation Safety

`run --publish`, `publish-pr --publish`, and `publish-readme --publish` require `GITHUB_TOKEN` and approval token `APPROVE_LIVE_PR`.

`merge-pr --merge` requires approval token `APPROVE_MERGE_PR`. The live PR approval token is rejected for merge.

See [Publishing and GitHub](publishing-and-github.md).
