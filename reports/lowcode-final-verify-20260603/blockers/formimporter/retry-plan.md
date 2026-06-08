# FormImporter Retry Plan

1. Monitor NuGet for Aspose.PDF > 26.5.0
2. When new version appears:
   a. Update Directory.Packages.props in pdf repo
   b. Regenerate FormImporter example with 3 JSON fixture formats
   c. Run dotnet build + dotnet run
   d. If Process() succeeds, create PR to add FormImporter example
   e. If still fails, update upstream-bug-status.md
3. Check weekly or on release announcement
