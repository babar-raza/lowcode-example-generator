# Real GitHub PR Publisher — Preflight Review

**Review date:** 2026-05-01
**Sprint:** Real GitHub PR Publisher Implementation Sprint

---

## Prior State Confirmed

| Check | Result |
|---|---|
| `approval_gate.py` exists | YES |
| `APPROVAL_EXPECTED_VALUE = "APPROVE_LIVE_PR"` | CONFIRMED |
| `probe-publish-permissions` is read-only | CONFIRMED (`probe_is_read_only=true`) |
| Cells `can_push=True` | CONFIRMED |
| Words `can_push=True` | CONFIRMED |
| No content pushed | CONFIRMED |
| No live PR created | CONFIRMED |
| Publisher has stub | CONFIRMED (`result.status = "published"` line 185) |
| `live_publish_ready=false` | CONFIRMED for cells and words |
| Simulations passed | CONFIRMED (both `SIMULATION_PASSED`) |
| Simulations are NOT real PRs | CONFIRMED (`live_pr_created=false`) |

---

## Stub Gap Confirmed

**File:** `src/plugin_examples/publisher/publisher.py`
**Line:** 185
**Code:** `result.status = "published"`

After ALL guards pass (approval token, branch name, repo_access_ready, pr_permission_ready, family_config, central repo check, GITHUB_TOKEN present), the code returns `status="published"` with **zero GitHub API calls**. No branch, no commit, no PR.

**Risk:** HIGH — Silent false success.

---

## Readiness for Implementation

- Approval gate: in place and tested
- Push permissions: CONFIRMED for both families
- Packages assembled: cells (9 ex) and words (4 ex)
- Target repos accessible: aspose-cells-net and aspose-words-net
- GITHUB_TOKEN: present

**Safe to implement real publisher.**

---

## Implementation Plan

1. **New:** `src/plugin_examples/publisher/github_pr_publisher.py`
   - GitHub REST API via urllib (GET → POST blobs → POST tree → POST commit → POST ref → POST PR)
   - Token via `Authorization: Bearer {token}` header only — never logged/serialized
2. **Replace stub** in `publisher.py` — add `package_path` param; call real publisher or `blocked_real_publisher_not_implemented`
3. **Update** `pr_builder.py` — richer PR body with all required sections
4. **Update** `__main__.py` — `publish-pr --publish` flag for live mode
5. **New tests:** `tests/unit/test_real_github_publisher.py` — 11 mock-based tests
