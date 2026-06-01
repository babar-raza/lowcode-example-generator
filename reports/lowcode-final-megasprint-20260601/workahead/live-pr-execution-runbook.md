# Live PR Execution Runbook

## Prerequisites
1. Set approval gate: `export PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`
2. Verify GH_TOKEN is set and has repo write access
3. Ensure all local gates pass (run validators)

## PR Creation (per family)
For each family in [cells, diagram, email, pdf, slides, words]:

```bash
cd workspace/pr-dry-run/<family>-controlled-pilot
gh pr create \
  --repo aspose-<family>-net/Aspose.<Family>.LowCode-for-.NET-Examples \
  --head lowcode-examples-<family>-readme-io-final \
  --title "Add LowCode examples for Aspose.<Family>" \
  --body "Generated, validated, and verified C# examples for Aspose.<Family>.LowCode namespace."
```

## Post-PR Verification
- Check each PR URL is accessible
- Verify CI checks pass
- Record PR URLs in publication/live-pr-results.json

## Merge (requires second gate)
```bash
export PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
gh pr merge <PR_NUMBER> --repo <repo> --squash
```
