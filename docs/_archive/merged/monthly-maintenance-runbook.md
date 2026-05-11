# Monthly Maintenance Runbook

**Version:** 1.0
**Date:** 2026-05-03
**Applies to:** Aspose .NET Plugin Example Generation Pipeline — Cells + Words families

This runbook is the repeatable procedure for monthly example generation runs. Every step has a
concrete command. Do not skip steps. Do not use one-time manual actions.

---

## Immutable rules (never override)

1. **Per-family repo targets** — each family publishes to its own dedicated repo. No central repo fallback.
   - Cells → `aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples`
   - Words → `aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples`
2. **No all-family generation** without explicit human approval per family.
3. **Live PR approval gate** — `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` required.
4. **Merge approval gate** — `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR` required. This is **separate** from `APPROVE_LIVE_PR`.
5. **No token logging** — `GITHUB_TOKEN` and approval tokens are never written to files or printed.
6. **Dry-run before live PR** — always run `publish-pr --dry-run` before `publish-pr --publish`.
7. **Clean checkout after merge** — always run post-merge clean-checkout validation.
8. **Words allowed types** — Cells: all types. Words: Converter, Watermarker, Splitter, Replacer only (controlled pilot). Broader generation requires opening and closing `followup-words-*` taskcards first.
9. **PDF blocked** until `followup-pdf-reflection-dedup` is resolved.

---

## Step 1 — Check for NuGet package updates

Determine if a new version of Aspose.Cells or Aspose.Words has been released this month.

```bash
# Check current versions
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples check --family cells
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples check --family words
```

If no new version: stop here. Monthly run is not needed (delta-based policy).

---

## Step 2 — Rebuild source-of-truth catalogs

Run discovery sweep to refresh the API catalog from the latest NuGet package.

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples discover-lowcode \
  --families cells words --promote-latest
```

Expected output: `Discovery sweep: 2 families scanned, 2 with LowCode namespaces`

Artifacts written:
- `workspace/verification/latest/all-family-lowcode-discovery.json`
- `workspace/verification/latest/family-generation-readiness-rank.json`

Stop if either family shows `blocked_reflection_failed`.

---

## Step 3 — Run family readiness checks

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples validate-publish-targets \
  --families cells words --promote-latest
```

Expected: `2/2 ready`

```bash
PYTHONPATH=src GITHUB_TOKEN="$GH_TOKEN" .venv/Scripts/python.exe -m plugin_examples \
  probe-publish-permissions --families cells words --promote-latest
```

Expected: `2/2 families have push permission`

Stop if any family is not ready.

---

## Step 4 — Regenerate only impacted examples (delta-based)

Run the generation pipeline. Only examples whose API signatures have changed will regenerate.

```bash
# Cells (all types)
PYTHONPATH=src \
  EXAMPLE_REVIEWER_PATH="C:/Users/prora/OneDrive/Documents/GitHub/example-reviewer" \
  .venv/Scripts/python.exe -m plugin_examples run \
  --family cells --tier 5 --promote-latest

# Words (controlled pilot — 4 types only, enforced by allowed_types in words.yml)
PYTHONPATH=src \
  EXAMPLE_REVIEWER_PATH="C:/Users/prora/OneDrive/Documents/GitHub/example-reviewer" \
  .venv/Scripts/python.exe -m plugin_examples run \
  --family words --tier 5 --promote-latest
```

Stop if verdict is not `PR_DRY_RUN_READY` or `FULL_E2E_PASSED`.

---

## Step 5 — Validate examples

Pipeline validates automatically during `run`. For explicit re-validation of a specific example:

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run \
  --family cells --tier 5 --require-validation --require-reviewer --promote-latest
```

Check `workspace/verification/latest/validation-results.json` for per-example results.

---

## Step 6 — Create dry-run PR package

```bash
# Cells dry-run
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family cells --dry-run --promote-latest

# Words dry-run
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family words --dry-run --promote-latest
```

Expected: `SIMULATION_PASSED` for each family.

Artifacts written:
- `workspace/verification/latest/cells-live-pr-simulation.json`
- `workspace/verification/latest/words-live-pr-simulation.json`

Stop if either simulation is blocked.

---

## Step 7 — Create live PR (requires human approval)

Human must explicitly provide `APPROVE_LIVE_PR` before this step.

```bash
# Cells live PR
PYTHONPATH=src GITHUB_TOKEN="$GH_TOKEN" .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family cells --publish --approval-token APPROVE_LIVE_PR --promote-latest

