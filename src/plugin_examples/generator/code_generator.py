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
    generation_strategy: str = "llm_generated"  # llm_generated, template_first, catalog_fallback


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
    # Extract per-type constraints early (needed for template_first check)
    _type_name = packet.target_type.split(".")[-1] if packet.target_type else ""
    _ptc = packet.per_type_constraints.get(_type_name, {}) if packet.per_type_constraints else {}

    # Template-first: bypass LLM for known deterministic API patterns.
    # Checked BEFORE the llm_generate is None fallback so that deterministic
    # templates are always preferred, regardless of LLM availability.
    if _ptc.get("template_first"):
        code = _generate_deterministic_template_for_scenario(packet)
        _family = "pdf" if packet.target_namespace.lower().startswith("aspose.pdf") else ""
        _type_short = _type_name.lower()
        tf_issues = _validate_code(code, family=_family, type_short=_type_short)
        tf_issues.extend(_validate_code_from_constraints(code, _ptc))
        if tf_issues:
            logger.error(
                "Template-first code for %s failed validation: %s",
                packet.scenario_id,
                tf_issues,
            )
            return GeneratedExample(
                scenario_id=packet.scenario_id,
                code=code,
                claimed_symbols=packet.approved_symbols,
                status="failed",
                failure_reason=f"Template-first validation failed: {tf_issues}",
            )
        return GeneratedExample(
            scenario_id=packet.scenario_id,
            code=code,
            claimed_symbols=packet.approved_symbols,
            status="generated_template_first",
        )

    if llm_generate is None:
        # Non-template_first type with no LLM available — use generic catalog-driven template
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

    # Detect family from packet namespace for family-specific validation
    _family = "pdf" if packet.target_namespace.lower().startswith("aspose.pdf") else ""
    _type_short = _type_name.lower()

    # Validate generated code — PDF-specific + generic checks
    issues = _validate_code(code, family=_family, type_short=_type_short)

    # Config-driven FORBIDDEN pattern check for all families
    if _ptc:
        issues.extend(_validate_code_from_constraints(code, _ptc))

    if issues and max_repairs > 0:
        logger.info("Attempting repair for %s: %s", packet.scenario_id, issues)
        try:
            # Re-inject all REQUIRED: and FORBIDDEN: constraints for any family so the
            # repair LLM cannot drop critical directives or re-introduce banned patterns.
            all_repair_constraints = [
                c for c in packet.constraints if c.startswith("REQUIRED:") or c.startswith("FORBIDDEN:")
            ]
            constraint_reminder = ""
            if all_repair_constraints:
                constraint_reminder = (
                    "\n\nREQUIRED AND FORBIDDEN PATTERNS (must be respected in fixed code):\n"
                    + "\n".join(all_repair_constraints)
                )
            # For PDF types: add full reference examples to ensure deterministic
            # API patterns even after package version changes (26.5.0+).
            if _family == "pdf" and _type_short == "optimizer":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for Optimizer (your fixed code MUST follow this exact pattern):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "\n"
                    "var document = new Document();\n"
                    "document.Pages.Add();\n"
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new OptimizeOptions();\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    'options.AddOutput(new FileDataSource("output.pdf"));\n'
                    "var result = new Optimizer().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "Optimized" : "No output");\n'
                    "```\n"
                    "CRITICAL: MUST use 'new Optimizer().Process(options)' — instantiate Optimizer then call .Process(). "
                    "MUST use OptimizeOptions. MUST use AddInput(new FileDataSource(...)) and AddOutput(new FileDataSource(...))."
                )
            elif _family == "pdf" and _type_short == "pdfaconverter":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for PdfAConverter (your fixed code MUST follow this exact pattern):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "\n"
                    "var document = new Document();\n"
                    "document.Pages.Add();\n"
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new PdfAConvertOptions();\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    'options.AddOutput(new FileDataSource("output.pdf"));\n'
                    "var result = new PdfAConverter().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "Converted to PDF/A" : "No output");\n'
                    "```\n"
                    "CRITICAL: MUST use 'new PdfAConvertOptions()' (NOT PluginOptions, NOT PdfFormatConversionOptions). "
                    "MUST use 'new PdfAConverter().Process(options)'. "
                    "MUST use AddInput(new FileDataSource(...)) and AddOutput(new FileDataSource(...))."
                )
            elif _family == "pdf" and _type_short == "docconverter":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for DocConverter (your fixed code MUST follow this exact pattern):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "using Aspose.Pdf.Text;\n"
                    "\n"
                    "var document = new Document();\n"
                    "var page = document.Pages.Add();\n"
                    'page.Paragraphs.Add(new TextFragment("LowCode DocConverter Test"));\n'
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new PdfToDocOptions();\n"
                    "options.SaveFormat = Aspose.Pdf.LowCode.SaveFormat.DocX;\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    'options.AddOutput(new FileDataSource("output.docx"));\n'
                    "var result = new DocConverter().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "Converted to DOCX" : "No output");\n'
                    "```\n"
                    "CRITICAL: MUST use 'new PdfToDocOptions()' (NOT PdfConverterOptions which is abstract). "
                    "MUST set 'options.SaveFormat = Aspose.Pdf.LowCode.SaveFormat.DocX' (fully-qualified to avoid CS0104 ambiguity with Aspose.Pdf.SaveFormat) — this line is non-negotiable. "
                    "MUST use 'new DocConverter().Process(options)'. "
                    "MUST use AddInput(new FileDataSource(...)) and AddOutput(new FileDataSource(...))."
                )
            elif _family == "pdf" and _type_short == "xlsconverter":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for XlsConverter (your fixed code MUST follow this exact pattern):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "\n"
                    "var document = new Document();\n"
                    "document.Pages.Add();\n"
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new PdfToXlsOptions();\n"
                    "options.Format = PdfToXlsOptions.ExcelFormat.XLSX;\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    'options.AddOutput(new FileDataSource("output.xlsx"));\n'
                    "var result = new XlsConverter().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "Converted to XLSX" : "No output");\n'
                    "```\n"
                    "CRITICAL: MUST use 'new PdfToXlsOptions()' (NOT PdfConverterOptions which is abstract). "
                    "MUST set 'options.Format = PdfToXlsOptions.ExcelFormat.XLSX' — this exact line is required. "
                    "MUST use 'new XlsConverter().Process(options)'. "
                    "MUST use AddInput(new FileDataSource(...)) and AddOutput(new FileDataSource(...))."
                )
            elif _family == "pdf" and _type_short == "html":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for Html (HTML-to-PDF converter — your fixed code MUST follow this exact pattern):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using System.IO;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "\n"
                    'File.WriteAllText("input.html", "<html><body><h1>Hello LowCode</h1><p>HTML to PDF.</p></body></html>");\n'
                    "\n"
                    "var options = new HtmlToPdfOptions();\n"
                    'options.AddInput(new FileDataSource("input.html"));\n'
                    'options.AddOutput(new FileDataSource("output.pdf"));\n'
                    "var result = new Html().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "HTML converted to PDF" : "No output");\n'
                    "```\n"
                    "CRITICAL: MUST use 'new HtmlToPdfOptions()' (NOT HtmlLoadOptions). "
                    "MUST use 'new Html().Process(options)'. "
                    'Input MUST be an HTML file created with File.WriteAllText("input.html", htmlContent). '
                    "Do NOT create a PDF Document. Do NOT use TextFragment. Input is HTML, not PDF. "
                    'MUST use AddInput(new FileDataSource("input.html")) — .html extension, NOT .pdf.'
                )
            # For PDF TextExtractor: add full reference example to guide the LLM
            # beyond the 4-line snippet — non-deterministic failures need this.
            elif _family == "pdf" and _type_short == "textextractor":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for TextExtractor (your fixed code MUST follow this exact pattern):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using System.IO;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "using Aspose.Pdf.Text;\n"
                    "\n"
                    "var document = new Document();\n"
                    "var page = document.Pages.Add();\n"
                    'page.Paragraphs.Add(new TextFragment("Sample text for extraction."));\n'
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new TextExtractorOptions();\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    "var result = new TextExtractor().Process(options);\n"
                    "if (result.ResultCollection.Count > 0 && result.ResultCollection[0] is StringResult sr)\n"
                    '    Console.WriteLine("Extracted text: " + sr.Text);\n'
                    "else\n"
                    '    Console.WriteLine("No text extracted.");\n'
                    "```\n"
                    "CRITICAL: Do NOT use TextAbsorber. Do NOT use AddOutput(). Do NOT access .Value — use .Text."
                )
            elif _family == "pdf" and _type_short == "jpeg":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for Jpeg (your fixed code MUST use output.jpg — NEVER output.pdf):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "\n"
                    "var document = new Document();\n"
                    "document.Pages.Add();\n"
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new JpegOptions();\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    'options.AddOutput(new FileDataSource("output.jpg"));\n'
                    "var result = new Jpeg().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "JPEG created" : "No output");\n'
                    "```\n"
                    'CRITICAL: output filename MUST be "output.jpg" (not output.pdf, not output.jpeg). '
                    "The Jpeg plugin writes a .jpg file. Do NOT use File.Exists — use result.ResultCollection.Count > 0."
                )
            elif _family == "pdf" and _type_short == "tiff":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for Tiff (your fixed code MUST use output.tiff — NEVER output.tif):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "\n"
                    "var document = new Document();\n"
                    "document.Pages.Add();\n"
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new TiffOptions();\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    'options.AddOutput(new FileDataSource("output.tiff"));\n'
                    "var result = new Tiff().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "TIFF created" : "No output");\n'
                    "```\n"
                    'CRITICAL: output filename MUST be "output.tiff" (four letters — NEVER output.tif). '
                    "Do NOT use File.Exists — use result.ResultCollection.Count > 0."
                )
            elif _family == "pdf" and _type_short == "tocgenerator":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for TocGenerator (your fixed code MUST follow this exact pattern):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "\n"
                    "var document = new Document();\n"
                    "document.Pages.Add();\n"
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new TocOptions();\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    'options.AddOutput(new FileDataSource("output.pdf"));\n'
                    "var result = new TocGenerator().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "TOC added" : "No output");\n'
                    "```\n"
                    "CRITICAL: use TocOptions (not PluginOptions which is abstract). "
                    "AddInput + AddOutput pattern identical to other converters. "
                    "Validate via result.ResultCollection.Count > 0."
                )
            elif _family == "pdf" and _type_short == "imageextractor":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for ImageExtractor (your fixed code MUST follow this exact pattern):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "\n"
                    "var document = new Document();\n"
                    "var page = document.Pages.Add();\n"
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new ImageExtractorOptions();\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    "var result = new ImageExtractor().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "Images extracted" : "No images found");\n'
                    "```\n"
                    "CRITICAL: use ImageExtractorOptions (not PluginOptions). "
                    "ImageExtractor is an EXTRACTOR (like TextExtractor) — no AddOutput needed; images are in ResultCollection. "
                    "Validate via result.ResultCollection.Count >= 0 (even 0 is valid if PDF has no images). "
                    "Do NOT use PdfExtractor from Aspose.Pdf.Facades — use LowCode ImageExtractor."
                )
            elif _family == "pdf" and _type_short == "png":
                constraint_reminder += (
                    "\n\nMANDATORY REFERENCE EXAMPLE for Png (output validation MUST use result.ResultCollection.Count > 0):\n"
                    "```csharp\n"
                    "using System;\n"
                    "using Aspose.Pdf;\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "\n"
                    "var document = new Document();\n"
                    "document.Pages.Add();\n"
                    'document.Save("input.pdf");\n'
                    "\n"
                    "var options = new PngOptions();\n"
                    'options.AddInput(new FileDataSource("input.pdf"));\n'
                    'options.AddOutput(new FileDataSource("output.png"));\n'
                    "var result = new Png().Process(options);\n"
                    'Console.WriteLine(result.ResultCollection.Count > 0 ? "PNG created" : "No output");\n'
                    "```\n"
                    'CRITICAL: validate using result.ResultCollection.Count > 0, NOT File.Exists("output.png"). '
                    "The Png plugin creates page-numbered output files (e.g. output_0.png). "
                    'File.Exists("output.png") will always return false.'
                )
            repair_prompt = f"Fix these issues in the code:\n{issues}" f"{constraint_reminder}\n\nCode:\n{code}"
            response = llm_generate(repair_prompt, packet.system_prompt)
            repaired_code = _extract_code(response)
            # Re-validate repaired code — reject if still failing
            post_repair_issues = _validate_code(repaired_code, family=_family, type_short=_type_short)
            if _ptc:
                post_repair_issues.extend(_validate_code_from_constraints(repaired_code, _ptc))
            if post_repair_issues:
                logger.warning(
                    "Repair for %s still has validation issues: %s",
                    packet.scenario_id,
                    post_repair_issues,
                )
                return GeneratedExample(
                    scenario_id=packet.scenario_id,
                    code=repaired_code,
                    claimed_symbols=packet.approved_symbols,
                    repair_attempts=1,
                    status="failed",
                    failure_reason=f"Post-repair validation failed: {post_repair_issues}",
                )
            code = repaired_code
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


