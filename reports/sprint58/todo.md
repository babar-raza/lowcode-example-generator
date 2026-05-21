# Sprint 58 Todo

**Sprint:** 58
**Goal:** Closure repair, 42/42 regeneration, package-authority proof, README/publication hardening
**Git HEAD at start:** `052f1a5429ce7a18e34c30bf1697ade477c15b33`
**Date:** 2026-05-21

---

## Phase Checklist

| Phase | Name | Status | Output |
|-------|------|--------|--------|
| 0 | Sprint 57 closure audit | IN_PROGRESS | reports/sprint58/00-01-02 + commands.log + todo.md + evidence-contract.json |
| 1 | Lane governance setup | PENDING | reports/sprint58/sprint-state.json + lane-ownership.md |
| 2 | pdf-pdf-aconverter fix + regeneration | PENDING | pdf.yml fix + regeneration + 42/42 proof |
| 3 | Real package-grounded authority proof | PENDING | reflection-ledger.json + xml-doc-ledger.json + runtime-probe-ledger.json + io-authority-evidence-matrix.json |
| 4 | Consistency scan | PENDING | consistency-scan-report.json + any failing tests |
| 5 | Per-example 42/42 regeneration | PENDING | reports/sprint58/regeneration/per-example/ (42 files, 15 fields each) |
| 6 | Destination deep audit | PENDING | deep-destination-audit.json + per-family reports |
| 7 | README gate + branch auto-delete | PENDING | implementation + dry-run tests |
| 8 | Hygiene before/after | PENDING | root-clutter-audit-before.md + root-clutter-audit-after.md |
| 9 | Process/skill creation (close Lane J) | PENDING | 9 process documents |
| 10 | Full test suite | PENDING | test-run.log (2816+ pass, 0 fail) |
| 11 | Final evidence bundle | PENDING | bundle.zip (25+ files) + SHA256 + bundle-manifest.json |

---

## Per-Phase Acceptance Criteria

### Phase 0 — DONE when:
- [x] 00-sprint57-evidence-audit.md created with all 11 defects classified
- [x] 01-sprint57-claim-vs-proof-matrix.md created (20 claims classified)
- [x] 02-corrected-state.md created
- [x] commands.log started
- [x] todo.md created (this file)
- [ ] evidence-contract.json created with all 25+ categories defined

### Phase 1 — DONE when:
- [ ] sprint-state.json created with 11 lanes, all PENDING
- [ ] lane-ownership.md created

### Phase 2 — DONE when:
- [ ] pdf.yml updated: `using Aspose.Pdf.Text;` in PdfAConverter.REQUIRED
- [ ] Regression test added for PdfAConverter constraint
- [ ] pdf-pdf-aconverter regenerated and built successfully
- [ ] Ledger updated: 42/42 generated, built, run_passed

### Phase 3 — DONE when:
- [ ] reflection-ledger.json created (DLL reflection output per package)
- [ ] xml-doc-ledger.json created (XML doc parse per package)
- [ ] runtime-probe-ledger.json created (assembly probe per package)
- [ ] io-authority-evidence-matrix.json created: 42 types, all with external proof
- [ ] Zero `"authority_source": "contract_only"` entries

### Phase 4 — DONE when:
- [ ] consistency-scan-report.json created
- [ ] Zero unresolved drift between package authority, FA contracts, configs, manifests
- [ ] New tests added for any newly found drift

### Phase 5 — DONE when:
- [ ] reports/sprint58/regeneration/per-example/ directory exists
- [ ] 42 JSON files, each with: scenario_id, family, type_name, generation_status, build_status, run_status, gate_results, diff_hash, fixture_path, output_path, generated_at, build_output, run_output, gate_verdict, notes
- [ ] full-regeneration-ledger.json updated: 42/42

### Phase 6 — DONE when:
- [ ] deep-destination-audit.json created per family (6 files)
- [ ] Each entry has: file_path, sha, content_snippet, package_version, api_calls_verified, readme_verified

### Phase 7 — DONE when:
- [ ] github_pr_merger.py has `allow_branch_auto_delete` flag implemented
- [ ] Dry-run branch auto-delete test added (no real API call without approval)
- [ ] README mandatory gate implemented and tested

### Phase 8 — DONE when:
- [ ] root-clutter-audit-before.md: current state
- [ ] root-clutter-audit-after.md: post-cleanup state
- [ ] fixture-layout-audit.md and generated-output-layout-audit.md

### Phase 9 — DONE when:
- [ ] 9 process documents created in reports/sprint58/lanes/lane-J/
- [ ] lane-J status set to COMPLETE in sprint-state.json

### Phase 10 — DONE when:
- [ ] Full test suite run: 0 failed
- [ ] test-run.log captured in reports/sprint58/lanes/lane-I/
- [ ] git-status.txt captured (clean state proof)

### Phase 11 — DONE when:
- [ ] Bundle ZIP contains 25+ meaningful files
- [ ] bundle-manifest.json with SHA256 for each file
- [ ] bundle-validator.py runs and passes (zero PENDING blocking evidence)
- [ ] Overall bundle SHA256 recorded

---

## Sprint 58 Closure Conditions

Sprint 58 is COMPLETE only when:
1. All 12 phases DONE
2. Lane J not PENDING
3. evidence-contract.json shows all blocking categories PRESENT
4. 42/42 regeneration proven (per-example)
5. Test suite 0 failed
6. Bundle validation passes (no PENDING blocking evidence)
7. commands.log is complete
8. git-status.txt (end) shows committed clean state
