# Timestamp Network Policy — lowcode-systemization-pass3-20260530

## Status: NETWORK_DEPENDENCY_BLOCKER (BLK-003)

TimestampEmbedder requires a live TSA (Timestamp Authority) RFC 3161 endpoint.
This is a fundamental requirement of RFC 3161 timestamp embedding.

No offline simulation is possible without compromising the timestamp's validity.

Policy: timestamp example is EXCLUDED from publication candidates.
