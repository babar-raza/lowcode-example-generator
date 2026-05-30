# Publication Rollback Plan — lowcode-systemization-pass3-20260530

If a published example has issues post-merge:
1. Revert PR in example repo
2. Fix issue through canonical pipeline (pilot_run.py)
3. Re-submit PR after validation
4. Update example.manifest.json with new status
