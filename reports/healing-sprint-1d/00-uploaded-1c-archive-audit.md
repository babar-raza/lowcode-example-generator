# Healing Sprint 1D -- Uploaded 1C Archive Audit

**Sprint:** Healing Sprint 1D
**Date:** 2026-05-27
**Purpose:** Archive rebuild only. Fix the Sprint 1C uploaded ZIP which contained 4 defects.

---

## Uploaded Sprint 1C ZIP — Confirmed Defects

**File:** `reports/healing-sprint-1c/bundles/healing-sprint-1c-evidence-20260527.zip`
**Entry count:** 17

### Defect 1 — bundle-manifest.json file_count: 0

Inside the ZIP, `bundle-manifest.json` has `"file_count": 0`.
The ZIP actually contains 17 files.

**Root cause:** The ZIP was built (via `scripts/build_healing_sprint_1c_bundle.py`) BEFORE the
bundle-manifest was updated with the real file_count. The ZIP captured the pre-update manifest.

**On-disk state:** `reports/healing-sprint-1c/bundle-manifest.json` on disk correctly shows
`"file_count": 17` (committed in `abeea0e`). But the ZIP was not rebuilt after that update.

### Defect 2 — bundle-manifest.json head_sha is step-2, not final HEAD

Inside the ZIP, `bundle-manifest.json` has:
- `head_sha: 75f974bd6cfa94e37c53d2be659519b8e2df7aac` (step-2 finalize-proof commit)

Actual final HEAD at ZIP build time: `3715840` (step-3 update-proof-SHA commit).
Current repo HEAD: `abeea0ed19c231a4fed5b45a4cf55ada1ff18eab` (post-ZIP bundle commit).

**Root cause:** The ZIP was built between step-3 and the post-ZIP bundle commit. head_sha
records step-2 per convention, but the final repo HEAD is `abeea0e` which is not reflected
in the manifest or proof inside the ZIP.

### Defect 3 — final-clean-proof.txt is not final

Inside the ZIP, `final-clean-proof.txt` shows:
```
# Source SHA (step-1 evidence commit): e1084a6
# Head SHA (step-2 finalize-proof commit): captured below after step-2 commit
```
- `HEAD SHA` line still contains placeholder wording "captured below after step-2 commit"
- The git log top shows `e1084a6` (captured at step-1, not updated to reflect step-2 onward)
- The file does NOT show the final repo state with `3715840` or `abeea0e` in the log

**Root cause:** The proof was committed in step-2 (`75f974b`) with the step-2 SHA recorded,
but then step-3 updated the proof file. However the ZIP was built from the DISK state AFTER step-3
only partially updated the proof. The pre-commit placeholder "captured below after step-2 commit"
was in the file at ZIP-build time.

Actually: the final-clean-proof.txt inside the ZIP reads as the STEP-1 version (pre-step-2 capture).
The proof was not fully finalized when the ZIP was built.

### Defect 4 — commands.log contains SHA=TBD_STEP3

Inside the ZIP, `commands.log` contains:
```
git commit -m "feat(healing-sprint-1c): update final-clean-proof.txt with correct HEAD SHA"  [SHA=TBD_STEP3 -- captured below]
```

**Root cause:** The commands.log was updated with real SHAs only in step-3 commit (`3715840`).
The ZIP was built between step-3 and step-4 (post-ZIP commit), so the ZIP captured the stale
commands.log from before step-3 committed the real SHA.

Wait -- actually the commands.log update WAS included in the step-3 commit content. But the ZIP
was built from disk BEFORE the git add/commit for step-3. So the disk file may have had the real
SHA, but the ZIP was built from pre-step-3 disk state.

---

## Current Actual Repo State

| Field | Value |
|---|---|
| HEAD | abeea0ed19c231a4fed5b45a4cf55ada1ff18eab |
| Branch | main |
| Working tree | CLEAN |
| Last commit | abeea0e feat(healing-sprint-1c): update bundle-manifest file_count=17 and add build script post-ZIP |

### Sprint 1C Commits (All Verified)

| Step | SHA | Message |
|---|---|---|
| Step 1 (evidence) | e1084a6f9c30aecb5f1586c52c40c7face0320c0 | authority patch -- 6 files patched, ECC 17/17 |
| Step 2 (finalize-proof) | 75f974bd6cfa94e37c53d2be659519b8e2df7aac | finalize final-clean-proof.txt |
| Step 3 (update-SHA) | 3715840 | update final-clean-proof.txt with correct HEAD SHA |
| Step 4 (post-ZIP) | abeea0ed19c231a4fed5b45a4cf55ada1ff18eab | update bundle-manifest file_count=17 + build script |

All 4 SHAs verified via `git cat-file -t` = commit.

---

## Sprint 1D Decision

**1D SUPERSEDES the uploaded 1C ZIP.**

Sprint 1D creates a new archive that:
1. Shows the actual final repo HEAD (`abeea0e`) in all proof files.
2. Has correct `file_count` matching actual ZIP entries.
3. Has no placeholder SHAs or TBD entries.
4. Has a truthful commands.log with real SHAs.
5. Documents the finalization sequence explicitly.

Sprint 1C verdict (`LOWCODE_MACHINERY_HEALING_ACCEPTED`) and all machinery results are carried
forward unchanged. Sprint 1D is an archive rebuild only — no product work or re-validation.
