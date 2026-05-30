# Timestamp Source Repair — lowcode-systemization-pass3-20260530
Date: 2026-05-30

## Problem
pdf-controlled-pilot-pr11 (timestamp example) has source_run: null.
This means canonical_packager cannot drive it from source_run.
The example was assembled directly into pr-dry-run (WORKSPACE_RUN_COPY).

## Why source_run is null
The timestamp example requires:
1. A real TSA (Timestamp Authority) server endpoint
2. Network access during dotnet run
3. A valid TSA certificate chain

This is a network-dependent operation that cannot be run in isolated/offline mode.

## Decision
timestamp is EXCLUDED from pass3 publication candidates.
Reason: NETWORK_DEPENDENCY_BLOCKER — cannot generate canonical output without live TSA endpoint.

## Blocker Packet
- API proof: Aspose.Pdf.LowCode.TimestampEmbedder exists (reflection evidence)
- Failure mode: Requires network TSA endpoint at runtime
- Offline alternative: None (TSA signature inherently requires live endpoint)
- Retry condition: When a valid TSA endpoint credential is available
- Classification: NETWORK_DEPENDENCY_BLOCKER

## Impact on Publication Candidates
- pdf-controlled-pilot-pr11 removed from publication candidate set
- Timestamp example NOT publication-ready for pass3
- Total publication candidates: 41 (was 42 with timestamp)
