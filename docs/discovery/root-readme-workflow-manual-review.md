# Root README Workflow Manual Verification Review

**Review date:** 2026-05-03
**Sprint reviewed:** Root README Template and Update Workflow Sprint
**Commit hash:** b501f67cef9ba3a87b86c00066ba384954c62910
**Reviewed by:** pipeline_agent

---

## Purpose

Manual verification of every claim in the Root README Template and Update Workflow Sprint
against actual code, test results, and generated output files. Goal: confirm whether
`ROOT_README_TEMPLATE_WORKFLOW_READY` is fully sound, identify any gaps, apply fixes,
and declare whether the PDF Assembly Deduplication Sprint may start.

---

## Claim Audit Results (30 claims)

| # | Claim | Verdict | Notes |
|---|---|---|---|
| 1 | Jinja2 dependency correctly declared | VERIFIED | `Jinja2>=3.1` in `pyproject.toml`; `jinja2 3.1.6` importable |
| 2 | Jinja2 importable from venv | VERIFIED | `import jinja2; print(jinja2.__version__)` → `3.1.6` |
| 3 | Template path resolves inside repo root | VERIFIED | `parents[3]` from `readme_renderer.py` → repo root; `exists()` True |
| 4 | Template generic, not hardcoded Cells/Words | VERIFIED + FIXED | No hardcoded family names; title had redundant "for .NET" — fixed |
| 5 | Template has all required sections | VERIFIED | All 9 sections present including `## License` |
| 6 | Template does not mention central repo | VERIFIED | No `aspose-plugins-examples-dotnet` in template |
| 7 | Template does not mention PDF in Cells/Words output | VERIFIED | No hardcoded PDF family reference; paths use `{{ family }}` |
| 8 | Renderer uses family config, not hardcoded names | VERIFIED | Reads `github.published_plugin_examples_repo.owner/.repo` |
| 9 | Renderer excludes failed/blocked examples | VERIFIED | Includes only examples passed as list; CLI passes only validated dirs |
| 10 | Renderer uses package version evidence correctly | VERIFIED | Reads `{family}-live-pr-result.json.nuget_version`; fallback to `Directory.Packages.props` |
| 11 | Auditor catches stale version | VERIFIED | `test_root_readme_auditor_detects_stale_package_version` passes |
| 12 | Auditor catches missing examples | VERIFIED | `test_root_readme_auditor_detects_missing_example` passes |
| 13 | Auditor catches extra examples | VERIFIED | `extra_examples` logic checks table names vs context |
| 14 | Auditor catches central repo references | VERIFIED | `_CENTRAL_REPO_PATTERNS` checked; `aspose-plugins-examples-dotnet` triggers failure |
| 15 | Auditor catches catalog symbol noise | VERIFIED | `test_root_readme_auditor_detects_catalog_symbol_noise` passes |
| 16 | CLI `render-root-readme` exists | VERIFIED | Subparser added; both CLI tests pass |
| 17 | CLI exits non-zero on audit failure | VERIFIED | Lines 1149-1151: `if not audit_result.passed: return 1` |
| 18 | `publish-pr` renders README before PR build/create | VERIFIED | Lines 512-563 fire before `build_pr()` at line 570 |
| 19 | Live publish blocks if README audit fails | **NEEDS_FIX → FIXED** | Original only warned; fixed to `if live_mode: return 1` |
| 20 | Dry-run READMEs exist for Cells and Words | VERIFIED | Both files exist; cells 5081 bytes, words 4337 bytes |
| 21 | Cells README has exactly 9 examples | VERIFIED | `found_example_count=9` in audit JSON; 9 table rows confirmed |
| 22 | Words README has exactly 4 examples | VERIFIED | `found_example_count=4`; converter, replacer, splitter, watermarker |
| 23 | Cells README does not mention Words | VERIFIED | Cross-family contamination check passes; no `Aspose.Words` in cells README |
| 24 | Words README does not mention Cells | VERIFIED | Cross-family contamination check passes; no `Aspose.Cells` in words README |
| 25 | README run commands match real package paths | VERIFIED | `examples/{family}/lowcode/<name>` matches disk structure |
| 26 | `followup-root-readme-template-workflow` closed with evidence | VERIFIED | Audit JSONs exist; 655 tests pass; dry-run renders pass |
| 27 | `followup-readme-symbols-from-catalog` remains open | VERIFIED | Status `open`; next action documented |
| 28 | Master plan has sprint section | VERIFIED | `## Root README Template and Update Workflow Sprint` in `linked-nibbling-hamster.md` |
| 29 | No remote write occurred | VERIFIED | `no_remote_write_performed=true` in all evidence; no git push |
| 30 | PDF work has not started | VERIFIED | No PDF-related files changed; `followup-pdf-reflection-dedup` still open |

---

## Gaps Found and Fixed

