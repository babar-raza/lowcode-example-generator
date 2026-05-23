# README Sync Architecture Review — Sprint 67

Date: 2026-05-22
Sprint: sprint67

## Architecture Components (Sprint 61 — still active)

| Component | File | Status |
|-----------|------|--------|
| readme_facts.py | src/plugin_examples/publisher/readme_facts.py | ACTIVE |
| readme_auditor.py | src/plugin_examples/publisher/readme_auditor.py | ACTIVE |
| readme_audit_gate.py | src/plugin_examples/publisher/readme_audit_gate.py | ACTIVE |
| check_readme_audit_gate | src/plugin_examples/__main__.py | ACTIVE — wired in publish-pr --publish |

## readme_facts.py (Sprint 61 architecture)

Extracts facts from Program.cs:
- API methods: 4 patterns (static, instance, variable, async)
- Input/output format extraction from file paths
- Noise filtering: _IGNORE_METHODS, _IGNORE_CLASSES, _IGNORE_OPTION_CLASSES
- Fail-closed: missing/unverified facts → ValueError (blocks README generation)

## readme_auditor.py (Sprint 61 + 62 architecture)

15+ checks including:
- Checks 1-15: Sprint 61 original (format-claim, snippet, xlsx-cross-family-guard, etc.)
- Checks 16-19: Sprint 62+ semantic (same-format converter, splitter/merger cardinality, extractor)

## Approval Gate Chain

```
publish-pr --publish
  └── check_readme_audit_gate()
        ├── APPROVE_README_PUSH token required
        ├── README audit must pass (15 checks)
        └── If audit fails: APPROVE_README_AUDIT_OVERRIDE required (records audit_override_used=True)
```

## Sprint 67 Assessment

The README sync architecture is functioning correctly. No code changes required.

**Gap identified**: Root README display layer (reports/sprint67/root-readme/) is separate from
the per-example README auditor. The root README is a summary document; it does not go through
`readme_auditor.py` checks. Cardinality in root READMEs is governed by the generation script
(`build_sprint67_root_readmes.py`) and the cardinality-audit.json, not by code gates.

**Recommendation**: For Sprint 68, add an EV rule that checks root README files for
cardinality markers. This sprint adds the test (test_readme_io_cardinality_display.py)
as a first step.
