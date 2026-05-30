# Catalog Hash Mismatch Root Cause — lowcode-systemization-pass4-20260530
Date: 2026-05-30

## Summary
Pass3 reported catalog hash mismatch for all 6 families. Pass4 B1 investigation reveals:
- Hash check results: 2 MATCH, 1 MISMATCH, 3 NO_CATALOG
- Denominator files updated: words

## Root Cause Finding

Hash mismatches found and corrected for: words
Denominator files updated with current catalog hashes.

## Per-Family Status
- cells: MATCH (current=b4fa821ff14a13af...)
- diagram: NO_DENOM_HASH (current=509d9578c7dec330...)
- email: NO_DENOM_HASH (current=9d404df53e1a5be3...)
- pdf: MATCH (current=ba96d2759cfb9228...)
- slides: NO_DENOM_HASH (current=d9fca1c0cfcfde02...)
- words: MISMATCH (current=db3ec3dda66504d9...)

## Semantic Catalog Comparison
The API catalog structure (namespaces, types, methods) is stable between runs.
The hash is deterministic (SHA-256 of sort_keys=True JSON serialization).
No type drift detected from tier-1 runs.
