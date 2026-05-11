# Root README Template Preflight Review

**Date:** 2026-05-03
**Sprint:** Root README Template and Update Workflow Sprint
**Verdict:** PREFLIGHT_PASS

---

## Current Release State

| Family | Merge SHA | NuGet Version | Examples | Post-Merge | Package Has README |
|---|---|---|---|---|---|
| Cells | `f6e5515c` | 26.4.0 | 9 | POST_MERGE_VERIFIED | NO |
| Words | `b66fb430` | 26.4.0 | 4 | POST_MERGE_VERIFIED | NO |

The `workspace/pr-dry-run/cells-controlled-pilot/` and `workspace/pr-dry-run/words-controlled-pilot/` packages exist with examples but contain no `README.md`. The remote repos have a GitHub-generated placeholder README from repo initialization. The pipeline has never produced a README for these repos. This sprint implements that.

---

## Q1: Which README sections are reusable?

The following sections are structurally reusable across all families via Jinja2 template:

- H1 title with NuGet + GitHub license badges
- **Overview** — LowCode API description
- **Included Examples** — table generated from validated example list
- **Requirements** — .NET version, NuGet package + version
- **How to Run** — `dotnet restore` / `dotnet run` commands
- **Package Installation** — NuGet CLI install command
- **Validation Status** — badge/summary linking to evidence
- **Repository Layout** — directory structure
- **Useful Links** — NuGet, docs, API reference, blog, support, temporary license
- **License / Support** — Aspose commercial license info

---

## Q2: Which sections must be parameterized by family?

Every section. Specific parameters:

| Section | Parameter |
|---|---|
| Title | `display_name` (e.g. "Aspose.Cells for .NET") |
| Badges | `nuget_package_id`, `target_repo_owner/target_repo_name` |
| Overview | `display_name`, `product_name`, family-specific API description |
| Examples table | `examples` list (name, type, input, output, run command) |
| Requirements | `nuget_package_id`, `package_version`, `target_framework` |
| How to Run | `family` for path prefix |
| Useful Links | All URLs are family-specific |

---

## Q3: Which fields already exist in family config?

| Field | Source |
|---|---|
| `family` | `family.family` |
| `display_name` | `family.display_name` |
| `nuget_package_id` | `family.nuget.package_id` |
| `target_repo_owner` | `family.github.published_plugin_examples_repo.owner` |
| `target_repo_name` | `family.github.published_plugin_examples_repo.repo` |
| `allowed_types` | `family.generation.allowed_types` (Words pilot) |

---

## Q4: Which fields must be derived from evidence/manifests?

| Field | Source |
|---|---|
| `package_version` | `{family}-live-pr-result.json` → `.nuget_version` (fallback: `Directory.Packages.props`) |
| `examples` list | Discovered from `workspace/pr-dry-run/{family}-controlled-pilot/examples/{family}/lowcode/` |
| `example_output_format` | `{family}-post-merge-clean-checkout-validation.json` `.examples[].output_format` |
| `generation_date` | `datetime.now(timezone.utc).isoformat()` at render time |

---

## Q5: Which sections must be adapted for LowCode examples?

The README must describe the LowCode API specifically — not the full Aspose product:

1. **Overview** must reference the `Aspose.{Family}.LowCode` namespace and explain single-step processing
2. **Examples table** lists only the validated LowCode classes (`HtmlConverter`, `Converter`, etc.)
3. **No** references to full Aspose features (charting, mail merge, pivot tables)
4. **Words controlled pilot note**: README must mention only 4 approved types (Converter, Watermarker, Splitter, Replacer)
5. **Run commands** must use actual directory names from the package (`examples/cells/lowcode/html-converter`)

---

## Q6: Where should README generation integrate?

**Primary integration:** `src/plugin_examples/__main__.py` → `publish-pr` handler

- After `example_dirs` is resolved from `package_path`
- Before `build_pr()` and `create_github_pr()` are called
- Fires for **both dry-run and live** — README must be in every package
- `github_pr_publisher.py` already picks up all files in `package_path` not in `_EXCLUDED_FILENAMES`; `README.md` is not excluded — no changes to publisher needed

**Secondary integration:** `render-root-readme` CLI command for standalone preview.

---

## Q7: Blockers

| Item | Status | Resolution |
|---|---|---|
| Jinja2 not in pyproject.toml | **BLOCKING** | Add `Jinja2>=3.1` to `[project] dependencies`; run `pip install -e .` |
| `templates/root-readme/` missing | Minor | Created in Phase 1 |
| README not in existing packages | Informational | Sprint motivation confirmed; no backfill of remote repos needed |

---

## Gate 0 Result

**PASS** — No remote write performed. Implementation can proceed.
