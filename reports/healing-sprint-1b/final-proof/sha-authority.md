# Healing Sprint 1B — SHA Authority

**Lane:** 1 — Final Git / SHA / Proof Repair
**Date:** 2026-05-27

## Healing Sprint 1 SHA Chain (Verified)

| Role | SHA | Exists in git |
|---|---|---|
| evidence_commit | 47ff25fa9eac333b3cb60f28c6886beabcbdd151 | YES (`git cat-file -t` = commit) |
| proof_commit | f62f1965d2a3bdc7e15e35b353efd32ddea4d1ef | YES |
| update_proof_commit | 580e8ebf (full: see git log) | YES |

**Sprint 1 Defect:** bundle-manifest.json `head_sha` pointed to `f62f196` (proof commit)
but the actual final 3-commit HEAD was `580e8eb` (update-proof commit). Sprint 1B
corrects this by using Sprint 1 as a superseded partial and creating a new authoritative
bundle.

## README.md Commit

| SHA | a20d875 | Exists | YES |
|---|---|---|---|
| Content | 101-line operator documentation additions | Safe | YES |

## Healing Sprint 1B SHA Chain

| Role | SHA | Status |
|---|---|---|
| readme_sha | a20d875 | COMMITTED |
| source_sha (evidence) | [captured after evidence commit] | PENDING |
| head_sha (proof) | [captured after proof commit] | PENDING |

All SHAs will be real committed SHAs before this file is finalized.

## Prohibited SHA Values

None of the following may appear in final authority files:
- `[to be set after ...]`
- `[to be captured ...]`
- Placeholder strings
- SHAs not verifiable via `git cat-file -t`

## Lane 1 Verdict

**SHA_AUTHORITY_IN_PROGRESS** — README.md committed. Sprint 1B chain pending evidence commit.
