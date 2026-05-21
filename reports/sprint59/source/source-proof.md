# Source Proof — Sprint 59 Phase 2

**Date:** 2026-05-21
**Commit:** `cf0919a`

---

## Changed Files

| File | Purpose | Commit |
|------|---------|--------|
| `pipeline/configs/families/pdf.yml` | PdfAConverter: add `using Aspose.Pdf.Text;` to per_type_constraints.PdfAConverter.required | `cf0919a` |
| `src/plugin_examples/publisher/github_pr_merger.py` | Add `_api_delete()`, `_LOWCODE_BRANCH_PREFIXES`, `delete_branch_after_merge()` | `cf0919a` |
| `tests/unit/test_llm_generation.py` | Add `TestPdfAConverterConstraint` class (3 tests) | `cf0919a` |
| `tests/unit/test_merge_governance.py` | Add `TestBranchAutoDelete` class (7 tests) | `cf0919a` |

---

## What Each Change Does

### pdf.yml — PdfAConverter constraint
```yaml
# Added to per_type_constraints.PdfAConverter.required:
- "using Aspose.Pdf.Text;"
```
Root cause fix for Sprint 57 defect D11: LLM generated code using `TextFragment` without the required namespace import. The validator now checks for this literal string in generated C#.

### github_pr_merger.py — Branch auto-delete
```python
_LOWCODE_BRANCH_PREFIXES = ("lowcode-pilot-", "lowcode-wave-")

def _api_delete(url, headers): ...

def delete_branch_after_merge(
    owner, repo, branch_ref, github_token,
    allow_branch_auto_delete=False,  # must opt-in
    dry_run=True,                     # safe default
) -> dict: ...
```
Safety rules:
1. Only `lowcode-pilot-*` and `lowcode-wave-*` prefixes eligible
2. `allow_branch_auto_delete=False` — must explicitly opt in
3. `dry_run=True` — never deletes without explicit `dry_run=False`

### test_llm_generation.py — TestPdfAConverterConstraint
- `test_pdfaconverter_config_requires_using_aspose_pdf_text` — validates yaml has the constraint
- `test_pdfaconverter_code_missing_using_pdf_text_fails_validation` — code without using fails
- `test_pdfaconverter_code_with_using_pdf_text_passes_validation` — code with using passes

### test_merge_governance.py — TestBranchAutoDelete
7 tests covering: dry_run default, non-lowcode skip, feature branch skip, flag disabled skip, lowcode-wave prefix, no API call on dry_run, no API call when flag disabled.

---

## Source Hashes

See `source-hashes.json` for SHA256 per file after commit `cf0919a`.

## Source Diff

See `source-diff.patch` — 370 lines covering all 4 files.

---

## Verification

```bash
git show cf0919a --stat
# 4 files changed, 313 insertions(+), 1 deletion(-)

git show cf0919a --name-only
# pipeline/configs/families/pdf.yml
# src/plugin_examples/publisher/github_pr_merger.py
# tests/unit/test_llm_generation.py
# tests/unit/test_merge_governance.py
```
