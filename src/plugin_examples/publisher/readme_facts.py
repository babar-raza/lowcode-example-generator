"""Source-truth README publication facts for LowCode example repositories.

Extracts verified input/output format claims and source snippets from actual
generated example source files (Program.cs). README rows render from these
verified facts, not from config defaults or name-keyword heuristics.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Regex patterns to extract file extensions from Program.cs path assignments
# Primary: "input.vsdx", 'input.pdf', Path.Combine(workDir, "input.vsdx"), etc.
_INPUT_PATTERN = re.compile(r'["\']input\.(\w+)["\']')
_OUTPUT_PATTERN = re.compile(r'["\']output\.(\w+)["\']')

# Extended input patterns: input1.ext, input2.ext, template.ext, source.ext
_INPUT_EXTENDED_PATTERNS = [
    re.compile(r'["\']input\d*\.(\w+)["\']'),
    re.compile(r'["\']template\.(\w+)["\']'),
    re.compile(r'["\']source\.(\w+)["\']'),
]

# Extended output patterns: result.ext, report.ext, output_signed.ext
_OUTPUT_EXTENDED_PATTERNS = [
    re.compile(r'["\']result\.(\w+)["\']'),
    re.compile(r'["\']report\.(\w+)["\']'),
    re.compile(r'["\']output[_-]\w+\.(\w+)["\']'),
]


@dataclass
class ExampleFact:
    """Verified publication fact for a single example."""
    example_name: str
    api_symbol: str
    source_file_path: str
    source_file_sha256: str
    snippet_mode: str  # "full_file" | "excerpt" | "none"
    snippet_content: str
    snippet_content_sha256: str
    input_extension: str
    output_extension: str
    input_extension_source: str  # e.g. "program_cs:line14:input.vsdx"
    output_extension_source: str
    proof_source: str  # "program_cs" | "config" | "blocked_unverified"
    validation_status: str  # "verified" | "blocked_unverified"
    api_method_extracted: str = ""  # e.g. "DiagramConverter.Process"
    api_method_source: str = ""  # e.g. "program_cs:line48"
    api_method_validation: str = ""  # "verified" | "blocked_unverified"


@dataclass
class ExampleReadmeFacts:
    """Complete set of verified facts for a family's README."""
    family: str
    generated_at: str
    source_artifact: str
    facts: list[ExampleFact] = field(default_factory=list)


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_extension(pattern: re.Pattern, source: str) -> tuple[str, str]:
    """Extract file extension and source location from Program.cs content.

    Returns (extension, source_location) or ("", "") if not found.
    """
    for i, line in enumerate(source.splitlines(), 1):
        m = pattern.search(line)
        if m:
            ext = m.group(1)
            raw = m.group(0).strip('"').strip("'")
            return ext, f"program_cs:line{i}:{raw}"
    return "", ""


# Patterns for API method extraction from Program.cs
# Pattern 1: Static call — ClassName.MethodName(
_STATIC_API_CALL = re.compile(
    r'(?:await\s+)?'                      # optional await
    r'(?:Aspose\.\w+\.LowCode\.)?'        # optional full namespace
    r'([A-Z][A-Za-z]+)\.([A-Z][A-Za-z]+)\(',  # ClassName.MethodName(
)
# Pattern 2: Instance call — new ClassName().Process(
_INSTANCE_API_CALL = re.compile(
    r'new\s+([A-Z][A-Za-z]+)\(\)\s*\.\s*([A-Z][A-Za-z]+)\(',
)
# Pattern 3: Variable call — variable.Process( where variable = new ClassName()
_VAR_DECL = re.compile(
    r'(?:var|[A-Z]\w+)\s+(\w+)\s*=\s*new\s+([A-Z][A-Za-z]+)\(\)',
)
_VAR_CALL = re.compile(
    r'(\w+)\.\s*([A-Z][A-Za-z]+)\(',
)