### GAP-1 (HIGH): `publish-pr` live mode did not block on README audit failure

**Finding:** The `publish-pr` handler only printed a WARNING on audit failure regardless of mode.
The preflight review (`root-readme-template-preflight-review.json`) explicitly states:
> `audit_blocks_packaging: "README audit failure blocks package step to prevent publishing stale or broken READMEs"`

This design intent was not implemented in the code.

**File:** [src/plugin_examples/__main__.py](../../src/plugin_examples/__main__.py) (lines 553-556 original)

**Original:**
```python
if not _readme_audit.passed:
    print(f"WARNING: README audit failed for {family}: {_readme_audit.warnings}")
```

**Fixed to:**
```python
if not _readme_audit.passed:
    if live_mode:
        print(f"ERROR: README audit FAILED for {family} — blocking live publish: {_readme_audit.warnings}")
        return 1
    else:
        print(f"WARNING: README audit failed for {family} (non-blocking in dry-run): {_readme_audit.warnings}")
```

**Tests added:** `TestPublishPrLiveBlocksOnAuditFailure` (2 tests) in `test_readme_renderer.py`

---

### GAP-2 (LOW): README title had redundant "for .NET"

**Finding:** Template title `# {{ display_name }} LowCode for .NET Examples` with
`display_name = "Aspose.Cells for .NET"` produced `"Aspose.Cells for .NET LowCode for .NET Examples"` — "for .NET" appeared twice.

**File:** [templates/root-readme/lowcode-family-readme.md.j2](../../templates/root-readme/lowcode-family-readme.md.j2) (line 1)

**Fixed to:** `# {{ display_name }} LowCode Examples`

**Result:**
- Cells: `# Aspose.Cells for .NET LowCode Examples`
- Words: `# Aspose.Words for .NET LowCode Examples`

---

## Verification Commands Run

```bash
# Compile check
PYTHONPATH=src .venv/Scripts/python.exe -m compileall src -q   # EXIT 0

# Jinja2
.venv/Scripts/python.exe -c "import jinja2; print('jinja2', jinja2.__version__)"  # jinja2 3.1.6

# DllReflector
dotnet build tools/DllReflector/DllReflector.csproj -c Release --nologo -v q  # 0 errors

# Unit tests
PYTHONPATH=src .venv/Scripts/python.exe -m pytest tests/unit -q --timeout=60  # 655 passed

# Dry-run renders
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples render-root-readme --family cells --package-path workspace/pr-dry-run/cells-controlled-pilot --promote-latest  # PASS
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples render-root-readme --family words --package-path workspace/pr-dry-run/words-controlled-pilot --promote-latest  # PASS
```

---

## README Render Results (Post-Fix)

| Family | File | Bytes | Examples | Title | Audit |
|---|---|---|---|---|---|
| Cells | `workspace/pr-dry-run/cells-controlled-pilot/README.md` | 5081 | 9 | `# Aspose.Cells for .NET LowCode Examples` | PASS |
| Words | `workspace/pr-dry-run/words-controlled-pilot/README.md` | 4337 | 4 | `# Aspose.Words for .NET LowCode Examples` | PASS |

---

## Files Changed in This Review

| File | Change |
|---|---|
| `src/plugin_examples/__main__.py` | Fixed: publish-pr live mode now blocks on README audit failure |
| `templates/root-readme/lowcode-family-readme.md.j2` | Fixed: title removes redundant "for .NET" |
| `tests/unit/test_readme_renderer.py` | Added: `TestPublishPrLiveBlocksOnAuditFailure` (2 tests; total 21) |
| `workspace/verification/latest/root-readme-workflow-manual-review.json` | New: this review in JSON form |
| `docs/discovery/root-readme-workflow-manual-review.md` | New: this document |

---

## Taskcard Status

| Taskcard | Status | Decision |
|---|---|---|
| `followup-root-readme-template-workflow` | CLOSED (verified) | Remains closed — gaps found and fixed within this review |
| `followup-readme-symbols-from-catalog` | OPEN | Remains open — next action: pull method names from `all-family-lowcode-discovery.json` |
| `followup-pdf-reflection-dedup` | OPEN | Remains next sprint — cleared to start after this review passes |

---

## Test Count

- **655 total** (634 baseline + 19 from README sprint + 2 from this review)
- `TestPublishPrLiveBlocksOnAuditFailure`: 2 tests, both pass

---

## Overall Verdict

**`ROOT_README_WORKFLOW_VERIFIED_READY_FOR_PDF`**

Two gaps were found and fixed within this review:
1. Live publish now correctly blocks on README audit failure (`return 1`)
2. Template title no longer has redundant "for .NET"

All 30 claims are VERIFIED or FIXED. No remote write. No PDF work started.

The PDF Assembly Deduplication Sprint (`followup-pdf-reflection-dedup`) is **approved to start next**.
