"""Generate C# example code using LLM."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from plugin_examples.generator.packet_builder import PromptPacket

logger = logging.getLogger(__name__)


class GenerationError(Exception):
    """Raised when code generation fails."""


@dataclass
class GeneratedExample:
    """A generated C# example."""
    scenario_id: str
    code: str
    claimed_symbols: list[str] = field(default_factory=list)
    repair_attempts: int = 0
    status: str = "generated"  # generated, repaired, failed
    failure_reason: str | None = None


def generate_example(
    packet: PromptPacket,
    *,
    llm_generate: callable | None = None,
    max_repairs: int = 1,
) -> GeneratedExample:
    """Generate a C# example from a prompt packet.

    Args:
        packet: Constrained prompt packet.
        llm_generate: Callable that takes (prompt, system_prompt) and returns text.
            If None, generates a template example.
        max_repairs: Maximum LLM repair attempts.

    Returns:
        GeneratedExample with generated code.
    """
    if llm_generate is None:
        # Generate template without LLM
        code = _generate_template(packet)
        return GeneratedExample(
            scenario_id=packet.scenario_id,
            code=code,
            claimed_symbols=packet.approved_symbols,
            status="generated",
        )

    try:
        response = llm_generate(packet.user_prompt, packet.system_prompt)
        code = _extract_code(response)
    except Exception as e:
        return GeneratedExample(
            scenario_id=packet.scenario_id,
            code="",
            status="failed",
            failure_reason=f"LLM generation failed: {e}",
        )

    # Validate generated code
    issues = _validate_code(code)
    if issues and max_repairs > 0:
        logger.info("Attempting repair for %s: %s", packet.scenario_id, issues)
        try:
            repair_prompt = f"Fix these issues in the code:\n{issues}\n\nCode:\n{code}"
            response = llm_generate(repair_prompt, packet.system_prompt)
            code = _extract_code(response)
            return GeneratedExample(
                scenario_id=packet.scenario_id,
                code=code,
                claimed_symbols=packet.approved_symbols,
                repair_attempts=1,
                status="repaired",
            )
        except Exception as e:
            return GeneratedExample(
                scenario_id=packet.scenario_id,
                code=code,
                status="failed",
                failure_reason=f"Repair failed: {e}",
            )

    return GeneratedExample(
        scenario_id=packet.scenario_id,
        code=code,
        claimed_symbols=packet.approved_symbols,
        status="generated",
    )


def _generate_template(packet: PromptPacket) -> str:
    """Generate a catalog-aware template example without LLM."""
    td = packet.type_details
    type_name = td.get("name", packet.target_type.split(".")[-1]) if td else packet.target_type.split(".")[-1]
    methods_catalog = td.get("methods", []) if td else []
    kind = td.get("kind", "class") if td else "class"

    needs_input = _needs_input_file_creation(td) if td else False
    hints = packet.template_hints if hasattr(packet, "template_hints") else {}
    input_strategy = getattr(packet, "input_strategy", "none")
    use_basedir = input_strategy in ("generated_fixture_file", "existing_fixture")

    # Build using directives
    usings = ["System"]
    if use_basedir:
        usings.append("System.IO")
    additional = hints.get("additional_usings", []) if hints else []
    if additional:
        for u in additional:
            if u not in usings:
                usings.append(u)
    elif needs_input and not use_basedir:
        parent_ns = packet.target_namespace.rsplit(".", 1)[0] if "." in packet.target_namespace else ""
        if parent_ns and parent_ns not in usings:
            usings.append(parent_ns)
    usings.append(packet.target_namespace)

    # Build body lines
    body: list[str] = []
    body.append(f'            Console.WriteLine("Example: {packet.scenario_id}");')
    body.append("")

    if use_basedir and needs_input:
        # Fixture files are placed in the project — use AppContext.BaseDirectory
        input_files = getattr(packet, "input_files", [])
        if input_files:
            body.append("            // Input file provided by pipeline fixture factory")
            body.append(f'            string inputPath = Path.Combine(AppContext.BaseDirectory, "{input_files[0]}");')
            body.append("")
    elif needs_input:
        body += _generate_input_creation_lines(type_name, hints)

    # Generate method calls
    seen_methods: set[str] = set()
    instance_declared = False
    for method_name in packet.target_methods[:3]:
        if method_name in seen_methods:
            continue
        seen_methods.add(method_name)
        overload = _select_simplest_overload(methods_catalog, method_name)
        if overload is None:
            body.append(f"            // {method_name} — no suitable overload found in catalog")
            continue
        call_lines = _generate_method_call(type_name, overload, kind, hints, instance_declared, use_basedir=use_basedir)
        if call_lines:
            if not overload.get("is_static", False) and kind != "abstract_class":
                instance_declared = True
            body += call_lines
        else:
            body.append(f"            // {method_name} — requires unsupported parameters, skipped")

    body.append("")
    body.append('            Console.WriteLine("Done.");')

    usings_str = "\n".join(f"using {u};" for u in usings)
    body_str = "\n".join(body)

    return f"""{usings_str}

namespace PluginExample
{{
    class Program
    {{
        static void Main(string[] args)
        {{
{body_str}
        }}
    }}
}}
"""