# Methods to ignore — these are not LowCode API operations
_IGNORE_METHODS = {
    "Dispose", "Save", "Add", "Exists", "Delete", "Combine", "GetTempPath",
    "GetCurrentDirectory", "CreateDirectory", "WriteAllText", "ReadAllBytes",
    "GetFileName", "WriteLine", "Write", "InsertField", "Writeln",
    "AddAutoShape", "AddTextFrame", "GetBytes", "AddInput", "AddOutput",
    "Create", "AddYears", "Rectangle", "Export",
}

# Classes to ignore — framework/fixture classes, not LowCode
_IGNORE_CLASSES = {
    "File", "Path", "Directory", "Console", "Document", "DocumentBuilder",
    "Presentation", "FileInfo", "Environment", "Encoding", "MemoryStream",
    "CertificateRequest", "RSA", "TextFragment", "Now",
    "Aspose", "Int32", "Pdf", "Slides", "Words", "Cells",
    "SaveFormat", "ShapeType", "GC",
}

# Classes that are Options, not operations — ignore when they appear as ClassName.Method
_IGNORE_OPTION_CLASSES = {
    "HtmlToPdfOptions", "PdfToDocOptions", "PdfToXlsOptions", "JpegOptions",
    "PngOptions", "TiffOptions", "MergeOptions", "SplitOptions", "OptimizeOptions",
    "TextExtractorOptions", "ImageExtractorOptions", "TableOptions", "TocOptions",
    "FormFlattenAllFieldsOptions", "FormRemoveAllFieldsOptions",
    "FormExporterToJsonOptions", "FormImporterJsonOptions",
    "EncryptionOptions", "SignOptions", "PdfAConvertOptions",
    "Options",
}


def _extract_api_method(source: str) -> tuple[str, str]:
    """Extract the primary LowCode API method call from Program.cs.

    Returns (api_symbol, source_location) e.g. ("DiagramConverter.Process", "program_cs:line48").
    Returns ("", "") if no recognizable API call is found.
    """
    # First pass: build variable→class mapping for indirect calls
    var_class_map: dict[str, str] = {}
    for line in source.splitlines():
        m = _VAR_DECL.search(line)
        if m:
            var_name, class_name = m.group(1), m.group(2)
            if class_name not in _IGNORE_CLASSES:
                var_class_map[var_name] = class_name

    # Second pass: find actual API calls (prefer non-Dispose, non-framework calls)
    candidates: list[tuple[str, str, int]] = []  # (class, method, line_num)

    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        # Skip comments
        if stripped.startswith("//") or stripped.startswith("*"):
            continue

        # Check Pattern 2: new ClassName().Method(
        m = _INSTANCE_API_CALL.search(stripped)
        if m:
            cls, method = m.group(1), m.group(2)
            if (cls not in _IGNORE_CLASSES and cls not in _IGNORE_OPTION_CLASSES
                    and method not in _IGNORE_METHODS):
                candidates.append((cls, method, i))
                continue

        # Check Pattern 3: variable.Method( — check BEFORE static to catch plugin.Process
        m = _VAR_CALL.search(stripped)
        if m:
            var_name, method = m.group(1), m.group(2)
            if var_name in var_class_map and method not in _IGNORE_METHODS:
                candidates.append((var_class_map[var_name], method, i))
                continue

        # Check Pattern 1: ClassName.Method( or await ClassName.Method(
        m = _STATIC_API_CALL.search(stripped)
        if m:
            cls, method = m.group(1), m.group(2)
            if (cls not in _IGNORE_CLASSES and cls not in _IGNORE_OPTION_CLASSES
                    and method not in _IGNORE_METHODS):
                candidates.append((cls, method, i))
                continue

    if not candidates:
        return "", ""

    # Return the first non-Dispose candidate (there should be exactly one main API call)
    for cls, method, line_num in candidates:
        return f"{cls}.{method}", f"program_cs:line{line_num}"

    return "", ""


