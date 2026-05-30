# Timestamp Offline Fallback — lowcode-systemization-pass3-20260530

No viable offline fallback exists for RFC 3161 timestamp embedding.
The TSA server must be reachable at runtime for the timestamp to be valid.

Fallback options considered:
- Mock TSA server: Would produce invalid timestamps — not acceptable for documentation
- Pre-computed timestamp: Would be stale — not useful for users

Decision: EXCLUDED from publication candidates.