# ---------------------------------------------------------------------------
# Smart template helpers
# ---------------------------------------------------------------------------

_FORMAT_NAME_TO_EXT: dict[str, str] = {
    "html": ".html",
    "pdf": ".pdf",
    "json": ".json",
    "text": ".txt",
    "txt": ".txt",
    "image": ".png",
    "png": ".png",
    "jpg": ".jpg",
    "jpeg": ".jpeg",
    "xlsx": ".xlsx",
    "spreadsheet": ".xlsx",
    "excel": ".xlsx",
    "docx": ".docx",
    "word": ".docx",
    "doc": ".docx",
    "pptx": ".pptx",
    "presentation": ".pptx",
    "slides": ".pptx",
    "eml": ".eml",
    "email": ".eml",
    "mail": ".eml",
    "csv": ".csv",
    "xml": ".xml",
    "svg": ".svg",
    "tiff": ".tiff",
    "bmp": ".bmp",
    "xps": ".xps",
    "epub": ".epub",
    "markdown": ".md",
    "md": ".md",
}


def _infer_output_extension(type_name: str, hints: dict | None = None) -> str:
    """Infer output file extension from type name, then hints, then fallback."""
    # Strip common suffixes to get a format token
    name_lower = type_name.lower()
    for suffix in ("converter", "merger", "splitter", "locker", "compressor", "signer"):
        if name_lower.endswith(suffix):
            token = name_lower[: -len(suffix)]
            if token in _FORMAT_NAME_TO_EXT:
                return _FORMAT_NAME_TO_EXT[token]
            break

    # Try the full name as a format token
    if name_lower in _FORMAT_NAME_TO_EXT:
        return _FORMAT_NAME_TO_EXT[name_lower]

    # Hints fallback
    if hints:
        return hints.get("default_output_extension", ".out")
    return ".out"


def _select_simplest_overload(methods: list[dict], method_name: str) -> dict | None:
    """Pick the simplest safe overload: fewest params, preferring all-string."""
    candidates = [m for m in methods if m.get("name") == method_name and not m.get("is_obsolete")]
    if not candidates:
        return None

    def _score(m: dict) -> tuple:
        params = m.get("parameters", [])
        all_string = all(_is_string_like(p) for p in params)
        return (0 if all_string else 1, len(params))

    candidates.sort(key=_score)
    # Return best candidate only if we can generate safe args for it
    for c in candidates:
        if _can_generate_args(c):
            return c
    return None


def _is_string_like(param: dict) -> bool:
    """Check if a parameter is System.String or System.String[]."""
    t = param.get("type", "")
    return t in ("System.String", "System.String[]", "String", "String[]")