def extract_example_readme_facts(
    family: str,
    package_path: Path,
    examples: list[dict],
    manifest_reader=None,
) -> ExampleReadmeFacts:
    """Extract verified README facts from actual example source files.

    Args:
        family: Family name (e.g. "diagram").
        package_path: Path to the PR dry-run package directory.
        examples: List of example metadata dicts with at least ``name``.
        manifest_reader: Optional callable to read API symbol from manifest.

    Returns:
        ExampleReadmeFacts with one ExampleFact per example.

    Each fact is either ``verified`` (input/output extracted from Program.cs)
    or ``blocked_unverified`` (source could not determine extensions).
    """
    facts = ExampleReadmeFacts(
        family=family,
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_artifact=str(package_path),
    )

    for ex in examples:
        name = ex.get("name", "") or ex.get("scenario_id", "")
        if not name:
            continue

        program_cs = package_path / "examples" / family / "lowcode" / name / "Program.cs"

        if not program_cs.exists():
            facts.facts.append(ExampleFact(
                example_name=name,
                api_symbol="",
                source_file_path=str(program_cs.relative_to(package_path)),
                source_file_sha256="",
                snippet_mode="none",
                snippet_content="",
                snippet_content_sha256="",
                input_extension="",
                output_extension="",
                input_extension_source="",
                output_extension_source="",
                proof_source="blocked_unverified",
                validation_status="blocked_unverified",
            ))
            continue

        source = program_cs.read_text(encoding="utf-8")
        file_hash = _sha256_file(program_cs)

        # Extract extensions from source — try primary patterns first, then extended
        input_ext, input_src = _extract_extension(_INPUT_PATTERN, source)
        if not input_ext:
            for pat in _INPUT_EXTENDED_PATTERNS:
                input_ext, input_src = _extract_extension(pat, source)
                if input_ext:
                    break

        output_ext, output_src = _extract_extension(_OUTPUT_PATTERN, source)
        if not output_ext:
            for pat in _OUTPUT_EXTENDED_PATTERNS:
                output_ext, output_src = _extract_extension(pat, source)
                if output_ext:
                    break

        # Determine snippet mode
        line_count = len(source.splitlines())
        if line_count <= 120:
            snippet_mode = "full_file"
            snippet_content = source
        else:
            snippet_mode = "excerpt"
            lines = source.splitlines()
            snippet_content = "\n".join(lines[:80]) + "\n// ... see full source in Program.cs\n"

        # API symbol from manifest if available
        api_symbol = ""
        if manifest_reader:
            manifest_path = (
                package_path / "examples" / family / "lowcode" / name / "example.manifest.json"
            )
            api_symbol = manifest_reader(manifest_path) or ""

        # Extract API method from source code — takes priority over manifest
        api_method, api_method_src = _extract_api_method(source)
        api_method_valid = "verified" if api_method else "blocked_unverified"
        # Source-extracted API method always overrides manifest (manifest may list .Dispose)
        if api_method:
            api_symbol = api_method
        # Fall back to manifest only if source extraction failed
        elif not api_symbol and manifest_reader:
            pass  # api_symbol already set from manifest above

        # Validation status
        if input_ext and output_ext:
            validation_status = "verified"
            proof_source = "program_cs"
        else:
            validation_status = "blocked_unverified"
            proof_source = "blocked_unverified"
            logger.warning(
                "Example '%s': could not extract %s from Program.cs",
                name,
                "input extension" if not input_ext else "output extension",
            )

        facts.facts.append(ExampleFact(
            example_name=name,
            api_symbol=api_symbol,
            source_file_path=str(program_cs.relative_to(package_path)),
            source_file_sha256=file_hash,
            snippet_mode=snippet_mode,
            snippet_content=snippet_content,
            snippet_content_sha256=_sha256(snippet_content),
            input_extension=input_ext,
            output_extension=output_ext,
            input_extension_source=input_src,
            output_extension_source=output_src,
            proof_source=proof_source,
            validation_status=validation_status,
            api_method_extracted=api_method,
            api_method_source=api_method_src,
            api_method_validation=api_method_valid,
        ))

    return facts


def facts_to_json(facts: ExampleReadmeFacts) -> str:
    """Serialize facts to JSON string (without snippet content for evidence)."""
    d = asdict(facts)
    # Strip snippet content from evidence JSON to keep it small
    for f in d.get("facts", []):
        f.pop("snippet_content", None)
    return json.dumps(d, indent=2)
