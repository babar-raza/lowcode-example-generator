# Live Publication Blockers — Sprint 61 Phase 8

## Status

Sprint 61 delivers audit and correction plan. README push to target repos is
**deferred to Sprint 62**.

---

## Active Blockers

### 1. Approval Gate (All 41 scenarios)

Pushing README I/O corrections requires:

```
PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH
```

This is enforced by the `check_readme_audit_gate` gate wired into `publish-pr`
live mode (Sprint 61 Phase 5). No README correction can be pushed without this.

### 2. Manual Classification Required (4 scenarios)

| Scenario | Reason |
|----------|--------|
| `words-mail-merger` | Input is data source (no `input.EXT` literal in Program.cs) |
| `words-report-builder` | Input is data source + template |
| `pdf-pdf-aconverter` | No local package — cannot parse Program.cs |
| `pdf-text-extractor` | Output is stdout — special README treatment needed |

### 3. Version Drift (2 families)

| Family | Published Version | Latest NuGet |
|--------|------------------|--------------|
| words | 26.4.0 | 26.5.0 |
| diagram | 26.4.0 | 26.5.0 |

Words and Diagram target repos are behind latest NuGet. Version drift push
requires a separate `Directory.Packages.props` update PR.

### 4. No Local Package (2 scenarios)

- `pdf-pdf-aconverter` — deferred (no local package)
- `pdf-text-extractor` — deferred (no local package)

---

## Sprint 62 Actions Required

1. Push I/O format sections to 38 auto-correctable READMEs
   - Requires `APPROVE_README_PUSH`
   - Source: `readme-io-correction-plan.json`
2. Manually author README I/O sections for 4 special cases
3. Resolve version drift for words and diagram families
4. Verify `check_readme_audit_gate` passes after push

---

## Evidence Files

| File | Description |
|------|-------------|
| `correction-package-ledger.json` | Per-scenario ledger (42 entries) |
| `readme-update-package-summary.json` | Machine-readable summary |
| `readme-update-package-summary.md` | Human-readable summary |
| `live-publication-blockers.json` | Machine-readable blockers |
| `live-publication-blockers.md` | This document |
| `../readme/readme-io-correction-plan.json` | Per-example correction text |
