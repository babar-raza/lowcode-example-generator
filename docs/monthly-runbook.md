# Monthly Runbook

## Overview

The pipeline runs monthly to detect NuGet package updates and generate new examples.

## Automated Schedule

- **When:** 1st of each month at 06:00 UTC
- **Workflow:** `.github/workflows/monthly-package-refresh.yml`
- **Trigger:** `schedule` or `workflow_dispatch`

## Manual Run

```bash
# Dry-run (default)
python -m plugin_examples run --family cells --dry-run

# Live run
python -m plugin_examples run --family cells
```

## Pipeline Stages

1. **Package check** — compare NuGet version against package-lock.json
2. **Fetch & extract** — download .nupkg, resolve dependencies, extract DLLs
3. **Reflect** — run DllReflector to build API catalog
4. **Detect** — match plugin namespaces, write source-of-truth proof
5. **Delta** — compare current catalog against previous version
6. **Plan** — build scenarios from delta and catalog
7. **Generate** — create C# examples via LLM
8. **Validate** — restore, build, run each example
9. **Review** — run example-reviewer gate
10. **Publish** — create PR with validated examples

## Exit Conditions

- No package change: exit cleanly, no PR
- No eligible namespaces: exit with proof, no PR
- No ready scenarios: exit with blocked report
- LLM unavailable: exit with preflight report
- Validation failure: exit with results, no PR
- Reviewer failure: exit with results, no PR

## Evidence Files

All runs produce evidence in `workspace/verification/latest/`.
Durable manifests go to `workspace/manifests/`.

## Disabled Families

Families with `enabled: false` or `status: disabled` in their config
are never processed. They are skipped silently.
