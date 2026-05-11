# Repo Access Self-Service Resolution Review

**Review date:** 2026-05-01
**Sprint:** Repo Access Self-Service Resolution Review
**Purpose:** Exhaust all safe autonomous access checks before escalating to human

---

## Prior Work Confirmed

All 16 prior claims verified:
- cells.yml and words.yml target family-specific repos ✓
- Token present and authenticated as babar-raza ✓
- Both repos returned HTTP 404 in all prior checks ✓
- repo_access_ready=false, pr_permission_ready=false, live_publish_ready=false ✓
- No live push occurred ✓
- dry_run=True enforced in publisher ✓

---

## What Was Attempted This Sprint

| Method | Result |
|---|---|
| REST API GET /repos/{owner}/{repo} | HTTP 404 both repos |
| gh repo view (GraphQL) | "Could not resolve to Repository" |
| git ls-remote --heads with Authorization header | "invalid credentials" |
| Variant repo name probes (4 variants) | All 404 |
| org endpoint /orgs/{org} | HTTP 200 — both orgs exist |
| org repos listing /orgs/{org}/repos | 0 repos visible |
| org membership /user/memberships/orgs/{org} | HTTP 403 |
| SSO header check | Not present |
| Rate limit check | 4978+ remaining — authenticated |
| GET /user | HTTP 200 — babar-raza |
| Own repo test | HTTP 200 — token is valid |

---

## Token Type Analysis

`gh auth status` shows GITHUB_TOKEN prefix: `github_pat_`

| Token Type | Prefix |
|---|---|
| Fine-grained PAT | `github_pat_` |
| Classic PAT (new format) | `ghp_` |
| OAuth App token | `gho_` |
| Legacy classic PAT | 40-char hex |

**Observed prefix `github_pat_` = fine-grained PAT.** User states "classic PAT." Discrepancy should be verified in GitHub Settings.

There is also a keyring token (`gho_` prefix, scopes: `repo`, `read:org`, `gist`) that is NOT active and was NOT used per security rules.

---

## Root Cause

The GITHUB_TOKEN (whether fine-grained or classic) is not authorized to read the target org repos:
- `aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples`
- `aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples`

Fine-grained PATs require explicit per-repo grants. Classic PATs require babar-raza to be a collaborator or org member.

**No SSO/SAML restriction detected** (no `x-github-sso` header).

---

## Required Human Action (Exactly One of These)

### Option A — If token is fine-grained PAT (`github_pat_` prefix)

1. Go to: GitHub > Settings > Developer settings > Personal access tokens > Fine-grained tokens
2. Click the active token
3. Under **Repository access**: add both repos:
   - `aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples`
   - `aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples`
4. Required permissions: `Contents` (Read), `Pull requests` (Write), `Metadata` (Read)
5. Save token

### Option B — If token is classic PAT (`ghp_` prefix)

1. Add babar-raza as a collaborator (write access) to both repos:
   - In `aspose-cells-net` org: repo Settings > Collaborators > add babar-raza
   - In `aspose-words-net` org: same
2. OR add babar-raza as an org member with appropriate access

### After Either Fix

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples resolve-repo-access --families cells words --promote-latest
```

Expected: `repo_access_ready=true` for both families.

---

## Evidence Files

- `workspace/verification/latest/repo-access-self-service-preflight.json`
- `workspace/verification/latest/gh-cli-access-check.json`
- `workspace/verification/latest/family-repo-access-resolution.json`