# Words live PR
PYTHONPATH=src GITHUB_TOKEN="$GH_TOKEN" .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family words --publish --approval-token APPROVE_LIVE_PR --promote-latest
```

Record PR URLs and numbers. Do not merge yet.

---

## Step 8 — Merge after approval (requires separate human approval)

Human must explicitly provide `APPROVE_MERGE_PR` (separate from `APPROVE_LIVE_PR`).

First, run dry-run to verify preconditions:

```bash
PYTHONPATH=src GITHUB_TOKEN="$GH_TOKEN" .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family cells --pr-number N --dry-run --approval-token APPROVE_MERGE_PR --promote-latest

PYTHONPATH=src GITHUB_TOKEN="$GH_TOKEN" .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family words --pr-number N --dry-run --approval-token APPROVE_MERGE_PR --promote-latest
```

Then live merge:

```bash
PYTHONPATH=src GITHUB_TOKEN="$GH_TOKEN" .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family cells --pr-number N --merge --approval-token APPROVE_MERGE_PR --promote-latest

PYTHONPATH=src GITHUB_TOKEN="$GH_TOKEN" .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family words --pr-number N --merge --approval-token APPROVE_MERGE_PR --promote-latest
```

Record merge commit SHAs. Do not delete source branches.

---

## Step 9 — Post-merge validation

After each merge, clone from main and validate:

```bash
# Run release-status to get current state
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples release-status \
  --families cells words --promote-latest
```

Manually validate by cloning the target repo and running each example:

```bash
git clone --depth=1 --branch main \
  https://github.com/aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples.git /tmp/cells-post-merge
cd /tmp/cells-post-merge/examples/cells/lowcode/html-converter && dotnet run --nologo
# ... repeat for all 9 examples

git clone --depth=1 --branch main \
  https://github.com/aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples.git /tmp/words-post-merge
cd /tmp/words-post-merge/examples/words/lowcode/converter && dotnet run --nologo
# ... repeat for all 4 examples
```

Expected: all examples exit 0 and produce output files.

Write post-merge validation JSON to `workspace/verification/latest/{family}-post-merge-clean-checkout-validation.json`.

---

## Step 10 — Failure triage

| Symptom | Likely cause | Action |
|---|---|---|
| `blocked_reflection_failed` in discovery | DLL version conflict (esp. PDF) | File taskcard for dedup fix |
| `LLMProviderError: not approved by policy` | Unapproved provider in config | Fix provider_order in family YAML |
| Build failure in generated example | LLM produced invalid code | Re-run `run --family X --tier 5`; check repair log |
| `blocked_live_pr_approval_required` | Missing APPROVE_LIVE_PR | Human provides token |
| `blocked_merge_reused_live_publish_token` | APPROVE_LIVE_PR used for merge | Use APPROVE_MERGE_PR instead |
| `gate_verdict_not_publishable` | Gate not PR_DRY_RUN_READY | Run `run --family X` first; check validation-results.json |
| Post-merge clean checkout fails | Bad example in PR | Investigate; do not merge; fix and re-PR |

---

## Release status check (at any time)

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples release-status \
  --families cells words --promote-latest
```

Writes `workspace/verification/latest/release-status.json` with per-family published state.

---

## Evidence files written per monthly run

| File | Description |
|---|---|
| `workspace/verification/latest/all-family-lowcode-discovery.json` | API catalog refresh |
| `workspace/verification/latest/family-generation-readiness-rank.json` | Readiness ranking |
| `workspace/verification/latest/family-publish-readiness.json` | Publish target readiness |
| `workspace/verification/latest/publish-permission-probe.json` | Push permission check |
| `workspace/verification/latest/{family}-live-pr-simulation.json` | Dry-run PR simulation |
| `workspace/verification/latest/{family}-live-pr-result.json` | Live PR creation result |
| `workspace/verification/latest/{family}-merge-pr-simulation.json` | Merge dry-run |
| `workspace/verification/latest/{family}-merge-result.json` | Live merge result |
| `workspace/verification/latest/{family}-post-merge-clean-checkout-validation.json` | Post-merge validation |
| `workspace/verification/latest/release-status.json` | Current release state |
