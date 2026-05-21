# Staging Plan — Sprint 59 Phase 1

**Date:** 2026-05-21

---

## Commit 1 — Source Changes (Sprint 58 repair: PdfAConverter + branch auto-delete)

```bash
git add pipeline/configs/families/pdf.yml
git add src/plugin_examples/publisher/github_pr_merger.py
git add tests/unit/test_llm_generation.py
git add tests/unit/test_merge_governance.py
git commit -m "fix(pdf): add PdfAConverter Aspose.Pdf.Text constraint; feat(merger): implement branch auto-delete with dry-run tests

- pipeline/configs/families/pdf.yml: PdfAConverter.required += 'using Aspose.Pdf.Text;'
- github_pr_merger.py: _api_delete(), _LOWCODE_BRANCH_PREFIXES, delete_branch_after_merge()
- test_llm_generation.py: TestPdfAConverterConstraint (3 tests)
- test_merge_governance.py: TestBranchAutoDelete (7 tests)"
```

---

## Commit 2 — Workspace Manifests (Sprint 58/59 regeneration state)

```bash
git add workspace/manifests/example-index.json
git add workspace/manifests/existing-examples-index.json
git add workspace/manifests/fixture-registry.json
git add workspace/manifests/package-lock.json
git add workspace/manifests/scenario-catalog.json
git commit -m "chore(workspace): update manifests from Sprint 58/59 all-family regeneration runs"
```

---

## Commit 3 — Workspace Verification Latest (Sprint 58/59 pipeline outputs)

```bash
git add workspace/verification/latest/
git commit -m "chore(verification): promote Sprint 58/59 all-family pipeline outputs (42/42 regenerated)"
```

---

## Commit 4 — Sprint 58 Evidence Bundle

```bash
git add reports/sprint58/
git commit -m "docs(sprint58): add Sprint 58 evidence bundle (76 files; Sprint 59 audit reclassifies as EVIDENCE_REPAIR_REQUIRED_NOT_CLOSED)"
```

---

## Commit 5 — Sprint 59 Evidence Bundle (at final closure)

```bash
git add reports/sprint59/
git commit -m "docs(sprint59): Sprint 59 closure repair bundle — IO_AUTHORITY_COMPLETE_DESTINATION_CONTENT_VERIFIED"
```

---

## Rules Followed

- No `git add .` or `git add -A`
- No `git reset --hard`
- No `git clean`
- Exact paths only for source files
- Directory-level add only for generated workspace outputs (all files are generated pipeline state)
- Each commit has a single logical purpose
