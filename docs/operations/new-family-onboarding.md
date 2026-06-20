# New Family Onboarding Checklist

Audience: Operator, Pipeline engineer
Source of truth: This file. For command reference see [CLI Reference](../reference/cli.md).

This checklist describes the complete, ordered sequence of steps to onboard a new
Aspose product family (NuGet package) into the pipeline and publish its first examples
to GitHub.

---

## Prerequisites

Before starting, confirm:

- [ ] Python 3.12+ installed and `.venv` created (`pip install -e ".[dev]"`)
- [ ] .NET SDK 8.0 installed (`dotnet --version`)
- [ ] `DllReflector` builds: `dotnet build tools/DllReflector/DllReflector.csproj -c Release`
- [ ] `GITHUB_TOKEN` env var set with a classic PAT (`repo` scope, read+write on target org)
- [ ] `GPT_OSS_ENDPOINT` / `GPT_OSS_MODEL` / `GPT_OSS_API_KEY` set (LLM generation only)
- [ ] Target GitHub repository exists for the family (see Step 9)

---

## Step 1 — Verify NuGet package availability

Confirm the package exists on NuGet.org and is accessible:

```bash
# Check NuGet availability (no credentials needed for public packages)
PYTHONPATH=src python -m plugin_examples nuget-check --package Aspose.<Family>
```

Expected output: package version, license, download URL, target frameworks.

**Blocking condition:** If package is unavailable or requires a paid license not in the
environment, mark the family as `BLOCKED_PACKAGE_UNAVAILABLE` in the capability registry
and stop.

**Evidence:** Record package version and license in the capability registry entry.

---

## Step 2 — Create capability registry entry

Create `pipeline/plugin-capability-registry/<family>.yaml`:

```yaml
entries:
- family: <family>
  package_id: Aspose.<Family>
  type_name: null        # filled after probe
  namespace: null        # filled after probe
  method_name: null      # filled after probe
  status: WEBSITE_DISCOVERED
  confidence_score: 0.5
  confidence_rationale: Initial entry — needs reflection probe.
  probe_evidence: null
  failure_taxonomy: null
  rejection_reason: null
  ai_source_flag: false
  assembly_fingerprint: null
  plugin_page_hash: null
  last_validated: '<YYYY-MM-DDT00:00:00Z>'
  bootstrap_status: WEBSITE_DISCOVERED
  next_action: PROBE_PENDING
  blocker_type: null
  last_reflected_package_version: null
  refresh_due: '<YYYY-MM-DD>'  # 3 months from today
```

See `pipeline/plugin-capability-registry/imaging.yaml` for a proven example.

**Evidence path:** `pipeline/plugin-capability-registry/<family>.yaml` committed.

---

## Step 3 — Create plugin-code-registry entry

Create `pipeline/plugin-code-registry/family/<family>.yaml`:

```yaml
family: <family>
package_id: Aspose.<Family>
github_repo: https://github.com/aspose-<family>/Aspose.<Family>-for-.NET
implementation_model: LOAD_SAVE_OPTIONS   # or RENDERING_API, PLUGIN_PATTERN
plugins:
- plugin_slug: <operation-name>
  canonical_plugin_slug: <operation-name>
  identity_status: WEBSITE_DISCOVERED
  registry_status: WEBSITE_DISCOVERED
  blocker_type: null
  next_action: PROBE_PENDING
```

**Evidence path:** `pipeline/plugin-code-registry/family/<family>.yaml` committed.

---

## Step 4 — Run the probe

The probe downloads the NuGet package, reflects its DLLs, and runs a minimal C# console
project to confirm the API actually works at runtime.

```bash
PYTHONPATH=src python -m plugin_examples probe-registry \
    --family <family> \
    --execute
```

**Expected outputs:**
- `reports/probe-<family>-<date>/prototypes/<family>/output-validation.json`
- Status updated to `PROBE_CONFIRMED` or `PROBE_FAILED` in the capability registry.

