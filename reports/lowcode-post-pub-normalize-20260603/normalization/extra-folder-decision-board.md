# Extra Folder Decision Board

## Diagram Repo: 4 folders, 2 intended, 2 extra

| Folder | API Class | Classification | Action |
|--------|-----------|---------------|--------|
| diagram-converter | DiagramConverter | INTENDED | Keep |
| pdf-converter | PdfConverter | INTENDED | Keep |
| diagram-diagram-converter | DiagramConverter | LEGACY_DUPLICATE_TO_REMOVE | Remove via PR |
| diagram-pdf-converter | PdfConverter | LEGACY_DUPLICATE_TO_REMOVE | Remove via PR |

**Rationale:** `diagram-diagram-converter` and `diagram-pdf-converter` are early pilot-style
examples that duplicate the canonical `diagram-converter` and `pdf-converter`. They use
class-based/namespace patterns and temp directories, while the intended versions use
top-level statements with committed inputs. They were created by a prior PR and not part
of the modeled 44-example publication set.

## PDF Repo: 21 folders, 20 intended, 1 extra

| Folder | API Class | Classification | Action |
|--------|-----------|---------------|--------|
| pdfa-converter | PdfAConverter | INTENDED | Keep |
| pdf-aconverter | PdfAConverter | LEGACY_DUPLICATE_TO_REMOVE | Remove via PR |

**Rationale:** `pdf-aconverter` is an earlier pilot version of the PDF/A converter example.
The canonical version is `pdfa-converter` (with csproj `pdf-pdf-aconverter.csproj`). Both
use the same `PdfAConverter` LowCode API class. The pilot version should be removed.
