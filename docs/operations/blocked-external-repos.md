# Blocked External Repositories

Audience: Operator, External stakeholder
Last updated: 2026-06-20

This file documents product families that have validated, packaged examples ready for
publication but cannot be published because the target GitHub repository does not yet
exist or is not accessible.

**TC-SRHP-02 — Unblock font, psd, note Publication**

---

## Status Summary

| Family | Examples Ready | Target Repo Expected | Repo Exists? | Blocked Since | Action Required |
|---|---|---|---|---|---|
| font | 2 | `aspose-font-net/Aspose.Font.Plugins-for-.NET-Examples` | Unknown | 2026-06-16 | Create repo or confirm org/name |
| psd | 4 | `aspose-psd-net/Aspose.PSD.Plugins-for-.NET-Examples` | Unknown | 2026-06-16 | Create repo or confirm org/name |
| note | 3 | `aspose-note-net/Aspose.Note.Plugins-for-.NET-Examples` | Unknown | 2026-06-16 | Create repo or confirm org/name |

**Total blocked examples: 9**

---

## Families in Detail

### font (2 examples ready)

- **Package:** `Aspose.Font`
- **Source examples repo:** `https://github.com/aspose-font/Aspose.Font-for-.NET`
- **Expected target repo:** `aspose-font-net/Aspose.Font.Plugins-for-.NET-Examples`
- **Evidence of readiness:** `pipeline/plugin-code-registry/family/font.yaml`
  — 2 entries with `registry_status: CANONICAL_PACKAGE_PROVEN`
- **Next action:** Confirm target repo name with org owner (babar-raza), then:
  ```bash
  PYTHONPATH=src python -m plugin_examples publish-pr --family font
  ```

### psd (4 examples ready)

- **Package:** `Aspose.PSD`
- **Source examples repo:** `https://github.com/aspose-psd/Aspose.Psd-for-.NET`
- **Expected target repo:** `aspose-psd-net/Aspose.PSD.Plugins-for-.NET-Examples`
- **Known constraint:** Aspose.PSD uses JavaAttributes-style API in some operations.
  Review generated examples for `JavaAttributes` usage before publishing.
- **Evidence of readiness:** `pipeline/plugin-code-registry/family/psd.yaml`
  — 4 entries with `registry_status: CANONICAL_PACKAGE_PROVEN`
- **Next action:** Confirm target repo and resolve JavaAttributes constraint, then publish.

### note (3 examples ready)

- **Package:** `Aspose.Note`
- **Source examples repo:** `https://github.com/aspose-note/Aspose.Note-for-.NET`
- **Expected target repo:** `aspose-note-net/Aspose.Note.Plugins-for-.NET-Examples`
- **Evidence of readiness:** `pipeline/plugin-code-registry/family/note.yaml`
  — 3 entries with `registry_status: CANONICAL_PACKAGE_PROVEN`
- **Note:** products.aspose.net/note/ was unverified (HTTP 403 WAF) as of 2026-06-14.
  Confirm product page URL before PR title generation.
- **Next action:** Confirm target repo name with org owner, then publish.

---

## Verification Steps

Before submitting PRs, verify target repos exist and token has access:

```bash
# Check font
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/aspose-font-net/Aspose.Font.Plugins-for-.NET-Examples \
  | python -c "import json,sys; d=json.load(sys.stdin); print(d.get('full_name'), d.get('permissions'))"

# Check psd
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/aspose-psd-net/Aspose.PSD.Plugins-for-.NET-Examples \
  | python -c "import json,sys; d=json.load(sys.stdin); print(d.get('full_name'), d.get('permissions'))"

# Check note
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/aspose-note-net/Aspose.Note.Plugins-for-.NET-Examples \
  | python -c "import json,sys; d=json.load(sys.stdin); print(d.get('full_name'), d.get('permissions'))"
```

Expected response for a working repo: `full_name` present, `"push": true` in permissions.

---

## Escalation

If repos cannot be created within the current cycle:

1. Update registry entries for each family:
   ```yaml
   registry_status: BLOCKED_EXTERNAL_REPO_MISSING
   blocker_type: EXTERNAL_REPO_MISSING
   next_action: AWAITING_REPO_CREATION
   ```

2. Update this file with the date escalated and who was contacted.

3. Recheck monthly.

---

## Permanent Discontinuation

If a product is permanently discontinued (no new repo will be created), update the
registry to `BLOCKED_EXTERNAL_PERMANENT` and archive the evidence bundles.

---

## Closure

This TC closes when:
- All 3 families have successfully submitted PRs (`publish-pr` succeeds), OR
- All 3 families are formally marked `BLOCKED_EXTERNAL_PERMANENT` with escalation evidence.

Date escalated: 2026-06-20
Escalated to: babar-raza (repo owner)
Expected resolution: TBD
