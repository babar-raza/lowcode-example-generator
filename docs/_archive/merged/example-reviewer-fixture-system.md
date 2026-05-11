# Example-Reviewer Fixture System Discovery

## Source Repository

Path: `C:\Users\prora\OneDrive\Documents\GitHub\example-reviewer`

## Fixture Modules Found

### 1. TestDataGenerator (`src/services/test_data_generator.py`)

The core fixture-creation engine. 1500+ lines, 30+ format-specific generators.

**Entry point:** `generate_file_for_family(filename, dest, test_data_dir, family) -> (bool, str)`

**Architecture:**
- Extension-based dispatch table (`_FAMILY_GENERATORS`)
- Priority: extension-specific generator > copy same-extension from test-data > placeholder text
- Deterministic: fixed 1980-01-01 timestamps, store compression, sorted file lists
- No external dependencies for file creation (stdlib only)

**Supported formats (create from scratch):**

| Format | Function | Method |
|--------|----------|--------|
| .xlsx | `_generate_xlsx()` | OOXML via stdlib zipfile |
| .html | `_generate_html()` | HTML table template |
| .csv | `_generate_csv()` | 3-row CSV with headers |
| .txt | `_generate_text()` | Canterbury Corpus snippet |
| .xml | `_generate_xml()` | Minimal valid XML |
| .rtf | `_generate_rtf()` | RTF1 control sequences |
| .png | `_generate_png()` | 1x1 pixel minimal PNG bytes |
| .jpg | `_generate_jpeg()` | Minimal JPEG SOI/EOI |
| .bmp | `_generate_bmp()` | Minimal BM header + DIB |
| .gif | `_generate_gif()` | GIF89a 1x1 transparent |
| .tiff | `_generate_tiff()` | Valid TIFF II byte order |
| .svg | `_generate_svg()` | Minimal SVG root element |
| .pptx | `_generate_pptx()` | OOXML via zipfile |
| .eml | `_generate_eml()` | RFC 2822 headers |
| .epub | `_generate_epub()` | EPUB via zipfile |

**Not generated (copy-only):** .docx, .doc, .pdf, .odt, .psd, .dwg

**No explicit .json generator** -- falls through to text-like placeholder.

### 2. FixtureResolverService (`src/services/fixture_resolver_service.py`)

5-tier resolution chain for missing files at runtime:
1. Existing file in test-data
2. Registry lookup (previously resolved)
3. Example repo recursive search
4. Same-extension match (difflib similarity)
5. Generate via TestDataGenerator

**Not needed for lowcode-example-generator** -- our pipeline generates fixtures before runtime, not during.

## Reuse Assessment

### `_generate_xlsx()` -- COPY
Pure stdlib (zipfile). Creates valid OOXML workbook. No dependencies.
Can be copied verbatim into fixture_factory.py.

### `_generate_html()`, `_generate_csv()`, `_generate_text()` -- COPY
All text-based, stdlib only. 5-10 lines each.

### `_generate_json()` -- NOT AVAILABLE
No explicit JSON generator exists. We must write our own (trivial).

### FixtureResolverService -- NOT NEEDED
Runtime resolution pattern does not match our pre-generation fixture placement.

## Recommendation

**Reuse mode: copy**

Copy the 5 format-specific generator functions from `test_data_generator.py` into a new `fixture_factory.py` in the lowcode-example-generator repo. Add a JSON generator (not present in reviewer). No need to import or subprocess -- the functions are pure stdlib.

## Dependencies Required

None beyond Python stdlib. The generators use:
- `pathlib.Path`
- `zipfile` (for .xlsx)
- String templates (for .html, .csv, .txt, .json)

## Gaps

1. No JSON generator in example-reviewer -- must write one
2. XLSX generator creates minimal valid file but Aspose.Cells SDK may need specific features -- current OOXML structure is sufficient for Aspose to open
3. No PDF generator from scratch (binary format) -- not needed for Cells pilot
