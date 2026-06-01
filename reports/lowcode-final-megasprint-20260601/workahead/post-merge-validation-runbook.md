# Post-Merge Validation

1. For each merged PR:
   - `gh pr view <number> --repo <repo>` — verify state=MERGED
   - Clone target repo, verify examples directory exists
   - Run `dotnet build` on each example
2. Record results in publication/post-merge-verification.md
