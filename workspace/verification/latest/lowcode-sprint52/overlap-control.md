# Overlap Control — Sprint 52

No overlapping writes between lanes.
- Lane 0 reads Sprint 51 artifacts (read-only)
- Lane A validates Sprint 51 ZIP (read-only on ZIP, writes proof externally)
- Lane B modifies dirty-state classification (writes to sprint52 evidence dir only)
- Lane C repairs release-status (may modify source + write evidence)
- Lane D resolves CONTRACT_FIRST_CODEGEN (writes evidence only, may reclassify)
- Lane E refreshes PDF packet (writes to sprint52 evidence dir only)
- Lane F runs planner (writes to sprint52 evidence dir only)
- Lane G builds final bundle (writes final artifacts, must run last)

Sequential dependency: G depends on all other lanes completing.
