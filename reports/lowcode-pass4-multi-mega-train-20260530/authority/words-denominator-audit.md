# Words Denominator Hash Audit

Sprint: lowcode-pass4-multi-mega-train-20260530
Date: 2026-05-30

## Claim Under Review

Prior sprint (multi-mega-train) set `api_catalog_sha256 = 8dfbb85d5923054106a15d7e332ebaaba6b038be5bfb1cc66ceffcbf4774e672`
in `pipeline/configs/denominators/words.json`.

Reviewer objection: hash mismatch (observed `db3ec3dda...` in some runs).

## Investigation

### How the hash is computed

`compute_catalog_hash()` in the pipeline:
```python
json.dumps(catalog, sort_keys=True, ensure_ascii=False)
```
Then SHA256 of the resulting UTF-8 string.

The catalog is built from the Aspose.Words NuGet package API surface for the target version.

### Hash sources by package version

| Version        | api_catalog_sha256 (first 16 chars) | Source run |
|----------------|--------------------------------------|------------|
| Aspose.Words 25.5.0 | `db3ec3dda...`               | pilot-words-heal-20260528, pilot-words-heal2-20260528 |
| Aspose.Words 26.5.0 | `8dfbb85d...`               | pilot-words-20260528-143053, pilot-words-20260529-215632, pilot-words-repair-20260530 |

### Verification evidence

Three independent 26.5.0 catalog files all produce `8dfbb85d...`:
- `workspace/runs/pilot-words-20260528-143053/` — hash: `8dfbb85d...`
- `workspace/runs/pilot-words-20260529-215632/` — hash: `8dfbb85d...`
- `workspace/runs/pilot-words-repair-20260530/` — hash: `8dfbb85d...`

The heal runs (`pilot-words-heal-20260528`) used Words 25.5.0. Those are NOT the current canonical version.

## Verdict

`8dfbb85d5923054106a15d7e332ebaaba6b038be5bfb1cc66ceffcbf4774e672` is **CORRECT** for Aspose.Words 26.5.0.

`db3ec3dda...` came exclusively from Words 25.5.0 heal runs — not the canonical version.

The denominator file `pipeline/configs/denominators/words.json` is **CORRECTLY SET**.

No change required.
