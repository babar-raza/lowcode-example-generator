# Format Authority

Repo-local, versioned format contracts for all 42 active LowCode types across 6 families.

## Structure

```
pipeline/format-authority/
  manifest.json              # Root manifest: family index, total counts
  contracts/
    cells.json               # 9 types
    words.json               # 8 types
    pdf.json                 # 19 types
    diagram.json             # 2 types
    email.json               # 1 type
    slides.json              # 3 types
```

## Authority Chain

1. **DllReflector API catalogs** (highest trust) — reflected method signatures, options classes, enums
2. **NuGet XML documentation** — where present in catalogs
3. **Options class properties / SaveFormat enums** — determines valid output formats
4. **This directory** — normalized, conflict-resolved, repo-local authority
5. **Pipeline consumers** (planner, codegen, manifests, gates, README) — must read from here

## Usage

```python
from plugin_examples.format_authority.store import get_contract
fc = get_contract("cells", "SpreadsheetConverter")
print(fc.canonical_output_format)  # ".csv"
```

## Conflict Resolutions

See `conflict_status` and `conflict_notes` fields in each contract entry for resolved conflicts.

## Do Not

- Edit these files manually without API evidence
- Add types without DllReflector reflection
- Use these as display-only reports — they are the production authority