def _can_generate_args(method: dict) -> bool:
    """Check if we can generate safe arguments for all parameters."""
    for p in method.get("parameters", []):
        if not _is_string_like(p):
            return False
    return True


def _generate_smart_args(parameters: list[dict], type_name: str, hints: dict | None = None,
                         use_basedir: bool = False) -> str | None:
    """Generate argument string for a method call. Returns None if unsupported.

    Args:
        use_basedir: If True, wrap input file references in Path.Combine(AppContext.BaseDirectory, ...).
    """
    args: list[str] = []
    ext = _infer_output_extension(type_name, hints)
    default_input = hints.get("default_input_filename", "input.xlsx") if hints else "input.xlsx"
    array_inputs = hints.get("array_input_filenames", ["input1.xlsx", "input2.xlsx"]) if hints else ["input1.xlsx", "input2.xlsx"]

    def _input_ref(filename: str) -> str:
        if use_basedir:
            return f'Path.Combine(AppContext.BaseDirectory, "{filename}")'
        return f'"{filename}"'

    if use_basedir:
        array_str = ", ".join(_input_ref(f) for f in array_inputs)
    else:
        array_str = ", ".join(f'"{f}"' for f in array_inputs)

    for p in parameters:
        pname = p.get("name", "").lower()
        ptype = p.get("type", "")

        if ptype in ("System.String[]", "String[]"):
            args.append(f'new string[] {{ {array_str} }}')
        elif ptype in ("System.String", "String"):
            if any(kw in pname for kw in ("template", "input", "source")):
                args.append(_input_ref(default_input))
            elif any(kw in pname for kw in ("result", "output", "target", "dest")):
                args.append(f'"output{ext}"')
            elif any(kw in pname for kw in ("password", "pwd")):
                args.append('"test-password"')
            else:
                args.append('"sample"')
        else:
            return None
    return ", ".join(args)


def _generate_method_call(type_name: str, method: dict, kind: str, hints: dict | None = None,
                          instance_declared: bool = False, use_basedir: bool = False) -> list[str]:
    """Generate C# code lines for a method call."""
    is_static = method.get("is_static", False)
    params = method.get("parameters", [])
    method_name = method["name"]

    args_str = _generate_smart_args(params, type_name, hints, use_basedir=use_basedir)
    if args_str is None:
        return []

    lines: list[str] = []
    lines.append(f"            // Demonstrate {type_name}.{method_name}")

    if is_static:
        lines.append(f"            {type_name}.{method_name}({args_str});")
    else:
        if kind == "abstract_class":
            return []
        if not instance_declared:
            lines.append(f"            var instance = new {type_name}();")
        lines.append(f"            instance.{method_name}({args_str});")

    return lines


def _needs_input_file_creation(type_details: dict) -> bool:
    """Check if any method takes file-path-like string params."""
    for m in type_details.get("methods", []):
        for p in m.get("parameters", []):
            ptype = p.get("type", "")
            pname = p.get("name", "").lower()
            if ptype in ("System.String", "String") and any(
                kw in pname for kw in ("template", "input", "source")
            ):
                return True
            if ptype in ("System.String[]", "String[]"):
                return True
    return False


def _generate_input_creation_lines(type_name: str, hints: dict | None = None) -> list[str]:
    """Generate C# lines to create input test files."""
    lines: list[str] = []
    is_merger = "merger" in type_name.lower()

    # Use hints if available
    if hints:
        hint_lines = hints.get("merger_input_creation_lines" if is_merger else "input_creation_lines", [])
        if hint_lines:
            lines.append("            // Create input file(s)")
            for line in hint_lines:
                lines.append(f"            {line}")
            lines.append("")
            return lines

    # Backward-compatible Cells fallback when no hints are configured
    if is_merger:
        lines.append("            // Create minimal input files for merging")
        lines.append("            var wb1 = new Workbook();")
        lines.append('            wb1.Worksheets[0].Cells["A1"].PutValue("Sheet1");')
        lines.append('            wb1.Save("input1.xlsx");')
        lines.append("            var wb2 = new Workbook();")
        lines.append('            wb2.Worksheets[0].Cells["A1"].PutValue("Sheet2");')
        lines.append('            wb2.Save("input2.xlsx");')
    else:
        lines.append("            // Create a minimal input file")
        lines.append("            var workbook = new Workbook();")
        lines.append('            workbook.Worksheets[0].Cells["A1"].PutValue("Hello World");')
        lines.append('            workbook.Save("input.xlsx");')
    lines.append("")
    return lines


