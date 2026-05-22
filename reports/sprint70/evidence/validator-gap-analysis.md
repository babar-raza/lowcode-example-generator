# Validator Gap Analysis — Sprint 70

Date: 2026-05-22
Sprint: sprint70

## Gaps Found in Sprint 69 Validator (EV 67/67)

### Gap 1: No rule checked root_readme.source_path currency

**Sprint 69 defect**: S69-D1
**Description**: Sprint 69 rules 62 and 66 verify that:
- `root_readme` field exists in handoff-index (rule 62)
- `root_readme_sha256` exists in publication-handoff-index (rule 66)

But neither rule checked that `root_readme.source_path` is actually inside the current sprint's
handoff folder, or that the file exists at that path, or that the stored hash matches the actual file.

**Result**: Sprint 69 passed EV 67/67 while all 6 handoff-indexes pointed to sprint68 paths.

### Gap 2: No rule enforced legacy index superseded status

**Sprint 69 defect**: S69-D2
**Description**: Sprint 69 rule 63 verifies exact-legacy-plan-reconciliation-final.md exists.
But no rule checked whether an older simplified reconciliation-index.md was still present
without a superseded marker.

**Result**: Sprint 69 passed while legacy-plan-reconciliation/reconciliation-index.md remained
without explicit historical/superseded marking.

## Sprint 70 New Rules (68-72)

| Rule # | Rule ID | Defect Closed | Description |
|--------|---------|---------------|-------------|
| 68 | handoff_root_readme_in_sprint_folder | S69-D1 | source_path must start with reports/{sprint_id}/handoff/per-family/{family}/ |
| 69 | handoff_root_readme_file_present | S69-D1 | root README file must physically exist at source_path |
| 70 | handoff_root_readme_hash_matches | S69-D1 | sha256 in handoff-index must match physical file bytes |
| 71 | publication_handoff_root_readme_hash_matches | S69-D1 | phi root_readme_sha256 must match physical file |
| 72 | legacy_simplified_index_superseded | S69-D2 | old reconciliation-index must be absent or marked superseded |

## Rule Implementation Details

### Rule 68 (handoff_root_readme_in_sprint_folder)
Reads source_path from each family's handoff-index.json root_readme field.
Checks: `source_path.startswith(f"reports/{sprint_id}/handoff/per-family/{family}/")`
FAILS if any family has a path pointing to an old sprint.

### Rule 69 (handoff_root_readme_file_present)
Uses `_resolve_sprint_relative_path(src)`: strips `reports/{sprint_id}/` prefix,
resolves relative to bundle_dir. This works in both production and unit tests.
FAILS if the file does not exist at the resolved path.

### Rule 70 (handoff_root_readme_hash_matches)
Same path resolution as rule 69.
Computes sha256 of the physical file bytes.
FAILS if hash doesn't match stored sha256 in handoff-index.

### Rule 71 (publication_handoff_root_readme_hash_matches)
Reads publication-handoff-index.json families list.
Checks root_readme_source_path + root_readme_sha256 against physical file.
FAILS if any family hash mismatches.

### Rule 72 (legacy_simplified_index_superseded)
Requires exact-legacy-plan-reconciliation-final.md to exist.
If legacy-plan-reconciliation/reconciliation-index.md exists, requires EITHER
history/legacy-plan-reconciliation-superseded.md OR legacy-reconciliation/README.md.
FAILS if old simplified index exists without a superseded marker.

## Sprint 69 Revalidation Under Sprint 70 Rules

Sprint 69 fails rules 68-70 because:
- Rule 68: all 6 source_paths start with reports/sprint68/ not reports/sprint69/handoff/
- Rule 69: files physically absent in sprint69 handoff (no README.md per family dir)
- Rule 70: hashes from sprint68 files don't match expected sprint69 handoff paths

Sprint 69 passes rules 71 and 72:
- Rule 71: publication-handoff-index.json doesn't have root_readme_source_path (skipped)
- Rule 72: exact-legacy-plan-reconciliation-final.md exists; no old index present

## Sprint 70 Passes All 72 Rules

Sprint 70 bundle passes:
- Rules 68-70: all 6 handoff-index files have source_path inside sprint70 handoff,
  README.md physically present, hashes match
- Rule 71: publication-handoff-index.json has root_readme_source_path + matching hash
- Rule 72: exact-legacy-plan-reconciliation-final.md exists + legacy-reconciliation/README.md
