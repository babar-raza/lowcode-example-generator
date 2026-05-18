# Publication Rollback Packet — Sprint 36

## If a PR was published and needs to be closed:

```bash
# Close individual PR (replace URL with actual)
gh pr close https://github.com/aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples/pull/N
```

## If a branch needs to be deleted after close:
```bash
gh api repos/aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples/git/refs/heads/plugin-examples/pdf/BRANCH_NAME -X DELETE
```

## Rollback conditions:
- Security example absent from PR#7
- bin/obj files present in any package
- Wrong target repo
- Example count mismatch
