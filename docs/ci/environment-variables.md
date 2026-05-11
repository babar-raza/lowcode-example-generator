# Environment Variables — Aspose Plugin Example Pipeline

This document lists all environment variables required or used by the pipeline.

## Required for GitHub Operations

### `GITHUB_TOKEN`
- **Required for:** Live PR creation, live PR merge, repo access probe, fixture registry fetch
- **Type:** GitHub classic PAT with `repo` scope
- **How to set:** `export GITHUB_TOKEN="ghp_XXXXXXXXXXXXXXXXXXXXXX"`
- **Security:** Never logged, never written to evidence files. Pipeline enforces no-log policy.
- **Note:** Must have write access to `aspose-cells-net` and `aspose-words-net` orgs.
- **Fixture registry:** Also needed for read access to `aspose-words/Aspose.Words-for-.NET` (different org — may require separate grant).

## Required for Live Publishing Approval

### `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`
- **Required for:** `publish-pr --publish` (live PR creation)
- **Value:** Must equal exactly `APPROVE_LIVE_PR`
- **How to set:** `export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`
- **Note:** Explicitly rejected for merge operations (gate blocks reuse).

### `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL`
- **Required for:** `merge-pr --merge` (live PR merge)
- **Value:** Must equal exactly `APPROVE_MERGE_PR`
- **How to set:** `export PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR`
- **Note:** Separate from `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`. Cannot be substituted.

## Required for LLM Generation

### `GPT_OSS_ENDPOINT`
- **Required for:** LLM-based example generation (`run` command with LLM router)
- **Example:** `https://llm.professionalize.com/v1/`

### `GPT_OSS_API_KEY`
- **Required for:** LLM API authentication
- **Security:** Never logged or written to evidence files.

### `GPT_OSS_MODEL`
- **Optional:** Override model name (default: `recommended`)
- **Note:** Do NOT use `gpt-4o-mini`. Use the latest recommended model.

## Required for Example Reviewer

### `EXAMPLE_REVIEWER_PATH`
- **Required for:** `--require-reviewer` mode in `run` command
- **Example:** `/path/to/example-reviewer`
- **Note:** Must point to a checked-out `example-reviewer` repo with `.venv` and `openai>=1.69.0`.

## Optional / CI-specific

### `PYTHONPATH`
- **Set to `src`** for all pipeline commands:
  ```bash
  PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples <command>
  ```

## GitHub Actions (CI) — Required Secrets

| Secret Name | Maps to env var | Purpose |
|-------------|-----------------|---------|
| `GITHUB_TOKEN` | `GITHUB_TOKEN` | Auto-provided by GitHub Actions for repo-scoped operations |
| `PLUGIN_EXAMPLES_PAT` | `GITHUB_TOKEN` | Cross-org PAT for publishing to `aspose-cells-net` / `aspose-words-net` |
| `GPT_OSS_ENDPOINT` | `GPT_OSS_ENDPOINT` | LLM endpoint for generation |
| `GPT_OSS_API_KEY` | `GPT_OSS_API_KEY` | LLM API key |

> **Note on approval tokens in CI:** `APPROVE_LIVE_PR` and `APPROVE_MERGE_PR` are human approval tokens and must NOT be stored as CI secrets. They must be provided interactively by a human operator.
