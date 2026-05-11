# Full-Completion Remediation Architecture

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/full-completion-remediation-architecture.json`
**Verdict:** REMEDIATION_ARCHITECTURE_DEFINED

## 6 Components

### 1. Planned Scenario Contract

Every scenario declares upfront: required_options_class, required_inputs, known_invalid_patterns, few_shot_required, completion_blocker. Data sourced from type-role-classification and backlog.

### 2. Scenario Completion Queue

State machine replacing binary pass/exclude. States: discovered > classified > contract_defined > ready_to_generate > [blocked_*] > generation_in_progress > validated > packaged > pr_published > merged. Backlogged scenarios can re-enter ready_to_generate after fixes.

### 3. Learning/Repair System

- Backlog failures become negative constraints in future prompts
- Successful code becomes few-shot templates
- Code validator issues trigger targeted repair (not just warnings)
- Repair prompts include API catalog excerpts

### 4. Backlog-to-Taskcard Bridge

Auto-create taskcard entries when scenarios enter backlogged state.

### 5. Readiness Rank Upgrade

New fields: full_completion_possible, true_completion_rate, next_blocker_to_clear, expected_completion_after_fixes.

### 6. Completion Policy

- **Controlled pilot:** Partial publishing allowed with backlog for excluded scenarios
- **Full family launch:** All candidates must be merged or permanently waived
- **Monthly updates:** Regression protection — previously merged examples must still build+run
