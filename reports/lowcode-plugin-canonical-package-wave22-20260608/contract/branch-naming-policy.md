# Branch Naming Policy

Date: 2026-06-08

## LowCode Example Repos
Pattern: `lowcode-examples-<family>-<descriptor>`
Example: `lowcode-examples-cells-readme-io-final`

## Plugin Example Repos (Non-LowCode)
Wave 22+ new branches: `plugins/wave<N>/<family>-plugin-examples`
Example: `plugins/wave22/barcode-plugin-examples`

## Legacy Branches (open PRs from Wave 19)
The following open PR branches retain their Wave 19 names. They cannot be renamed without
closing and reopening the PR, which would lose PR history and review context.
These are grandfathered until merged:
- `lowcode/wave19/barcode-plugin-examples` (BarCode PR#1)
- `lowcode/wave19/svg-plugin-examples` (SVG PR#1)
- `lowcode/wave19/cad-plugin-examples` (CAD PR#1)

## Post-Merge Cleanup
All source branches must be deleted after PR merge unless:
1. Branch is a long-lived feature branch (explicitly retained with documented reason)
2. Branch deletion is pending human approval