**If PROBE_FAILED:** Check `failure_taxonomy` for the root cause:
- `PROBE_FAILED_LICENSE` — runtime license exception (Aspose evaluation watermark is OK; hard fail is not)
- `PROBE_FAILED_API` — type or method not found in reflection
- `PROBE_FAILED_BUILD` — dotnet build error
- `PROBE_FAILED_RESTORE` — NuGet restore error
- `PROBE_FAILED_TIMEOUT` — probe timed out

See `docs/operations/dll-sibling-fixes.md` for known DLL dependency issues.

**Blocking condition:** Do not proceed to Step 5 without `PROBE_CONFIRMED` status.

---

## Step 5 — Promote confirmed probe entries

```bash
PYTHONPATH=src python -m plugin_examples probe-registry \
    --family <family> \
    --promote
```

This updates the capability registry YAML with:
- `status: PROBE_CONFIRMED`
- `assembly_fingerprint`
- `last_reflected_package_version`
- `probe_evidence` path
- `next_action: READY_FOR_EXAMPLE_GENERATION`

**Verification:**
```bash
grep "status: PROBE_CONFIRMED" pipeline/plugin-capability-registry/<family>.yaml
```

---

## Step 6 — Create family config YAML

Create `pipeline/configs/families/<family>.yaml`. Copy the structure from an existing
family config (e.g., `imaging` or `barcode`).

Key fields:
- `nuget.package_id` — must match the capability registry.
- `github.target_repo` — the target GitHub repository where PRs will be submitted.
- `github.target_org` — the GitHub org that owns the repo.
- `validation.require_example_reviewer` — set to `true` for families with complex APIs.
- `plugin_detection.fallback_strategy` — set to `CAPABILITY_REGISTRY` for non-LowCode families.

**Verification:**
```bash
PYTHONPATH=src python -m plugin_examples doctor
```
Doctor should show the new family config as loaded without errors.

---

## Step 7 — Prepare fixture files

Many examples require input files (e.g., a sample image, a PDF, a spreadsheet). Identify
the required formats from the capability registry entries and add fixture files under
`tests/fixtures/` if they do not already exist.

Common fixture locations:
- `tests/fixtures/samples/` — generic sample files
- `tests/fixtures/<family>/` — family-specific samples

The pipeline will use `--input-strategy` to select:
- `existing_fixture` — uses a file from `tests/fixtures/`
- `generated_fixture_file` — generates a minimal fixture programmatically
- `programmatic_input` — creates input in-memory within the generated example

**No fixture = no example.** The scenario planner blocks examples with no valid input strategy.

---

## Step 8 — Run a dry-run pipeline pass

Verify the full pipeline runs from config → reflection → scenario planning without
generating LLM code or touching GitHub:

```bash
PYTHONPATH=src python -m plugin_examples run \
    --family <family> \
    --dry-run \
    --template-mode \
    --promote-latest
```

**Expected outputs** (under `workspace/<family>/<run-id>/`):
- `download-manifest.json`
- `dependency-manifest.json`
- `reflection-catalog.json`
- `plugin-detection-proof.json`
- `scenario-catalog.json`
- `fixture-strategy-plan.json`

**Investigate if** `scenario-catalog.json` shows all scenarios as blocked — check `blocked_reason` in each entry.

---

## Step 9 — Verify target GitHub repository exists

```bash
# Requires GITHUB_TOKEN to be set
PYTHONPATH=src python -m plugin_examples probe-publish-permissions \
    --family <family>
```

Or manually check:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/repos/<org>/<repo-name>
```

Expected: HTTP 200 with `"permissions": {"push": true}`.

**Blocking condition:** If the repo does not exist or the token lacks push access, stop here
and raise as an external blocker. Document in `docs/operations/blocked-external-repos.md`.

---

## Step 10 — Run with LLM generation

Once dry-run is green and the target repo is accessible, run with generation:

```bash
PYTHONPATH=src python -m plugin_examples run \
    --family <family> \
    --promote-latest
