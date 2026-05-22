# Sprint 61 — README Sync Architecture Plan

Source: reports/sprint61/ (sprint61-sprint60-false-closure-kill-switch-20260521)
Reconciliation Date: 2026-05-22

## Plan Items from Sprint 61 README I/O Correction Plan

Source file: reports/sprint61/readme/readme-io-correction-plan.md

| # | Item | Sprint 61 Disposition | Sprint 67 Status |
|---|------|-----------------------|-----------------|
| 1 | 42-example README I/O correction text (41/42 ready) | DEFERRED to Sprint 62 | SUPERSEDED — Sprint 62 closed all 42 |
| 2 | Push corrections to destination repos | DEFERRED to Sprint 62 | CARRIED_FORWARD — still BLOCKED_BY_APPROVAL as of Sprint 66 |
| 3 | README gate (APPROVE_README_PUSH) | Wired in Sprint 61 Phase 5 | CLOSED — Sprint 62 hardened semantics |
| 4 | pdf-pdf-aconverter special case | No local package — deferred | CLOSED — Sprint 62 found Program.cs, resolved as DUAL_SOURCE |
| 5 | Words/Diagram version drift | DEFERRED to Sprint 62 | CARRIED_FORWARD — dry-run ready, publication blocked |

## Sprint 61 README Sync Architecture — Current State

Sprint 61 introduced `src/plugin_examples/publisher/readme_facts.py` and `readme_auditor.py`.
These modules remain active in the pipeline.

| Component | Sprint 61 State | Sprint 67 State |
|-----------|----------------|----------------|
| readme_facts.py | Active — extracts API methods/formats from Program.cs | Active (Sprint 66 confirmed) |
| readme_auditor.py | Active — 15 checks including format-claim, snippet | Active (Sprint 66 confirmed) |
| readme_audit_gate.py | Active — blocks pub on missing/shallow/failed audit | Active — hardened in Sprint 62 |
| check_readme_audit_gate | Wired in publish-pr --publish | Active (Sprint 66 confirmed) |

## Sprint 61 Open Gaps — Now Resolved

| Gap (Sprint 61) | Resolution |
|----------------|-----------|
| 0/42 IO_DOC_MATCH before Sprint 61 | Sprint 62: 42/42 README I/O text ready; Sprint 66: 42/42 corrected packages in handoff |
| api_verified=0/42 | Sprint 62: api_verified=CONFIRMED_FROM_PROGRAMCS for 42/42 |
| readme_audit_gate not imported | Sprint 61 wired; Sprint 62 hardened |
| EvidenceValidator optional | Sprint 61 wired; Sprint 62 mandatory |

## Sprint 61 Open Gaps — Still Open

| Gap (Sprint 61) | Current Status | Sprint 67 Action |
|----------------|----------------|-----------------|
| Push README corrections to destination repos | BLOCKED_BY_APPROVAL (Sprint 66) | Phase 8: activation check |
| api_verified=True via NuGet API introspection | BACKLOG — CONFIRMED_FROM_PROGRAMCS is current ceiling | No Sprint 67 action |
| FormImporter | PERMANENTLY_DEFERRED | No Sprint 67 action |

## Sprint 61 README Sync Architecture — Residual Gaps for Sprint 67

Sprint 61 README sync architecture did NOT address:
1. Root README operation-kind-aware cardinality display (merger N→1, splitter 1→N)
   → Sprint 66 S66-D1: root README files present but cardinality missing
   → Sprint 67 Phase 2: MUST repair

2. README display strategy in format-authority contracts uses plain `xlsx`→`xlsx` without cardinality
   → Format authority contracts have `readme_display_strategy.input_format/output_format` only
   → No `cardinality` field in `readme_display_strategy`
   → Sprint 67 Phase 2: Add cardinality annotation in root README content (not contract-level change)

These gaps mean the Sprint 61 README Sync plan is PARTIALLY_SUPERSEDED:
- Core sync mechanism (facts/auditor/gate) is proven and active
- Root README display layer is incomplete (Sprint 67 target)
