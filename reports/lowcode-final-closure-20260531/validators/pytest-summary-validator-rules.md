# Pytest Summary Validator Rules — lowcode-final-closure-20260531
Generated: 2026-05-31T13:32:59

## Rules
1. full-pytest-summary.json must agree with full-pytest.log
2. Raw log with FAILED lines requires failed > 0 in summary
3. Raw log must contain final pytest summary line
4. pytest command in command-index must match summary
5. summary is generated from actual pytest result, not hand-authored

## Applied To
- Raw log: C:\Users\prora\OneDrive\Documents\GitHub\lowcode-example-generator-gitlab\reports\lowcode-final-closure-20260531\tests\full-pytest.log
- Passed: 3222
- Failed: 0
- Skipped: 18

## Verdict
PASS — 0 failures confirmed