```

This calls the approved LLM endpoint (`https://llm.professionalize.com/v1/`) to generate
C# code for each planned scenario, then runs `dotnet restore → build → run → output check`
for every generated example.

**Watch for:**
- `BLOCKED_BUILD_FAILED` — generated code does not compile (LLM used wrong symbol)
- `BLOCKED_RUN_FAILED` — code compiles but crashes at runtime
- `advisory_no_output` — code runs but produces no meaningful console output

All failures are preserved in `workspace/<family>/<run-id>/validation-results.json`
with explicit reasons.

---

## Step 11 — Review generated examples and prepare PR

After generation, inspect generated examples under `workspace/<family>/<run-id>/examples/`:
- Open `Program.cs` files to verify they are sensible and runnable.
- Check `validation-results.json` for any advisory failures.
- Confirm `gate-verdict.json` shows `PR_READY` or `PR_DRY_RUN_READY`.

To create the pull request (requires `GITHUB_PR_APPROVAL_TOKEN` env var):

```bash
PYTHONPATH=src python -m plugin_examples publish-pr \
    --family <family>
```

This uses the GitHub Git Data API (no direct push to `main`) to:
1. Create a branch
2. Upload all validated example files
3. Open a pull request

**Evidence:** PR URL is printed and recorded in `workspace/<family>/<run-id>/publish-report.json`.

---

## Step 12 — Merge PR after review

After the PR is reviewed and CI passes on the target repo, merge it:

```bash
PYTHONPATH=src python -m plugin_examples merge-pr \
    --family <family> \
    --pr-number <N>
```

This requires `GITHUB_MERGE_APPROVAL_TOKEN` (a separate token from PR creation).

**Post-merge:** Run post-publication verification:

```bash
PYTHONPATH=src python -m plugin_examples post-publication-verify \
    --family <family>
```

Verify the merged examples are present and buildable in the target repo.

---

## Common Failure Patterns

| Failure | First check | Resolution |
|---|---|---|
| `PROBE_FAILED_API` | Is the type in the DLL? Run DllReflector manually. | Check `docs/operations/dll-sibling-fixes.md` for sibling DLL issues. |
| `BLOCKED_BUILD_FAILED` | Check generated `Program.cs` for wrong namespace/type | Update capability registry with correct type_name; rerun probe. |
| `BLOCKED_RUN_FAILED` with license error | Aspose evaluation mode adds watermarks but usually does not throw | If a hard exception: the family needs a valid license to run — mark as BLOCKED_LICENSE_RESTRICTED. |
| `BLOCKED_RESTORE_FAILED` | NuGet feed unreachable? Proxy? | Check NuGet.org access from the machine; check `.csproj` PackageReference. |
| Scenario catalog shows 0 ready scenarios | No fixture files? Wrong plugin_detection.fallback_strategy? | Verify capability registry has at least one PROBE_CONFIRMED entry; add fixture files. |
| GitHub 403 on PR creation | Token scope issue | Ensure token is a classic PAT with `repo` scope; fine-grained PATs may fail on org repos. |

---

## Walk-Through Validation

To validate this checklist is accurate for a specific family, run through it and record
the output at each step in:

```
workspace/evidence/onboarding-walkthrough-<family>/
  step-01-nuget-check.txt
  step-02-capability-registry.yaml
  step-03-code-registry.yaml
  step-04-probe-output.json
  step-05-probe-promote.txt
  step-06-doctor.txt
  step-07-fixtures.txt
  step-08-dryrun-scenarios.json
  step-09-repo-check.json
  step-10-generation-gate.json
  step-11-pr-url.txt
  step-12-post-merge-verify.txt
```

If any step produces unexpected output, update this checklist before onboarding the
next family.