def _extract_code(response: str) -> str:
    """Extract C# code from LLM response."""
    # Try to find csharp/cs code block
    match = re.search(r'```(?:csharp|cs)\s*\n(.*?)```', response, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Try any generic code block that looks like C#
    for m in re.finditer(r'```\s*\n(.*?)```', response, re.DOTALL):
        code = m.group(1).strip()
        if "using " in code or "namespace " in code or "class " in code:
            return code
    # If response itself looks like C# code, use it directly
    stripped = response.strip()
    if stripped and ("using " in stripped or "namespace " in stripped or "static void Main" in stripped):
        return stripped
    # Return empty — generation failed to produce code
    return ""


def _validate_code(code: str) -> list[str]:
    """Validate generated code for common issues."""
    issues = []

    if "TODO" in code:
        issues.append("Contains TODO placeholder")

    if "NotImplementedException" in code:
        issues.append("Contains NotImplementedException")

    if re.search(r'[A-Z]:\\', code):
        issues.append("Contains hardcoded absolute path")

    if "Version=" in code and "<PackageReference" in code:
        issues.append("Contains inline package version")

    # Forbidden interactive patterns
    if "Console.ReadKey(" in code:
        issues.append("Contains Console.ReadKey() — forbidden in headless CI. Remove it.")

    if "Console.ReadLine(" in code:
        issues.append("Contains Console.ReadLine() — forbidden in headless CI. Remove it.")

    # Forbidden options misuse patterns
    if re.search(r'\(LowCodeLoadOptions\)\s*null', code):
        issues.append(
            "Passes null for LowCodeLoadOptions — this causes NullReferenceException. "
            "Use the simple string-path overload instead, or create a LowCodeLoadOptions "
            "with InputFile set."
        )

    if re.search(r'\(LowCodeSaveOptions\)\s*null', code):
        issues.append(
            "Passes null for LowCodeSaveOptions — this causes NullReferenceException. "
            "Use the simple string-path overload instead, or create a LowCodeSaveOptions "
            "with OutputFile set."
        )

    # Detect empty LowCodeLoadOptions without InputFile assignment
    if re.search(r'new\s+LowCodeLoadOptions\s*\(\s*\)', code):
        if '.InputFile' not in code and '.InputStream' not in code:
            issues.append(
                "Creates LowCodeLoadOptions without setting InputFile or InputStream. "
                "You MUST set InputFile before passing to Process(), or use the simple "
                "string-path overload instead."
            )

    # Detect empty LowCodeSaveOptions without OutputFile assignment
    if re.search(r'new\s+LowCodeSaveOptions\s*\(\s*\)', code):
        if '.OutputFile' not in code and '.OutputStream' not in code:
            issues.append(
                "Creates LowCodeSaveOptions without setting OutputFile or OutputStream. "
                "You MUST set OutputFile before passing to Process(), or use the simple "
                "string-path overload instead."
            )

    # Detect multiple Process() calls — should use only one overload
    process_calls = re.findall(r'\b\w+\.Process\s*\(', code)
    if len(process_calls) > 1:
        issues.append(
            f"Contains {len(process_calls)} Process() calls — use only ONE overload per example. "
            "Remove the extra Process() calls and keep only the simplest string-path overload."
        )

    return issues