def _generate_deterministic_template_for_scenario(packet: PromptPacket) -> str:
    """Return a verified, harness-validated C# script for known PDF LowCode types.

    Called when ``template_first: true`` is set in per_type_constraints.  The
    templates are the same code shown as MANDATORY REFERENCE EXAMPLEs in the
    repair path; keeping them in one place avoids drift.

    For unrecognised types the generic ``_generate_template`` fallback is used.
    """
    type_name = packet.target_type.split(".")[-1] if packet.target_type else ""
    t = type_name.lower()

    if t == "docconverter":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "using Aspose.Pdf.Text;\n"
            "\n"
            "var document = new Document();\n"
            "var page = document.Pages.Add();\n"
            'page.Paragraphs.Add(new TextFragment("LowCode DocConverter Test"));\n'
            'document.Save("input.pdf");\n'
            "\n"
            "var options = new PdfToDocOptions();\n"
            "options.SaveFormat = Aspose.Pdf.LowCode.SaveFormat.DocX;\n"
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.docx"));\n'
            "var result = new DocConverter().Process(options);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "Converted to DOCX" : "No output");\n'
        )
    if t == "xlsconverter":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "\n"
            "var document = new Document();\n"
            "document.Pages.Add();\n"
            'document.Save("input.pdf");\n'
            "\n"
            "var options = new PdfToXlsOptions();\n"
            "options.Format = PdfToXlsOptions.ExcelFormat.XLSX;\n"
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.xlsx"));\n'
            "var result = new XlsConverter().Process(options);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "Converted to XLSX" : "No output");\n'
        )
    if t == "html":
        return (
            "using System;\n"
            "using System.IO;\n"
            "using Aspose.Pdf.LowCode;\n"
            "\n"
            'File.WriteAllText("input.html", "<html><body><h1>Hello LowCode</h1><p>HTML to PDF.</p></body></html>");\n'
            "\n"
            "var options = new HtmlToPdfOptions();\n"
            'options.AddInput(new FileDataSource("input.html"));\n'
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            "var result = new Html().Process(options);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "HTML converted to PDF" : "No output");\n'
        )
    if t == "jpeg":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "\n"
            "var document = new Document();\n"
            "document.Pages.Add();\n"
            'document.Save("input.pdf");\n'
            "\n"
            "var options = new JpegOptions();\n"
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.jpg"));\n'
            "var result = new Jpeg().Process(options);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "JPEG created" : "No output");\n'
        )
    if t == "tiff":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "\n"
            "var document = new Document();\n"
            "document.Pages.Add();\n"
            'document.Save("input.pdf");\n'
            "\n"
            "var options = new TiffOptions();\n"
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.tiff"));\n'
            "var result = new Tiff().Process(options);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "TIFF created" : "No output");\n'
        )
    if t == "png":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "\n"
            "var document = new Document();\n"
            "document.Pages.Add();\n"
            'document.Save("input.pdf");\n'
            "\n"
            "var options = new PngOptions();\n"
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.png"));\n'
            "var result = new Png().Process(options);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "PNG created" : "No output");\n'
        )
    if t == "tablegenerator":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "using Aspose.Pdf.Text;\n"
            "\n"
            "var document = new Document();\n"
            "document.Pages.Add();\n"
            'document.Save("input.pdf");\n'
            "\n"
            "// Build TableOptions separately so AddInput/AddOutput are called on the\n"
            "// TableOptions instance, not on the TableCellBuilder chain end.\n"
            "var options = new TableOptions();\n"
            "options.InsertPageBefore(1);\n"
            "options.AddTable()\n"
            "    .AddRow()\n"
            '        .AddCell().AddParagraph(new TextFragment("Header 1"))\n'
            '        .AddCell().AddParagraph(new TextFragment("Header 2"));\n'
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            "var result = new TableGenerator().Process(options);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "Table added" : "No output");\n'
        )
    if t == "tocgenerator":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "\n"
            "var document = new Document();\n"
            "document.Pages.Add();\n"
            'document.Save("input.pdf");\n'
            "\n"
            "var options = new TocOptions();\n"
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            "var result = new TocGenerator().Process(options);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "TOC added" : "No output");\n'
        )
    if t == "imageextractor":
        return (
            "using System;\n"
            "using System.IO;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "\n"
            "// Minimal 1x1 red pixel BMP (58 bytes) as fixture image\n"
            "var bmpBytes = new byte[] {\n"
            "    66, 77, 58, 0, 0, 0, 0, 0, 0, 0, 54, 0, 0, 0,\n"
            "    40, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 24, 0,\n"
            "    0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,\n"
            "    0, 0, 0, 0, 0, 0, 0, 0,\n"
            "    0, 0, 255, 0\n"
            "};\n"
            "var document = new Document();\n"
            "var page = document.Pages.Add();\n"
            "page.Resources.Images.Add(new MemoryStream(bmpBytes));\n"
            'document.Save("input.pdf");\n'
            "\n"
            "var options = new ImageExtractorOptions();\n"
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            "var result = new ImageExtractor().Process(options);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "Images extracted" : "No images found");\n'
        )
    if t == "security":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "using Aspose.Pdf.Facades;\n"
            "\n"
            "var doc = new Document();\n"
            "doc.Pages.Add();\n"
            'doc.Save("input.pdf");\n'
            "\n"
            "DocumentPrivilege privilege = DocumentPrivilege.ForbidAll;\n"
            "privilege.AllowPrint = true;\n"
            "\n"
            'var encOptions = new EncryptionOptions("owner123", "user123", privilege);\n'
            'encOptions.AddInput(new FileDataSource("input.pdf"));\n'
            'encOptions.AddOutput(new FileDataSource("output.pdf"));\n'
            "var result = new Security().Process(encOptions);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "PDF encrypted" : "No output");\n'
        )
    if t == "formflattener":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "using Aspose.Pdf.Forms;\n"
            "\n"
            "var doc = new Document();\n"
            "var page = doc.Pages.Add();\n"
            "var textBox = new TextBoxField(page, new Aspose.Pdf.Rectangle(100, 700, 300, 730));\n"
            'textBox.PartialName = "TextField1";\n'
            'textBox.Value = "Hello AcroForm";\n'
            "doc.Form.Add(textBox, 1);\n"
            'doc.Save("input.pdf");\n'
            "\n"
            "var flattenOptions = new FormFlattenAllFieldsOptions();\n"
            'flattenOptions.AddInput(new FileDataSource("input.pdf"));\n'
            'flattenOptions.AddOutput(new FileDataSource("output.pdf"));\n'
            "var result = new FormFlattener().Process(flattenOptions);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "Form flattened" : "No output");\n'
        )
    if t == "formeditor":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "using Aspose.Pdf.Forms;\n"
            "\n"
            "var doc = new Document();\n"
            "var page = doc.Pages.Add();\n"
            "var textBox = new TextBoxField(page, new Aspose.Pdf.Rectangle(100, 700, 300, 730));\n"
            'textBox.PartialName = "TextField1";\n'
            'textBox.Value = "Hello AcroForm";\n'
            "doc.Form.Add(textBox, 1);\n"
            'doc.Save("input.pdf");\n'
            "\n"
            "var removeOptions = new FormRemoveAllFieldsOptions();\n"
            'removeOptions.AddInput(new FileDataSource("input.pdf"));\n'
            'removeOptions.AddOutput(new FileDataSource("output.pdf"));\n'
            "var result = new FormEditor().Process(removeOptions);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "Form fields removed" : "No output");\n'
        )
    if t == "formexporter":
        return (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "using Aspose.Pdf.Forms;\n"
            "\n"
            "var doc = new Document();\n"
            "var page = doc.Pages.Add();\n"
            "var textBox = new TextBoxField(page, new Aspose.Pdf.Rectangle(100, 700, 300, 730));\n"
            'textBox.PartialName = "TextField1";\n'
            'textBox.Value = "ExportedValue";\n'
            "doc.Form.Add(textBox, 1);\n"
            'doc.Save("input.pdf");\n'
            "\n"
            "var exportOptions = new FormExporterToJsonOptions();\n"
            'exportOptions.AddInput(new FileDataSource("input.pdf"));\n'
            'exportOptions.AddOutput(new FileDataSource("output.json"));\n'
            "var result = new FormExporter().Process(exportOptions);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "Form exported to JSON" : "No output");\n'
        )
    if t == "signature":
        return (
            "using System;\n"
            "using System.IO;\n"
            "using System.Security.Cryptography;\n"
            "using System.Security.Cryptography.X509Certificates;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "using Aspose.Pdf.Text;\n"
            "\n"
            "// Create self-signed PFX fixture (no TSA/CA server required)\n"
            "using var rsa = RSA.Create(2048);\n"
            'var req = new CertificateRequest("cn=TestSign", rsa, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);\n'
            "req.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));\n"
            "var cert = req.CreateSelfSigned(DateTimeOffset.Now, DateTimeOffset.Now.AddYears(1));\n"
            'var pfxBytes = cert.Export(X509ContentType.Pfx, "testpassword");\n'
            'File.WriteAllBytes("test.pfx", pfxBytes);\n'
            "\n"
            "// Create PDF input fixture\n"
            "var doc = new Document();\n"
            "var page = doc.Pages.Add();\n"
            'page.Paragraphs.Add(new TextFragment("Document for digital signing"));\n'
            'doc.Save("input.pdf");\n'
            "\n"
            "// Apply digital signature using Signature LowCode plugin\n"
            'var signOptions = new SignOptions("test.pfx", "testpassword");\n'
            "signOptions.PageNumber = 1;\n"
            'signOptions.Reason = "Authorized Signature";\n'
            'signOptions.Contact = "signatory@example.com";\n'
            'signOptions.Location = "Document Processing";\n'
            'signOptions.AddInput(new FileDataSource("input.pdf"));\n'
            'signOptions.AddOutput(new FileDataSource("output.pdf"));\n'
            "var result = new Signature().Process(signOptions);\n"
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "PDF signed successfully." : "No output produced.");\n'
        )
    # ---------------------------------------------------------------------------
    # Diagram family deterministic templates
    # Distinguish from PDF family using target_namespace.
    # ---------------------------------------------------------------------------
    _ns = (packet.target_namespace or "").lower()

    # ---------------------------------------------------------------------------
    # PDF family deterministic templates (namespace-guarded to avoid colliding
    # with words Merger which shares the same short type name)
    # ---------------------------------------------------------------------------
    if "aspose.pdf" in _ns:
        if t == "merger":
            return (
                "using System;\n"
                "using Aspose.Pdf;\n"
                "using Aspose.Pdf.LowCode;\n"
                "using Aspose.Pdf.Text;\n"
                "\n"
                "var document1 = new Document();\n"
                "var page1 = document1.Pages.Add();\n"
                'page1.Paragraphs.Add(new TextFragment("Document 1 - Page 1"));\n'
                'document1.Save("input1.pdf");\n'
                "\n"
                "var document2 = new Document();\n"
                "var page2 = document2.Pages.Add();\n"
                'page2.Paragraphs.Add(new TextFragment("Document 2 - Page 1"));\n'
                'document2.Save("input2.pdf");\n'
                "\n"
                "var options = new MergeOptions();\n"
                'options.AddInput(new FileDataSource("input1.pdf"));\n'
                'options.AddInput(new FileDataSource("input2.pdf"));\n'
                'options.AddOutput(new FileDataSource("output.pdf"));\n'
                "var result = new Merger().Process(options);\n"
                'Console.WriteLine(result.ResultCollection.Count > 0 ? "Merged successfully" : "No output");\n'
            )
        if t == "optimizer":
            return (
                "using System;\n"
                "using Aspose.Pdf;\n"
                "using Aspose.Pdf.LowCode;\n"
                "using Aspose.Pdf.Text;\n"
                "\n"
                "var document = new Document();\n"
                "var page = document.Pages.Add();\n"
                'page.Paragraphs.Add(new TextFragment("LowCode Optimizer Test"));\n'
                'document.Save("input.pdf");\n'
                "\n"
                "var options = new OptimizeOptions();\n"
                'options.AddInput(new FileDataSource("input.pdf"));\n'
                'options.AddOutput(new FileDataSource("output.pdf"));\n'
                "var result = new Optimizer().Process(options);\n"
                'Console.WriteLine(result.ResultCollection.Count > 0 ? "Optimized successfully" : "No output");\n'
            )
        if t == "splitter":
            return (
                "using System;\n"
                "using Aspose.Pdf;\n"
                "using Aspose.Pdf.LowCode;\n"
                "using Aspose.Pdf.Text;\n"
                "\n"
                "var document = new Document();\n"
                "for (int i = 1; i <= 3; i++)\n"
                "{\n"
                "    var pg = document.Pages.Add();\n"
                '    pg.Paragraphs.Add(new TextFragment($"Page {i}"));\n'
                "}\n"
                'document.Save("input.pdf");\n'
                "\n"
                "var options = new SplitOptions();\n"
                'options.AddInput(new FileDataSource("input.pdf"));\n'
                'options.AddOutput(new FileDataSource("output_page1.pdf"));\n'
                'options.AddOutput(new FileDataSource("output_page2.pdf"));\n'
                'options.AddOutput(new FileDataSource("output_page3.pdf"));\n'
                "var result = new Splitter().Process(options);\n"
                "Console.WriteLine(result.ResultCollection.Count > 0\n"
                '    ? $"Split into {result.ResultCollection.Count} file(s)"\n'
                '    : "No output");\n'
            )
        if t == "pdfaconverter":
            return (
                "using System;\n"
                "using Aspose.Pdf;\n"
                "using Aspose.Pdf.LowCode;\n"
                "using Aspose.Pdf.Text;\n"
                "\n"
                "var document = new Document();\n"
                "var page = document.Pages.Add();\n"
                'page.Paragraphs.Add(new TextFragment("LowCode PDF/A Converter Test"));\n'
                'document.Save("input.pdf");\n'
                "\n"
                "var options = new PdfAConvertOptions();\n"
                "options.PdfAVersion = PdfAStandardVersion.PDF_A_1B;\n"
                'options.AddInput(new FileDataSource("input.pdf"));\n'
                'options.AddOutput(new FileDataSource("output.pdf"));\n'
                "var result = new PdfAConverter().Process(options);\n"
                'Console.WriteLine(result.ResultCollection.Count > 0 ? "Converted to PDF/A-1B" : "No output");\n'
            )
        if t == "textextractor":
            return (
                "using System;\n"
                "using Aspose.Pdf;\n"
                "using Aspose.Pdf.LowCode;\n"
                "using Aspose.Pdf.Text;\n"
                "\n"
                "var document = new Document();\n"
                "var page = document.Pages.Add();\n"
                'page.Paragraphs.Add(new TextFragment("Hello, LowCode TextExtractor!"));\n'
                'document.Save("input.pdf");\n'
                "\n"
                "var options = new TextExtractorOptions();\n"
                'options.AddInput(new FileDataSource("input.pdf"));\n'
                "var result = new TextExtractor().Process(options);\n"
                "Console.WriteLine(result.ResultCollection.Count > 0\n"
                '    ? $"Extracted text from {result.ResultCollection.Count} page(s)"\n'
                '    : "No text extracted");\n'
            )

    if "aspose.diagram" in _ns:
        if t == "diagramconverter":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Diagram;\n"
                "using Aspose.Diagram.LowCode;\n"
                "\n"
                'var inputPath = "input.vsdx";\n'
                "var diagram = new Diagram();\n"
                "var page = diagram.Pages[0];\n"
                "long shapeId = page.DrawEllipse(1.0, 1.0, 2.0, 2.0);\n"
                "var shape = page.Shapes.GetShape(shapeId);\n"
                "if (shape != null)\n"
                "{\n"
                '    shape.Name = "SampleShape";\n'
                "    shape.XForm.PinX.Value = 2.0;\n"
                "    shape.XForm.PinY.Value = 2.0;\n"
                "    shape.XForm.Width.Value = 1.0;\n"
                "    shape.XForm.Height.Value = 1.0;\n"
                "}\n"
                "diagram.Save(inputPath, SaveFileFormat.Vsdx);\n"
                "\n"
                'var outputPath = "output.vdx";\n'
                "DiagramConverter.Process(inputPath, outputPath);\n"
                "\n"
                "Console.WriteLine(File.Exists(outputPath)\n"
                "    ? $\"Conversion succeeded, output file created at '{outputPath}'.\"\n"
                "    : $\"Conversion failed, output file not found at '{outputPath}'.\");\n"
            )
        if t == "pdfconverter":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Diagram;\n"
                "using Aspose.Diagram.LowCode;\n"
                "\n"
                'var inputPath = "input.vsdx";\n'
                "var diagram = new Diagram();\n"
                "var page = diagram.Pages[0];\n"
                "long shapeId = page.DrawEllipse(1.0, 1.0, 2.0, 2.0);\n"
                "var shape = page.Shapes.GetShape(shapeId);\n"
                "if (shape != null)\n"
                "{\n"
                '    shape.Name = "SampleShape";\n'
                "    shape.XForm.PinX.Value = 2.0;\n"
                "    shape.XForm.PinY.Value = 2.0;\n"
                "    shape.XForm.Width.Value = 1.0;\n"
                "    shape.XForm.Height.Value = 1.0;\n"
                "}\n"
                "diagram.Save(inputPath, SaveFileFormat.Vsdx);\n"
                "\n"
                'var outputPath = "output.pdf";\n'
                "PdfConverter.Process(inputPath, outputPath);\n"
                "\n"
                "Console.WriteLine(File.Exists(outputPath)\n"
                '    ? $"PDF generated successfully: {outputPath}"\n'
                "    : $\"PDF conversion failed, output not found at '{outputPath}'.\");\n"
            )

    # ---------------------------------------------------------------------------
    # Cells family deterministic templates
    # ---------------------------------------------------------------------------
    if "aspose.cells" in _ns:
        if t == "spreadsheetmerger":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Cells.LowCode;\n"
                "\n"
                "namespace PluginExample\n"
                "{\n"
                "    class Program\n"
                "    {\n"
                "        static void Main(string[] args)\n"
                "        {\n"
                '            Console.WriteLine("Example: cells-spreadsheet-merger");\n'
                "\n"
                '            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");\n'
                '            string input1Path = Path.Combine(AppContext.BaseDirectory, "input1.xlsx");\n'
                '            string input2Path = Path.Combine(AppContext.BaseDirectory, "input2.xlsx");\n'
                "            File.Copy(inputPath, input1Path, overwrite: true);\n"
                "            File.Copy(inputPath, input2Path, overwrite: true);\n"
                "\n"
                '            SpreadsheetMerger.Process(new string[] { input1Path, input2Path }, "output.xlsx");\n'
                "\n"
                '            Console.WriteLine("Done.");\n'
                "        }\n"
                "    }\n"
                "}\n"
            )

    # ---------------------------------------------------------------------------
    # Words family deterministic templates
    # ---------------------------------------------------------------------------
    if "aspose.words" in _ns:
        if t == "merger":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Words;\n"
                "using Aspose.Words.LowCode;\n"
                "\n"
                "namespace PluginExample\n"
                "{\n"
                "    class Program\n"
                "    {\n"
                "        static void Main(string[] args)\n"
                "        {\n"
                '            Console.WriteLine("Example: words-merger");\n'
                "\n"
                '            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");\n'
                '            string input1Path = Path.Combine(AppContext.BaseDirectory, "input1.docx");\n'
                '            string input2Path = Path.Combine(AppContext.BaseDirectory, "input2.docx");\n'
                "            File.Copy(inputPath, input1Path, overwrite: true);\n"
                "            File.Copy(inputPath, input2Path, overwrite: true);\n"
                "\n"
                '            Merger.Merge("output.docx", new string[] { input1Path, input2Path });\n'
                "\n"
                '            Console.WriteLine("Done.");\n'
                "        }\n"
                "    }\n"
                "}\n"
            )
        if t == "watermarker":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Words.LowCode;\n"
                "\n"
                "namespace PluginExample\n"
                "{\n"
                "    class Program\n"
                "    {\n"
                "        static void Main(string[] args)\n"
                "        {\n"
                '            Console.WriteLine("Example: words-watermarker");\n'
                "\n"
                '            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.docx");\n'
                "\n"
                '            Watermarker.SetText(inputPath, "output_text_watermark.docx", "Confidential");\n'
                "\n"
                '            string imagePath = Path.Combine(AppContext.BaseDirectory, "watermark.bmp");\n'
                "            byte[] bmpBytes = new byte[] {\n"
                "                0x42, 0x4D, 0x3A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x36, 0x00,\n"
                "                0x00, 0x00, 0x28, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,\n"
                "                0x00, 0x00, 0x01, 0x00, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00,\n"
                "                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,\n"
                "                0x00, 0x00, 0x00, 0x00, 0x00, 0x00,\n"
                "                0xFF, 0x00, 0x00, 0x00\n"
                "            };\n"
                "            File.WriteAllBytes(imagePath, bmpBytes);\n"
                '            Watermarker.SetImage(inputPath, "output_image_watermark.docx", imagePath);\n'
                "\n"
                '            Console.WriteLine("Done.");\n'
                "        }\n"
                "    }\n"
                "}\n"
            )
        if t == "comparer":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Words;\n"
                "using Aspose.Words.LowCode;\n"
                "\n"
                "namespace PluginExample\n"
                "{\n"
                "    class Program\n"
                "    {\n"
                "        static void Main(string[] args)\n"
                "        {\n"
                '            Console.WriteLine("Example: words-comparer");\n'
                "\n"
                '            string v1Path = "input_v1.docx";\n'
                '            string v2Path = "input_v2.docx";\n'
                "\n"
                "            var doc1 = new Document();\n"
                "            var builder1 = new DocumentBuilder(doc1);\n"
                '            builder1.Writeln("This is version 1 of the document.");\n'
                "            doc1.Save(v1Path);\n"
                "\n"
                "            var doc2 = new Document();\n"
                "            var builder2 = new DocumentBuilder(doc2);\n"
                '            builder2.Writeln("This is version 2 of the document with changes.");\n'
                "            doc2.Save(v2Path);\n"
                "\n"
                '            string outputPath = "output.docx";\n'
                '            Comparer.Compare(v1Path, v2Path, outputPath, "Author", DateTime.UtcNow);\n'
                "\n"
                "            Console.WriteLine(File.Exists(outputPath)\n"
                '                ? $"Comparison succeeded: {outputPath}"\n'
                '                : "Comparison failed: output not found.");\n'
                "        }\n"
                "    }\n"
                "}\n"
            )
        if t == "mailmerger":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Words;\n"
                "using Aspose.Words.LowCode;\n"
                "\n"
                "namespace PluginExample\n"
                "{\n"
                "    class Program\n"
                "    {\n"
                "        static void Main(string[] args)\n"
                "        {\n"
                '            Console.WriteLine("Example: words-mail-merger");\n'
                "\n"
                '            string templatePath = "template.docx";\n'
                "            var doc = new Document();\n"
                "            var builder = new DocumentBuilder(doc);\n"
                '            builder.Write("Hello, ");\n'
                '            builder.InsertField("MERGEFIELD FirstName");\n'
                '            builder.Write(" ");\n'
                '            builder.InsertField("MERGEFIELD LastName");\n'
                '            builder.Writeln("! Welcome to the LowCode example.");\n'
                "            doc.Save(templatePath);\n"
                "\n"
                '            string outputPath = "output.docx";\n'
                '            string[] fieldNames = { "FirstName", "LastName" };\n'
                '            string[] fieldValues = { "John", "Doe" };\n'
                "            MailMerger.Execute(templatePath, outputPath, fieldNames, fieldValues);\n"
                "\n"
                "            Console.WriteLine(File.Exists(outputPath)\n"
                '                ? $"Mail merge succeeded: {outputPath}"\n'
                '                : "Mail merge failed: output not found.");\n'
                "        }\n"
                "    }\n"
                "}\n"
            )
        if t == "reportbuilder":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Words;\n"
                "using Aspose.Words.LowCode;\n"
                "\n"
                "namespace PluginExample\n"
                "{\n"
                "    class Program\n"
                "    {\n"
                "        static void Main(string[] args)\n"
                "        {\n"
                '            Console.WriteLine("Example: words-report-builder");\n'
                "\n"
                '            string templatePath = "template.docx";\n'
                "            var doc = new Document();\n"
                "            var builder = new DocumentBuilder(doc);\n"
                '            builder.Writeln("Report: <<[Name]>>");\n'
                '            builder.Writeln("Value: <<[Value]>>");\n'
                "            doc.Save(templatePath);\n"
                "\n"
                '            string outputPath = "output.docx";\n'
                '            var data = new ReportData { Name = "LowCode Report", Value = 42 };\n'
                "            ReportBuilder.BuildReport(templatePath, outputPath, data);\n"
                "\n"
                "            Console.WriteLine(File.Exists(outputPath)\n"
                '                ? $"Report built: {outputPath}"\n'
                '                : "Report build failed: output not found.");\n'
                "        }\n"
                "    }\n"
                "\n"
                "    public class ReportData\n"
                "    {\n"
                "        public string Name { get; set; }\n"
                "        public int Value { get; set; }\n"
                "    }\n"
                "}\n"
            )

    # ---------------------------------------------------------------------------
    # Slides family deterministic templates
    # Aspose.Slides.LowCode.Convert conflicts with System.Convert — must
    # use fully-qualified type name Aspose.Slides.LowCode.Convert.ToPdf().
    # ---------------------------------------------------------------------------
    if "aspose.slides" in _ns:
        if t == "convert":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Slides;\n"
                "using Aspose.Slides.Export;\n"
                "using Aspose.Slides.LowCode;\n"
                "\n"
                "namespace PluginExample\n"
                "{\n"
                "    class Program\n"
                "    {\n"
                "        static void Main(string[] args)\n"
                "        {\n"
                '            Console.WriteLine("Example: slides-convert");\n'
                "\n"
                "            // Create input PPTX programmatically\n"
                '            string inputPath = "input.pptx";\n'
                "            using (var pres = new Presentation())\n"
                "            {\n"
                "                pres.Slides[0].Shapes.AddAutoShape(\n"
                "                    Aspose.Slides.ShapeType.Rectangle, 100, 100, 200, 50);\n"
                "                pres.Save(inputPath, SaveFormat.Pptx);\n"
                "            }\n"
                "\n"
                "            // Convert PPTX to PDF using LowCode Convert\n"
                "            // Use fully-qualified name to avoid ambiguity with System.Convert\n"
                '            string outputPath = "output.pdf";\n'
                "            Aspose.Slides.LowCode.Convert.ToPdf(inputPath, outputPath);\n"
                "\n"
                "            Console.WriteLine(File.Exists(outputPath)\n"
                '                ? $"Conversion succeeded: {outputPath}"\n'
                '                : "Conversion failed: output file not found.");\n'
                "        }\n"
                "    }\n"
                "}\n"
            )
        if t == "compress":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using Aspose.Slides;\n"
                "using Aspose.Slides.Export;\n"
                "using Aspose.Slides.LowCode;\n"
                "\n"
                "namespace PluginExample\n"
                "{\n"
                "    class Program\n"
                "    {\n"
                "        static void Main(string[] args)\n"
                "        {\n"
                '            Console.WriteLine("Example: slides-compress");\n'
                "\n"
                '            string inputPath = "input.pptx";\n'
                "            using (var pres = new Presentation())\n"
                "            {\n"
                "                pres.Slides[0].Shapes.AddAutoShape(\n"
                "                    Aspose.Slides.ShapeType.Rectangle, 100, 100, 200, 50);\n"
                "                pres.Save(inputPath, SaveFormat.Pptx);\n"
                "            }\n"
                "\n"
                '            string outputPath = "output.pptx";\n'
                "            using (var pres = new Presentation(inputPath))\n"
                "            {\n"
                "                Compress.RemoveUnusedLayoutSlides(pres);\n"
                "                pres.Save(outputPath, SaveFormat.Pptx);\n"
                "            }\n"
                "\n"
                "            Console.WriteLine(File.Exists(outputPath)\n"
                '                ? $"Compression succeeded: {outputPath}"\n'
                '                : "Compression failed: output file not found.");\n'
                "        }\n"
                "    }\n"
                "}\n"
            )

    # ---------------------------------------------------------------------------
    # Email family deterministic templates
    # ---------------------------------------------------------------------------
    if "aspose.email" in _ns:
        if t == "converter":
            return (
                "using System;\n"
                "using System.IO;\n"
                "using System.Threading.Tasks;\n"
                "using Aspose.Email.LowCode;\n"
                "\n"
                "namespace PluginExample\n"
                "{\n"
                "    class Program\n"
                "    {\n"
                "        static async Task Main(string[] args)\n"
                "        {\n"
                '            Console.WriteLine("Example: email-converter");\n'
                "\n"
                '            string inputPath = "input.eml";\n'
                "            File.WriteAllText(inputPath,\n"
                '                "From: sender@example.com\\r\\n" +\n'
                '                "To: recipient@example.com\\r\\n" +\n'
                '                "Subject: LowCode Converter Test\\r\\n" +\n'
                '                "MIME-Version: 1.0\\r\\n" +\n'
                '                "Content-Type: text/plain\\r\\n\\r\\n" +\n'
                '                "Hello, this is a test email for LowCode conversion.");\n'
                "\n"
                '            string outputDir = "output_html";\n'
                "            Directory.CreateDirectory(outputDir);\n"
                "\n"
                "            using var stream = new MemoryStream(File.ReadAllBytes(inputPath));\n"
                "            string fileName = Path.GetFileName(inputPath);\n"
                "            var outputHandler = new FolderOutputHandler(outputDir);\n"
                "            await Converter.ConvertToHtml(stream, fileName, outputHandler);\n"
                "\n"
                "            Console.WriteLine(Directory.Exists(outputDir) && Directory.GetFiles(outputDir).Length > 0\n"
                '                ? $"Conversion succeeded: {outputDir}"\n'
                '                : "Conversion failed: no output files found.");\n'
                "        }\n"
                "    }\n"
                "}\n"
            )

    # Unrecognised type — fall back to the generic catalog-driven template
    return _generate_template(packet)


