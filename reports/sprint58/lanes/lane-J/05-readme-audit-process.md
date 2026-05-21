# Process: README Audit and Healing

**Process ID:** LANE-J-05
**Version:** Sprint 58
**Date:** 2026-05-21

---

## Overview

Sprint 57 Defect D08: README audit was listed as open in the backlog, but `readme-update-matrix.md` contained only requirements — no actual audit was performed.

Sprint 58 Phase 7 implements a README audit gate and documents the process.

---

## README Healing System Components

| Module | Path | Purpose |
|--------|------|---------|
| `readme_facts.py` | `src/plugin_examples/publisher/readme_facts.py` | Extracts API methods and formats from Program.cs |
| `readme_auditor.py` | `src/plugin_examples/publisher/readme_auditor.py` | 15 checks per README |
| `readme_renderer.py` | `src/plugin_examples/publisher/readme_renderer.py` | Renders README from facts |

---

## README Facts Extraction

`readme_facts.py` extracts from `Program.cs`:
- API method names (4 patterns: static, instance, variable, async)
- Input/output format claims
- Namespace/package references

Noise filters (not extracted): `_IGNORE_METHODS`, `_IGNORE_CLASSES`, `_IGNORE_OPTION_CLASSES`

**Fail-closed rule:** Missing or unverified facts → ValueError, blocks README generation.

---

## README Auditor (15 Checks)

| Check | Description |
|-------|-------------|
| format_claim | README format claim matches Program.cs I/O |
| snippet | Code snippet present and compilable |
| xlsx_cross_family | xlsx output not claimed for non-Cells family |
| api_method | API method name matches reflection catalog |
| package_version | NuGet version in README matches Directory.Packages.props |
| ... | (remaining 10 checks) |

---

## Audit Approval Gate

README pushes require explicit approval:
```
PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH
```

This approval must be set before any `push-readme` command runs. Never bypass.

---

## Audit Process Steps

### Step 1: Sampled Audit

For each family, sample ≥3 examples and verify README.md presence:
```
GET /repos/{owner}/{repo}/contents/Examples/{ExampleName}/README.md
```

### Step 2: Content Verification

For sampled examples, verify README contains:
- Correct API method name
- Correct I/O format description
- NuGet package reference with correct version
- C# code snippet

### Step 3: Write Audit Results

Write to: `reports/sprint58/destination/readme-audit-results.json`

---

## Acceptance Criteria

- Sampled audit: ≥3 examples per family, all have README.md
- No format claim mismatches in sampled examples
- Verdict: `SAMPLED_AUDIT_PASSED`
- Approval gate: documented (not yet activated — Sprint 58 performs sampled audit only)
