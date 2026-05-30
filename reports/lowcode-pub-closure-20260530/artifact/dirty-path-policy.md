# Dirty Path Policy — lowcode-pub-closure-20260530

## Tracked dirty files at K1 check: 9
M workspace/pr-dry-run/cells-controlled-pilot/README.md
 M workspace/pr-dry-run/words-controlled-pilot/README.md
 M workspace/verification/latest/cells-readme-backfill-simulation.json
 M workspace/verification/latest/cells-root-readme-audit.json
 M workspace/verification/latest/cells-root-readme-render-result.json
 M workspace/verification/latest/release-status.json
 M workspace/verification/latest/words-readme-backfill-simulation.json
 M workspace/verification/latest/words-root-readme-audit.json
 M workspace/verification/latest/words-root-readme-render-result.json

## Policy
- bin/obj: gitignored; any tracked copies removed via git rm --cached
- workspace/pr-dry-run: gitignored; builds stay local
- workspace/verification/latest: committed when updated
- reports/: committed via exact-path staging
