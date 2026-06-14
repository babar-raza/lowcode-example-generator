# Rollback Procedure

This document describes how to revert pipeline changes or published examples when a release introduces regressions.

## Pipeline Rollback (Source Code)

### Revert a Wave Commit

If a wave commit introduces a regression:

```bash
# Identify the commit to revert
git log --oneline -10

# Revert the specific wave commit
git revert <commit-sha>

# Verify tests still pass
PYTHONPATH=src pytest tests/ -v --timeout=60 --cov=src/plugin_examples --cov-fail-under=70

# Verify doctor health
PYTHONPATH=src python -m plugin_examples doctor
```

### Revert a Configuration Change

Family configs are under `pipeline/configs/families/`. To revert a config change:

```bash
# Restore the previous version of a family config
git checkout HEAD~1 -- pipeline/configs/families/<family>.yml

# Verify the config is valid
PYTHONPATH=src python -m plugin_examples validate-config --family <family>
```

## Published Example Rollback (Target Repositories)

### Close an Open PR

If a PR with bad examples was created but not merged:

```bash
# Close the PR without merging (requires GITHUB_TOKEN)
gh pr close <PR-NUMBER> --repo <org>/<repo> --comment "Reverted due to regression"
```

### Revert a Merged PR

If bad examples were already merged to a target repository:

```bash
# Clone the target repo
git clone https://github.com/<org>/<repo> /tmp/rollback-target
cd /tmp/rollback-target

# Create a revert PR
git checkout -b revert-bad-examples
git revert <merge-commit-sha>
git push origin revert-bad-examples
gh pr create --title "revert: rollback bad examples from wave N" --body "Reverting examples due to regression found in pipeline wave N."
```

### Re-Run Pipeline After Rollback

After reverting:

1. Run the pipeline in dry-run mode to verify the fix:
   ```bash
   PYTHONPATH=src python -m plugin_examples run --family <family> --dry-run --template-mode
   ```

2. If the fix is confirmed, run the full pipeline to regenerate correct examples.

## Evidence

All rollback actions must be documented in the current wave's sprint evidence:
- What was reverted and why.
- Which published examples were affected.
- Verification that the rollback restored correct behavior.