# ---------------------------------------------------------------------------
# Smart template helpers
# ---------------------------------------------------------------------------

_FORMAT_NAME_TO_EXT: dict[str, str] = {
    # Type-specific overrides (must appear before generic entries)
    "mailmerger": ".docx",
    "diagramconverter": ".vdx",
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
    "xls": ".xlsx",
    "spreadsheet": ".xlsx",
    "excel": ".xlsx",
    "docx": ".docx",
    "word": ".docx",
    "doc": ".docx",
    "vdx": ".vdx",
    "vsdx": ".vsdx",
    "diagram": ".vsdx",
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
    """Infer output file extension from type name.

    Priority:
    1. FormatContract (API-backed authority) — if family hint is available
    2. Legacy _FORMAT_NAME_TO_EXT (deprecated compatibility)
    3. hints fallback
    """
    # Priority 1: FormatContract authority
    family = (hints or {}).get("family", "")
    if family:
        try:
            from plugin_examples.format_authority.store import get_contract

            contract = get_contract(family, type_name)
            return contract.canonical_output_format
        except ImportError:
            pass
        # NOTE: MissingFormatContractError (KeyError subclass) is NOT caught here — fail closed.

    # Priority 2: Legacy map (DEPRECATED — compatibility only)
    name_lower = type_name.lower()
    if name_lower in _FORMAT_NAME_TO_EXT:
        return _FORMAT_NAME_TO_EXT[name_lower]

    for suffix in ("converter", "merger", "splitter", "locker", "compressor", "signer"):
        if name_lower.endswith(suffix):
            token = name_lower[: -len(suffix)]
            if token in _FORMAT_NAME_TO_EXT:
                return _FORMAT_NAME_TO_EXT[token]
            break

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


def _generate_smart_args(
    parameters: list[dict], type_name: str, hints: dict | None = None, use_basedir: bool = False
) -> str | None:
    """Generate argument string for a method call. Returns None if unsupported.

    Args:
        use_basedir: If True, wrap input file references in Path.Combine(AppContext.BaseDirectory, ...).
    """
    args: list[str] = []
    ext = _infer_output_extension(type_name, hints)
    default_input = hints.get("default_input_filename", "input.xlsx") if hints else "input.xlsx"
    array_inputs = (
        hints.get("array_input_filenames", ["input1.xlsx", "input2.xlsx"]) if hints else ["input1.xlsx", "input2.xlsx"]
    )

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
            args.append(f"new string[] {{ {array_str} }}")
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


def _generate_method_call(
    type_name: str,
    method: dict,
    kind: str,
    hints: dict | None = None,
    instance_declared: bool = False,
    use_basedir: bool = False,
) -> list[str]:
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
            if ptype in ("System.String", "String") and any(kw in pname for kw in ("template", "input", "source")):
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
    match = re.search(r"```(?:csharp|cs)\s*\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Try any generic code block that looks like C#
    for m in re.finditer(r"```\s*\n(.*?)```", response, re.DOTALL):
        code = m.group(1).strip()
        if "using " in code or "namespace " in code or "class " in code:
            return code
    # If response itself looks like C# code, use it directly
    stripped = response.strip()
    if stripped and ("using " in stripped or "namespace " in stripped or "static void Main" in stripped):
        return stripped
    # Return empty — generation failed to produce code
    return ""


def _validate_code_from_constraints(code: str, type_constraints: dict) -> list[str]:
    """Validate generated code against REQUIRED and FORBIDDEN patterns from per_type_constraints.

    REQUIRED: checks primary LowCode API calls (method calls) and critical using directives.
    FORBIDDEN: checks for banned API substitutions, but skips the check when the complementary
               LowCode call is present — this allows support/fixture code that happens to use
               a non-LowCode API alongside the required LowCode call.

    Design principle: avoid false positives on REQUIRED_SUPPORTING_DEPENDENCY usage.
    A FORBIDDEN pattern is only flagged when the required LowCode call is absent,
    indicating the forbidden API has replaced the LowCode API entirely.
    """
    issues = []

    # --- Parse REQUIRED entries ---
    required_calls: list[tuple[str, str]] = []  # (method_token, full_entry)
    required_usings: list[tuple[str, str]] = []  # (using_stmt, full_entry)

    for req in type_constraints.get("required", []):
        # Extract pattern: strip "REQUIRED:" and remove explanation suffix (" — " or " (")
        req_stripped = req.replace("REQUIRED:", "").strip()
        for sep in (" — ", " ("):
            if sep in req_stripped:
                req_stripped = req_stripped.split(sep)[0].strip()
                break

        if req_stripped.startswith("using "):
            # Using directive: check literal presence (normalize to end with semicolon)
            using_stmt = req_stripped.rstrip(";") + ";"
            required_usings.append((using_stmt, req))
        elif "(" in req_stripped and len(req_stripped) >= 5:
            # Method/constructor call: extract token up to first "("
            # Handles static calls "Converter.Convert(...)" → token "Converter.Convert"
            # AND instance calls "new Merger().Process(...)" → token "new Merger"
            token = req_stripped.split("(")[0].strip()
            if token and len(token) >= 4:
                required_calls.append((token, req))
        elif len(req_stripped) >= 4:
            # Literal string check — pattern must appear verbatim in generated code.
            # Use this for filename/value constraints (e.g. "output.jpg") where a
            # method-call token would be too broad and would produce false positives.
            required_calls.append((req_stripped, req))

    # Check REQUIRED using directives — must appear literally in code
    for using_stmt, req_entry in required_usings:
        if using_stmt not in code:
            issues.append(f"Missing required using directive: {req_entry}")

    # Check REQUIRED method calls — primary LowCode API must be present
    for call_token, req_entry in required_calls:
        if call_token not in code:
            issues.append(f"Missing required LowCode API call: {req_entry}")

    # --- FORBIDDEN check ---
    # If the required LowCode call IS present, a forbidden pattern in the same code
    # is likely fixture/support code — exempt it to avoid false positives.
    has_required_lowcode_call = any(token in code for token, _ in required_calls)

    for forb in type_constraints.get("forbidden", []):
        forb_stripped = forb.replace("FORBIDDEN:", "").strip()
        first_token = forb_stripped.split("(")[0].split(" ")[0].strip()
        if not first_token or len(first_token) < 4:
            continue
        if first_token not in code:
            continue
        # Forbidden token present — skip if the required LowCode call is also present
        # (forbidden API is being used for fixture/support, not as a substitute)
        if has_required_lowcode_call:
            continue
        issues.append(f"Uses forbidden pattern: {forb}")

    return issues


def _validate_code(code: str, family: str = "", type_short: str = "") -> list[str]:
    """Validate generated code for common issues."""
    issues = []

    if "TODO" in code:
        issues.append("Contains TODO placeholder")

    if "NotImplementedException" in code:
        issues.append("Contains NotImplementedException")

    if re.search(r"[A-Z]:\\", code):
        issues.append("Contains hardcoded absolute path")

    if "Version=" in code and "<PackageReference" in code:
        issues.append("Contains inline package version")

    # Forbidden interactive patterns
    if "Console.ReadKey(" in code:
        issues.append("Contains Console.ReadKey() — forbidden in headless CI. Remove it.")

    if "Console.ReadLine(" in code:
        issues.append("Contains Console.ReadLine() — forbidden in headless CI. Remove it.")

    # Forbidden options misuse patterns
    if re.search(r"\(LowCodeLoadOptions\)\s*null", code):
        issues.append(
            "Passes null for LowCodeLoadOptions — this causes NullReferenceException. "
            "Use the simple string-path overload instead, or create a LowCodeLoadOptions "
            "with InputFile set."
        )

    if re.search(r"\(LowCodeSaveOptions\)\s*null", code):
        issues.append(
            "Passes null for LowCodeSaveOptions — this causes NullReferenceException. "
            "Use the simple string-path overload instead, or create a LowCodeSaveOptions "
            "with OutputFile set."
        )

    # Detect empty LowCodeLoadOptions without InputFile assignment
    if re.search(r"new\s+LowCodeLoadOptions\s*\(\s*\)", code):
        if ".InputFile" not in code and ".InputStream" not in code:
            issues.append(
                "Creates LowCodeLoadOptions without setting InputFile or InputStream. "
                "You MUST set InputFile before passing to Process(), or use the simple "
                "string-path overload instead."
            )

    # Detect empty LowCodeSaveOptions without OutputFile assignment
    if re.search(r"new\s+LowCodeSaveOptions\s*\(\s*\)", code):
        if ".OutputFile" not in code and ".OutputStream" not in code:
            issues.append(
                "Creates LowCodeSaveOptions without setting OutputFile or OutputStream. "
                "You MUST set OutputFile before passing to Process(), or use the simple "
                "string-path overload instead."
            )

    # Detect multiple Process() calls — should use only one overload
    process_calls = re.findall(r"\b\w+\.Process\s*\(", code)
    if len(process_calls) > 1:
        issues.append(
            f"Contains {len(process_calls)} Process() calls — use only ONE overload per example. "
            "Remove the extra Process() calls and keep only the simplest string-path overload."
        )

    # PDF-specific validation rules
    if family == "pdf":
        if "new FileSaveTarget(" in code:
            issues.append(
                "PDF: uses FileSaveTarget for output — WRONG type. "
                "AddOutput() takes IDataSource. Use new FileDataSource(path) instead."
            )
        if ".IsSuccess" in code:
            issues.append(
                "PDF: uses result.IsSuccess — property does not exist on ResultContainer. "
                "Use result.ResultCollection.Count > 0 instead."
            )
        if ".OperationResult" in code:
            issues.append(
                "PDF: uses result.OperationResult — property does not exist on ResultContainer. "
                "Use result.ResultCollection instead."
            )
        if re.search(r"output_\{0\}\.pdf|output_\{[0-9]+\}\.pdf", code):
            issues.append(
                "PDF Splitter: uses format string in output filename (e.g. 'output_{0}.pdf'). "
                "Splitter does not expand format strings — use plain 'output.pdf' instead."
            )
        if "TextExtractor" in code and "AddOutput(" in code:
            issues.append(
                "PDF TextExtractor: calls AddOutput() — TextExtractor has no file output. "
                "Remove AddOutput() and read result from result.ResultCollection[0] as StringResult."
            )
        # Html plugin: TextFragment is NEVER valid — input must be an HTML file, not a PDF
        if type_short.lower() == "html" and "TextFragment" in code:
            issues.append(
                "HTML plugin MUST NOT use TextFragment — Html plugin converts HTML to PDF. "
                'Input MUST be an HTML file created with File.WriteAllText("input.html", htmlContent). '
                "Do NOT use Aspose.Pdf.Document or TextFragment for input creation."
            )
        # Html plugin: must not create PDF input (Document fixture is for PDF-input plugins only)
        if type_short.lower() == "html" and re.search(r"new\s+(Aspose\.Pdf\.)?Document\s*\(", code):
            issues.append(
                "HTML plugin MUST NOT create a PDF Document fixture. "
                "Html plugin converts HTML->PDF, so input is an HTML file. "
                'Create input with: File.WriteAllText("input.html", "<html><body><h1>Hello</h1></body></html>");'
            )
        # Html plugin: must not use input.pdf as input
        if type_short.lower() == "html" and "input.pdf" in code and "output.pdf" not in code.replace("input.pdf", ""):
            # allow output.pdf but not input.pdf as input
            if re.search(r'FileDataSource\s*\(\s*"input\.pdf"', code):
                issues.append(
                    "HTML plugin: AddInput must receive 'input.html', NOT 'input.pdf'. "
                    "Html plugin takes HTML file as input, not PDF."
                )
        if "input.docx" in code or '"input.docx"' in code:
            issues.append(
                "PDF: references input.docx — PDF LowCode requires .pdf input files. "
                "Create input with 'new Aspose.Pdf.Document(); doc.Save(\"input.pdf\")' and use 'input.pdf'."
            )
        if "InputPath" in code or "OutputPath" in code:
            issues.append(
                "PDF: uses InputPath/OutputPath properties — PDF LowCode options use AddInput()/AddOutput() methods. "
                "Replace '.InputPath =' with '.AddInput(new FileDataSource(...))' "
                "and '.OutputPath =' with '.AddOutput(new FileDataSource(...))'."
            )
        # Check that non-TextExtractor types actually use AddInput
        if "TextExtractor" not in code and "AddInput(" not in code:
            issues.append(
                'PDF: missing AddInput() call — options must have AddInput(new FileDataSource("input.pdf")) '
                "before calling Process()."
            )
        # Detect use of abstract PluginOptions base class instead of concrete options class
        if "new PluginOptions(" in code or "new PluginOptions{" in code or "new PluginOptions " in code:
            issues.append(
                "PDF: uses 'new PluginOptions()' — PluginOptions is abstract. "
                "Use the concrete options class: MergeOptions, SplitOptions, OptimizeOptions, or TextExtractorOptions."
            )
        # Detect hallucinated LowCodePluginOptions class (does not exist)
        if "LowCodePluginOptions" in code:
            issues.append(
                "PDF: uses 'LowCodePluginOptions' — this class does not exist. "
                "Use the concrete options class: MergeOptions, SplitOptions, OptimizeOptions, or TextExtractorOptions."
            )
        # Detect AddInput/AddOutput called with plain string (must use FileDataSource)
        if re.search(r"\.AddInput\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)", code) or re.search(
            r'\.AddInput\s*\(\s*"[^"]*"\s*\)', code
        ):
            # Only flag if FileDataSource is absent — string-arg form doesn't exist in PDF LowCode
            if "FileDataSource" not in code:
                issues.append(
                    "PDF: AddInput() called with a plain string — must use FileDataSource: "
                    'AddInput(new FileDataSource("input.pdf")). The string overload does not exist.'
                )
        # Detect wrong Process() overload (string array)
        if re.search(r"\.Process\s*\(\s*new\s*\[\s*\]", code):
            issues.append(
                "PDF: calls Process() with a string array — use the options object overload: "
                "Process(IPluginOptions). Create a MergeOptions/SplitOptions/etc, call AddInput()/AddOutput(), "
                "then call plugin.Process(options)."
            )
        # Detect TextExtractor called without TextExtractorOptions
        if "TextExtractor" in code and "TextExtractorOptions" not in code:
            issues.append(
                "PDF TextExtractor: must instantiate TextExtractorOptions and call Process(options). "
                'Example: var options = new TextExtractorOptions(); options.AddInput(new FileDataSource("input.pdf")); '
                "var result = new TextExtractor().Process(options);"
            )
        # Detect TextAbsorber usage — this is the CORE PDF API, not the LowCode API
        if "TextAbsorber" in code:
            issues.append(
                "PDF: uses TextAbsorber (Aspose.Pdf.Text namespace) — this is the CORE PDF API, NOT the LowCode API. "
                "Replace with Aspose.Pdf.LowCode.TextExtractor + TextExtractorOptions: "
                "var options = new TextExtractorOptions(); "
                'options.AddInput(new FileDataSource("input.pdf")); '
                "var result = new TextExtractor().Process(options); "
                "Console.WriteLine(((StringResult)result.ResultCollection[0]).Text);"
            )
        # Detect fake local class definitions that shadow real LowCode plugin classes
        if re.search(r"^\s*class\s+(Merger|Splitter|Optimizer|TextExtractor)\b", code, re.MULTILINE):
            issues.append(
                "PDF: defines a local class with the same name as a real Aspose.Pdf.LowCode plugin class. "
                "Remove the local class — use the imported Aspose.Pdf.LowCode class directly."
            )
        # Detect wrong StringResult property access (.Value does not exist — use .Text)
        if "TextExtractor" in code and re.search(r"ResultCollection\s*\[\s*\d+\s*\]\s*\.Value", code):
            issues.append(
                "PDF TextExtractor: accesses result.ResultCollection[0].Value — StringResult has no .Value property. "
                "Cast and use .Text instead: ((StringResult)result.ResultCollection[0]).Text"
            )
        # Detect TextFragment usage without required 'using Aspose.Pdf.Text'
        # Allow the fully-qualified name Aspose.Pdf.Text.TextFragment as an alternative to the using directive
        if (
            "TextFragment" in code
            and "using Aspose.Pdf.Text" not in code
            and "Aspose.Pdf.Text.TextFragment" not in code
        ):
            issues.append(
                "PDF: uses TextFragment but is missing 'using Aspose.Pdf.Text;' directive. "
                "Add 'using Aspose.Pdf.Text;' at the top of the file, or use the fully-qualified name Aspose.Pdf.Text.TextFragment."
            )
        # Detect hallucinated sub-namespace Aspose.Pdf.LowCode.DataSources — does not exist
        if "Aspose.Pdf.LowCode.DataSources" in code:
            issues.append(
                "PDF: uses 'using Aspose.Pdf.LowCode.DataSources;' — this sub-namespace does NOT exist in the Aspose.PDF assembly. "
                "FileDataSource lives in Aspose.Pdf.LowCode. Remove the sub-namespace using directive; "
                "'using Aspose.Pdf.LowCode;' already covers FileDataSource."
            )
        # Detect File.Copy as semantic substitute for any PDF LowCode operation — FORBIDDEN
        if re.search(r"\bFile\.Copy\s*\(", code):
            issues.append(
                "PDF: uses File.Copy() — this is NOT a LowCode operation and does not demonstrate the Aspose API. "
                "You MUST use the LowCode plugin class (Merger, Splitter, Optimizer, TextExtractor) "
                "with its concrete options class (MergeOptions, SplitOptions, OptimizeOptions, TextExtractorOptions) "
                "and call plugin.Process(options)."
            )
        # Optimizer-specific: require OptimizeOptions
        if type_short == "optimizer" and "OptimizeOptions" not in code:
            issues.append(
                "PDF Optimizer: must use 'OptimizeOptions' — do NOT use any other class. "
                'var options = new OptimizeOptions(); options.AddInput(new FileDataSource("input.pdf")); '
                'options.AddOutput(new FileDataSource("output.pdf")); var result = new Optimizer().Process(options);'
            )
        # Optimizer-specific: require Optimizer().Process pattern
        if type_short == "optimizer" and not re.search(r"new\s+Optimizer\s*\(\s*\)\s*\.Process\s*\(", code):
            issues.append(
                "PDF Optimizer: must call 'new Optimizer().Process(options)' — the Optimizer class must be instantiated "
                "and its Process() method called with an OptimizeOptions instance."
            )

    return issues
