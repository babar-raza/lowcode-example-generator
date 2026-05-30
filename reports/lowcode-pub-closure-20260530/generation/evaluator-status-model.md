# Evaluator Status Model — lowcode-pub-closure-20260530

## Status Taxonomy (post-fix)

| Verdict | Condition | Publishable |
|---------|-----------|-------------|
| CANONICAL_TEMPLATE_GENERATION_PASS | template_mode=True, skip_run=False, build_passed>0 | YES |
| CANONICAL_LLM_GENERATION_PASS | template_mode=False, gen_mode=llm, build+run pass | YES |
| FULL_E2E_PASSED | all_required_passed, not dry_run, run_passed>0 | YES |
| PR_READY | all_required_passed, not dry_run | YES |
| PR_DRY_RUN_READY | all_required_passed, dry_run | NO (approval blocked) |
| DATA_FLOW_PROTOTYPE_ONLY | template_mode+skip_run=True, or build_passed=0 | NO |
| BLOCKED_* | hard failure | NO |

## Change made (B1)
Old: `if ctx.template_mode or ctx.skip_run: return "DATA_FLOW_PROTOTYPE_ONLY"`
New: split skip_run (always cap) vs template_mode (cap only if build_passed=0)

## Reason
Pass4 runs had build_passed=42, run_passed=42 in template_mode. The old ceiling
incorrectly labeled a successful full E2E run as prototype-only.

## Regression safety
- `test_template_mode_produces_data_flow_prototype`: still passes (skip_run=True path)
- New: `test_template_mode_with_build_pass_produces_canonical_template_pass`
- New: `test_template_mode_skip_run_true_stays_data_flow_prototype`
- New: `test_template_mode_with_build_fail_stays_data_flow_prototype`
- New: `test_canonical_template_pass_is_publishable`
