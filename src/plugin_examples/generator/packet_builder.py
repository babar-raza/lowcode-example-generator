"""Build constrained prompt packets for LLM example generation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class UnknownSymbolError(Exception):
    """Raised when a scenario references symbols not in the catalog."""


@dataclass
class PromptPacket:
    """Constrained prompt packet for LLM generation."""

    scenario_id: str
    target_type: str
    target_namespace: str
    target_methods: list[str] = field(default_factory=list)
    approved_symbols: list[str] = field(default_factory=list)
    fixture_files: list[str] = field(default_factory=list)
    output_plan: str = ""
    constraints: list[str] = field(default_factory=list)
    system_prompt: str = ""
    user_prompt: str = ""
    type_details: dict = field(default_factory=dict)
    template_hints: dict = field(default_factory=dict)
    input_strategy: str = "none"
    input_files: list[str] = field(default_factory=list)
    per_type_constraints: dict = field(default_factory=dict)
    format_contract: dict = field(default_factory=dict)  # FormatContract as dict


def build_packet(
    scenario: dict,
    catalog: dict,
    *,
    prompt_template: str | None = None,
    template_hints: dict | None = None,
    per_type_constraints: dict | None = None,
) -> PromptPacket:
    """Build a constrained prompt packet from a scenario.

    Validates that all required symbols exist in the catalog before
    allowing LLM generation.

    Args:
        scenario: Scenario dict from scenario catalog.
        catalog: API catalog dict.
        prompt_template: Optional custom prompt template.

    Returns:
        PromptPacket ready for LLM generation.

    Raises:
        UnknownSymbolError: If scenario references unknown symbols.
    """
    catalog_symbols = _build_catalog_symbols(catalog)
    required_symbols = scenario.get("required_symbols", [])

    # Validate all symbols exist
    unknown = [s for s in required_symbols if s not in catalog_symbols]
    if unknown:
        raise UnknownSymbolError(
            f"Scenario {scenario.get('scenario_id')} references unknown symbols: " f"{', '.join(unknown)}"
        )

    target_type = scenario.get("target_type", "")
    target_ns = scenario.get("target_namespace", "")
    methods = scenario.get("target_methods", [])

    # Build approved symbol context from catalog
    approved = _get_type_details(catalog, target_type)

    input_strategy = scenario.get("input_strategy", "none")
    input_files = scenario.get("input_files", [])

    constraints = [
        "Use only symbols from the approved API catalog",
        "Do not use TODO placeholders",
        "Do not use NotImplementedException",
        "Do not hardcode absolute file paths",
        "Use PackageReference without inline version numbers",
        "Create a complete, runnable SDK-style console application",
        "Do not reference input.xlsx, input.csv, input.json, input.html, or input.txt "
        "unless the file is created programmatically in the code or listed as a provided fixture",
        "Do not assume any files exist in the working directory unless explicitly provided",
        "Do NOT use Console.ReadKey() or Console.ReadLine() — the example runs headless in CI",
        "Do NOT use any interactive console input methods",
        "Do NOT wrap the plugin API call in try/catch that silently swallows exceptions",
        "After calling the plugin API, validate that the output file exists and print its size",
        'Print a deterministic success line like: Console.WriteLine("Done. Output: " + outputPath);',
        "Validate that the input file exists before calling the plugin API: "
        "if (!File.Exists(inputPath)) throw new FileNotFoundException(inputPath);",
        "Demonstrate ONLY the single primary API method for this scenario — the FIRST method "
        "listed in 'Methods to demonstrate'. Use only its simplest string-path overload. "
        "Do NOT attempt to demonstrate every listed method. One method, one overload, one clean example.",
        "NEVER pass null for LowCodeLoadOptions or LowCodeSaveOptions parameters.",
        "If you use LowCodeLoadOptions, you MUST set its InputFile property before passing it to Process().",
        "If you use LowCodeSaveOptions, you MUST set its OutputFile property before passing it to Process().",
    ]

    # Add input-strategy-specific constraints
    fixture_instruction = _build_fixture_instruction(input_strategy, input_files)

    # Detect family from namespace
    ns_lower = target_ns.lower()
    is_pdf = ns_lower.startswith("aspose.pdf")
    type_short = target_type.split(".")[-1].lower() if target_type else ""

    # Detect family name for programmatic fixture guidance
    _family_name = ""
    if ns_lower.startswith("aspose.diagram"):
        _family_name = "diagram"
    elif ns_lower.startswith("aspose.email"):
        _family_name = "email"
    elif ns_lower.startswith("aspose.slides"):
        _family_name = "slides"

    # Inject family-specific programmatic fixture guidance
    fixture_constraints, fixture_appendix = _build_programmatic_fixture_guidance(
        _family_name,
        type_short,
        input_strategy,
    )
    if fixture_constraints:
        constraints.extend(fixture_constraints)
    if fixture_appendix:
        fixture_instruction += fixture_appendix

    if is_pdf:
        constraints += [
            "FORBIDDEN: File.Copy() or System.IO.File.Copy() — this is NOT a LowCode operation. You MUST use the LowCode plugin class and its Process(options) method.",
            "FORBIDDEN: new FileSaveTarget(path) — use new FileDataSource(path) for AddOutput()",
            "FORBIDDEN: result.IsSuccess — use result.ResultCollection.Count > 0",
            "FORBIDDEN: result.OperationResult — use result.ResultCollection",
            "FORBIDDEN: format strings in output filename (e.g. 'output_{0}.pdf') — use plain 'output.pdf'",
            "FORBIDDEN: InputPath or OutputPath properties on any options object — use AddInput() and AddOutput() methods",
            "FORBIDDEN: defining your own class stubs or fake implementations — use only the real Aspose API",
            "FORBIDDEN: defining a local class named Merger, Splitter, Optimizer, or TextExtractor — these are real Aspose.Pdf.LowCode classes; do NOT shadow them with local definitions",
            "FORBIDDEN: input.docx — PDF LowCode always uses .pdf files, never .docx",
            "FORBIDDEN: new PluginOptions() — PluginOptions is an abstract base; use the concrete options class for this type",
            "FORBIDDEN: LowCodePluginOptions — this class does not exist; use the concrete options class (MergeOptions, SplitOptions, OptimizeOptions, TextExtractorOptions)",
            'FORBIDDEN: AddInput(string) or AddOutput(string) with a plain string path — always wrap in FileDataSource: AddInput(new FileDataSource("input.pdf"))',
            "FORBIDDEN: string array overloads of Process() — always use the options object overload Process(IPluginOptions)",
            "FORBIDDEN: using Aspose.Pdf.LowCode.DataSources — this sub-namespace does NOT exist. FileDataSource lives in Aspose.Pdf.LowCode. Use 'using Aspose.Pdf.LowCode;' only.",
            "REQUIRED: always include 'using Aspose.Pdf.LowCode;'",
            "REQUIRED: use instance-method pattern — create plugin instance first: 'var plugin = new XxxPlugin(); plugin.Process(options)'",
        ]
        if type_short == "html":
            constraints += [
                "REQUIRED: Html plugin converts HTML -> PDF. Input MUST be an HTML file, NOT a PDF.",
                'REQUIRED: create HTML input file: File.WriteAllText("input.html", "<html><body><h1>Hello</h1></body></html>");',
                "REQUIRED: use HtmlToPdfOptions as the options class (NOT PluginOptions, NOT PdfConverterOptions)",
                'REQUIRED: options.AddInput(new FileDataSource("input.html")) — HTML file as input',
                'REQUIRED: options.AddOutput(new FileDataSource("output.pdf")) — PDF file as output',
                "REQUIRED: new Html().Process(options) — use the LowCode Html plugin",
                "FORBIDDEN: new Aspose.Pdf.Document() for Html plugin — no PDF fixture needed; input is HTML",
                "FORBIDDEN: TextFragment for Html plugin — input is an HTML string, not a PDF document",
                'FORBIDDEN: AddInput(new FileDataSource("input.pdf")) — Html plugin takes HTML file input, NOT PDF',
                "FORBIDDEN: HtmlLoadOptions — use HtmlToPdfOptions (LowCode namespace)",
            ]
        else:
            constraints += [
                "REQUIRED: always include 'using Aspose.Pdf;' (for Document/TextFragment fixture creation)",
                "REQUIRED: create input PDF programmatically in code before calling the API:\n"
                "    var doc = new Aspose.Pdf.Document();\n"
                "    doc.Pages.Add();\n"
                '    doc.Save("input.pdf");',
                'REQUIRED: use AddInput(new FileDataSource("input.pdf")) to set the input on the options object',
            ]
        # Per-type exact class name hints — prevent hallucination of wrong options class
        _pdf_type_hints = {
            "merger": (
                "MergeOptions",
                "Merger",
                "var options = new MergeOptions();\n"
                '    options.AddInput(new FileDataSource("input.pdf"));\n'
                '    options.AddOutput(new FileDataSource("output.pdf"));\n'
                "    var result = new Merger().Process(options);",
            ),
            "splitter": (
                "SplitOptions",
                "Splitter",
                "var options = new SplitOptions();\n"
                '    options.AddInput(new FileDataSource("input.pdf"));\n'
                '    options.AddOutput(new FileDataSource("output.pdf"));\n'
                "    var result = new Splitter().Process(options);",
            ),
            "optimizer": (
                "OptimizeOptions",
                "Optimizer",
                "var options = new OptimizeOptions();\n"
                '    options.AddInput(new FileDataSource("input.pdf"));\n'
                '    options.AddOutput(new FileDataSource("output.pdf"));\n'
                "    var result = new Optimizer().Process(options);",
            ),
            "textextractor": (
                "TextExtractorOptions",
                "TextExtractor",
                "var options = new TextExtractorOptions();\n"
                '    options.AddInput(new FileDataSource("input.pdf"));\n'
                "    var result = new TextExtractor().Process(options);\n"
                "    if (result.ResultCollection.Count > 0 && result.ResultCollection[0] is StringResult sr)\n"
                '        Console.WriteLine("Extracted: " + sr.Text);',
            ),
        }
        if type_short in _pdf_type_hints:
            opts_class, plugin_class, code_snippet = _pdf_type_hints[type_short]
            constraints += [
                f"REQUIRED: options class is '{opts_class}' — do NOT use any other class name",
                f"REQUIRED: plugin class is '{plugin_class}' — do NOT use any other class name",
                f"REQUIRED: exact usage pattern:\n    {code_snippet}",
            ]

        if type_short == "textextractor":
            constraints += [
                "FORBIDDEN: TextAbsorber — TextAbsorber is in Aspose.Pdf.Text and is the CORE (non-LowCode) API. NEVER use TextAbsorber in a LowCode example.",
                "FORBIDDEN: pdfDoc.Pages.Accept(absorber) — this is the core PDF API pattern, not LowCode",
                "FORBIDDEN: AddOutput() call for TextExtractor — result is in ResultCollection, not a file",
                "REQUIRED: 'using Aspose.Pdf.Text;' ONLY for TextFragment creation (input PDF). The extraction MUST use Aspose.Pdf.LowCode.TextExtractor.",
                "REQUIRED: check result with 'if (result.ResultCollection.Count > 0 && result.ResultCollection[0] is StringResult sr)'",
                "REQUIRED: access extracted text as 'sr.Text'",
                "FORBIDDEN: result.ResultCollection[0].Value — StringResult has no .Value property; use .Text (via cast or pattern match)",
                "REQUIRED: add 'using Aspose.Pdf.Text;' if you use TextFragment to build the input PDF",
            ]
        else:
            constraints += [
                'REQUIRED: use AddOutput(new FileDataSource("output.pdf")) to set the output on the options object',
            ]

    # Inject FormatContract authority constraint if available
    _format_contract_dict: dict = {}
    _type_name = target_type.split(".")[-1] if target_type else ""
    _fc_family = scenario.get("format_contract_id", "").split("/")[0] if scenario.get("format_contract_id") else ""
    if not _fc_family:
        # Infer family from namespace
        _ns = target_ns.lower()
        for _fam in ("cells", "words", "pdf", "diagram", "email", "slides"):
            if _fam in _ns:
                _fc_family = _fam
                break
    if _fc_family and _type_name:
        try:
            from plugin_examples.format_authority.store import get_contract

            _fc = get_contract(_fc_family, _type_name)
            _format_contract_dict = _fc.to_dict()
            _fc_out = _fc.canonical_output_format
            _fc_in = _fc.input_format
            _fc_kind = _fc.output_kind
            constraints.append(
                f"FORMAT CONTRACT (API-backed authority): "
                f"input={_fc_in}, output={_fc_out}, output_kind={_fc_kind}. "
                f"Your generated code MUST use output extension '{_fc_out}' — "
                f"do NOT use any other output extension."
            )
            if _fc_kind == "stdout":
                constraints.append(
                    "FORMAT CONTRACT: This type produces stdout output, NOT a file. "
                    "Do NOT use AddOutput() or create an output file."
                )
            elif _fc_kind == "directory":
                constraints.append("FORMAT CONTRACT: This type produces directory output via FolderOutputHandler.")
        except (KeyError, ImportError):
            pass

    # Inject config-driven per_type_constraints for the target type (all families)
    if per_type_constraints and _type_name in per_type_constraints:
        type_cfg = per_type_constraints[_type_name]
        for req in type_cfg.get("required", []):
            if req not in constraints:
                constraints.append(req)
        for forb in type_cfg.get("forbidden", []):
            if forb not in constraints:
                constraints.append(forb)
        logger.debug(
            "Injected %d per_type_constraints for %s from family config",
            len(type_cfg.get("required", [])) + len(type_cfg.get("forbidden", [])),
            _type_name,
        )

    system_prompt = (
        "You are an expert C# developer. Generate a complete, runnable SDK-style "
        "console application example that demonstrates the specified API. "
        "Use only the symbols provided in the API catalog. "
        "The example must compile and run without errors in a headless CI environment. "
        "FORBIDDEN patterns: Console.ReadKey(), Console.ReadLine(), TODO, NotImplementedException, "
        "passing null for LowCodeLoadOptions/LowCodeSaveOptions. "
        "REQUIRED: validate input file exists before API call, validate output exists after, "
        "print deterministic success output. "
        "CRITICAL: Demonstrate ONLY the single primary method (the FIRST in the provided list) "
        "using its simplest string-path overload. Do NOT demonstrate multiple methods or overloads. "
        "Return ONLY the C# source code inside a single ```csharp code block. "
        "Do not include any markdown, explanations, or text outside the code block."
        + (
            " PDF LowCode API rules: "
            "NEVER define your own class stubs — use only the real Aspose.Pdf.LowCode namespace. "
            "AddOutput() takes FileDataSource (IDataSource) — NOT FileSaveTarget (ISaveTarget). "
            "Check success with result.ResultCollection.Count > 0 (no IsSuccess property). "
            "Use instance-method pattern: new Plugin().Process(options). "
            "Options have AddInput()/AddOutput() methods — NOT InputPath/OutputPath properties. "
            "Always create input PDF programmatically with new Aspose.Pdf.Document() before calling API. "
            "TextExtractor: no AddOutput(), result is StringResult in ResultCollection."
            if is_pdf
            else (
                " Diagram LowCode API rules: "
                "Create input VSDX using Aspose.Diagram.Diagram() with Shape objects — NOT raw ZIP bytes. "
                "PdfConverter.Process(inputPath, outputPath) converts Visio to PDF. "
                "DiagramConverter.Process(inputPath, outputPath) converts Visio to Visio formats ONLY (VDX, VSDX, VSD). "
                "DiagramConverter does NOT support PDF, SVG, or PNG output. "
                "Core Aspose.Diagram API is allowed ONLY for creating the input fixture."
                if _family_name == "diagram"
                else ""
            )
        )
    )

    user_prompt = _build_user_prompt(scenario, approved, prompt_template, fixture_instruction)

    return PromptPacket(
        scenario_id=scenario.get("scenario_id", ""),
        target_type=target_type,
        target_namespace=target_ns,
        target_methods=methods,
        approved_symbols=required_symbols,
        fixture_files=scenario.get("required_fixtures", []),
        output_plan=scenario.get("output_plan", ""),
        constraints=constraints,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        type_details=approved,
        template_hints=template_hints or {},
        input_strategy=input_strategy,
        input_files=input_files,
        per_type_constraints=per_type_constraints or {},
        format_contract=_format_contract_dict,
    )


def _build_catalog_symbols(catalog: dict) -> set[str]:
    """Build set of all known symbols."""
    symbols: set[str] = set()
    for ns in catalog.get("namespaces", []):
        symbols.add(ns["namespace"])
        for t in ns.get("types", []):
            symbols.add(t["full_name"])
            for m in t.get("methods", []):
                symbols.add(f"{t['full_name']}.{m['name']}")
    return symbols


def _get_type_details(catalog: dict, full_name: str) -> dict:
    """Get detailed type information from catalog."""
    for ns in catalog.get("namespaces", []):
        for t in ns.get("types", []):
            if t["full_name"] == full_name:
                return t
    return {}


def _build_fixture_instruction(input_strategy: str, input_files: list[str]) -> str:
    """Build fixture instruction block for the LLM prompt."""
    if input_strategy == "generated_fixture_file" and input_files:
        files_list = ", ".join(input_files)
        return (
            f"\nINPUT FILES: The following input files are provided in the project directory "
            f"and will be available at runtime via AppContext.BaseDirectory: {files_list}\n"
            f'Use Path.Combine(AppContext.BaseDirectory, "{input_files[0]}") to reference them.\n'
            f"Do NOT create these files in code — they already exist.\n"
            f"Do NOT reference any other input files not listed here."
        )
    elif input_strategy == "existing_fixture" and input_files:
        files_list = ", ".join(input_files)
        return (
            f"\nINPUT FILES: The following fixture files are provided in the project directory: {files_list}\n"
            f'Use Path.Combine(AppContext.BaseDirectory, "{input_files[0]}") to reference them.\n'
            f"Do NOT create these files in code — they already exist.\n"
            f"Do NOT reference any other input files not listed here."
        )
    elif input_strategy == "programmatic_input":
        return (
            "\nINPUT STRATEGY: Create any required input data programmatically before "
            "calling the plugin API. Use the product's core Aspose API to create a valid "
            "input file. Do NOT write raw bytes, do NOT create empty placeholder files, "
            "do NOT use File.WriteAllBytes with byte arrays. "
            "Verify the file exists and is non-empty before passing it to the "
            "plugin API. Do NOT reference files that are not created in the code. "
            "Structure your code in three sections: "
            "(1) INPUT FIXTURE CREATION — create the input file using the core product API, "
            "(2) LOWCODE OPERATION — call the LowCode API for the operation under test, "
            "(3) OUTPUT VALIDATION — verify the output file exists and print its size."
        )
    return ""


def _build_fewshot_snippet(input_strategy: str, input_files: list[str]) -> str:
    """Build a compact few-shot code pattern from verified passing examples."""
    if input_strategy != "generated_fixture_file" or not input_files:
        return ""

    filename = input_files[0]
    return (
        "\nREFERENCE PATTERN (from a verified passing example):\n"
        "```csharp\n"
        "// Locate input file from project output directory\n"
        f'string inputPath = Path.Combine(AppContext.BaseDirectory, "{filename}");\n'
        "if (!File.Exists(inputPath))\n"
        '    throw new FileNotFoundException("Input fixture not found", inputPath);\n'
        "\n"
        "// Define output path\n"
        'string outputPath = Path.Combine(AppContext.BaseDirectory, "output.xlsx");\n'
        "\n"
        "// Call the plugin API\n"
        "// TypeName.Process(inputPath, outputPath);\n"
        "\n"
        "// Validate output\n"
        "if (File.Exists(outputPath))\n"
        '    Console.WriteLine($"Done. Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");\n'
        "else\n"
        '    throw new InvalidOperationException("Output file was not created");\n'
        "```\n"
    )


# ---------------------------------------------------------------------------
# Family-scoped programmatic fixture guidance registry
# ---------------------------------------------------------------------------
# Each entry teaches the LLM how to create valid input files using the
# product's core API (allowed for fixture setup only) and how to call the
# LowCode API for the operation under test.
# To add a new family: add an entry keyed by family name.

_PROGRAMMATIC_FIXTURE_GUIDANCE: dict[str, dict] = {
    "diagram": {
        "fixture_code": (
            "// Create a valid VSDX input file using Aspose.Diagram (core API — allowed for fixture setup only)\n"
            "// DURABLE FIX: use page.DrawEllipse() which returns long shapeId — do NOT use new Shape() or TypeValue\n"
            "var diagram = new Aspose.Diagram.Diagram();\n"
            "var page = diagram.Pages[0];\n"
            "long shapeId = page.DrawEllipse(1.0, 1.0, 2.0, 2.0);\n"
            "var shape = page.Shapes.GetShape(shapeId);\n"
            "if (shape != null)\n"
            "{\n"
            '    shape.Name = "SampleShape";\n'
            "    // XForm properties are DoubleValue objects — set via .Value, not direct assignment\n"
            "    shape.XForm.PinX.Value = 2.0;\n"
            "    shape.XForm.PinY.Value = 2.0;\n"
            "    shape.XForm.Width.Value = 1.0;\n"
            "    shape.XForm.Height.Value = 1.0;\n"
            "}\n"
            "diagram.Save(inputPath, Aspose.Diagram.SaveFileFormat.Vsdx);"
        ),
        "operation_examples": {
            "pdfconverter": (
                "// LowCode operation: convert VSDX to PDF\n"
                "Aspose.Diagram.LowCode.PdfConverter.Process(inputPath, outputPath);\n"
                "// outputPath must end in .pdf"
            ),
            "diagramconverter": (
                "// LowCode operation: convert VSDX to another Visio format\n"
                "Aspose.Diagram.LowCode.DiagramConverter.Process(inputPath, outputPath);\n"
                "// outputPath must end in a Visio format (.vdx, .vsdx, .vsd)\n"
                "// DiagramConverter does NOT support PDF, SVG, or PNG output"
            ),
        },
        "forbidden_patterns": [
            "FORBIDDEN: File.WriteAllBytes() with raw byte arrays to create VSDX — this creates invalid files. Use Aspose.Diagram.Diagram() API to create valid VSDX.",
            "FORBIDDEN: creating empty placeholder .vsdx files — always use Aspose.Diagram.Diagram() programmatic creation.",
            "FORBIDDEN: fake or dummy binary content for input files.",
            "FORBIDDEN: using DiagramConverter for PDF output — DiagramConverter only supports Visio formats (VDX, VSDX, VSD). Use PdfConverter for PDF output.",
            "FORBIDDEN: using core Aspose.Diagram API for the conversion operation — the conversion MUST use the LowCode API (Aspose.Diagram.LowCode namespace).",
            "FORBIDDEN: new Aspose.Diagram.Shape() with .Type = TypeValue.Shape — TypeValue.Shape does not exist; use page.DrawEllipse() instead.",
            "FORBIDDEN: shape.XForm.PinX = 2.0 — PinX is DoubleValue, not double; use shape.XForm.PinX.Value = 2.0.",
        ],
        "required_patterns": [
            "REQUIRED: create input VSDX using page.DrawEllipse(x,y,w,h) which returns long shapeId.",
            "REQUIRED: retrieve shape via page.Shapes.GetShape(shapeId) and set XForm.PinX.Value, PinY.Value, Width.Value, Height.Value.",
            "REQUIRED: save input as VSDX using diagram.Save(path, Aspose.Diagram.SaveFileFormat.Vsdx).",
            "REQUIRED: include 'using Aspose.Diagram;' for fixture creation and 'using Aspose.Diagram.LowCode;' for the LowCode operation.",
            "REQUIRED: structure code in three sections: (1) INPUT FIXTURE CREATION using core API, (2) LOWCODE OPERATION using LowCode namespace, (3) OUTPUT VALIDATION.",
        ],
    },
    "pdf": {
        "fixture_code": (
            "// Create a PDF input file using Aspose.Pdf (core API — allowed for fixture setup only)\n"
            "var doc = new Aspose.Pdf.Document();\n"
            "var page = doc.Pages.Add();\n"
            'page.Paragraphs.Add(new Aspose.Pdf.Text.TextFragment("LowCode PDF Example"));\n'
            'doc.Save("input.pdf");'
        ),
        "operation_examples": {
            "docconverter": (
                "// LowCode operation: convert PDF to DOCX (OOXML format)\n"
                "var options = new PdfToDocOptions();\n"
                "options.SaveFormat = SaveFormat.DocX;  // DocX = OOXML .docx; Doc = OLE2 .doc\n"
                'options.AddInput(new FileDataSource("input.pdf"));\n'
                'options.AddOutput(new FileDataSource("output.docx"));\n'
                "var result = new DocConverter().Process(options);\n"
                "// result.ResultCollection.Count > 0 on success\n"
                "// CRITICAL: PdfConverterOptions is abstract — use PdfToDocOptions"
            ),
            "xlsconverter": (
                "// LowCode operation: convert PDF to XLSX\n"
                "var options = new PdfToXlsOptions();\n"
                "options.Format = PdfToXlsOptions.ExcelFormat.XLSX;  // nested enum\n"
                'options.AddInput(new FileDataSource("input.pdf"));\n'
                'options.AddOutput(new FileDataSource("output.xlsx"));\n'
                "var result = new XlsConverter().Process(options);\n"
                "// result.ResultCollection.Count > 0 on success\n"
                "// CRITICAL: ExcelFormat is PdfToXlsOptions.ExcelFormat (nested), NOT ExcelFormat directly"
            ),
            "html": (
                "// LowCode operation: convert HTML to PDF\n"
                "// CRITICAL: Html plugin converts HTML -> PDF. Input MUST be an HTML file, NOT a PDF!\n"
                "// Step 1: Create HTML input file (no Aspose.Pdf.Document needed for Html plugin)\n"
                'System.IO.File.WriteAllText("input.html",\n'
                '    "<html><body><h1>Hello LowCode</h1><p>HTML to PDF.</p></body></html>");\n'
                "// Step 2: Convert HTML to PDF using LowCode Html plugin\n"
                "var options = new HtmlToPdfOptions();\n"
                'options.AddInput(new FileDataSource("input.html"));\n'
                'options.AddOutput(new FileDataSource("output.pdf"));\n'
                "var result = new Html().Process(options);\n"
                "// result.ResultCollection.Count > 0 on success"
            ),
        },
        # Types whose operation example includes its own input fixture (skip general PDF fixture)
        "self_sufficient_op_types": {"html"},
        "forbidden_patterns": [
            "FORBIDDEN: new PdfConverterOptions() — PdfConverterOptions is abstract; use PdfToDocOptions for DocConverter or PdfToXlsOptions for XlsConverter.",
            "FORBIDDEN: using core Document.Save() to replace LowCode conversion operations.",
            "FORBIDDEN: new PluginOptions() — PluginOptions is abstract; use the concrete options class.",
            "FORBIDDEN: FileSaveTarget as AddOutput argument — use FileDataSource(path) instead.",
            "FORBIDDEN: result.IsSuccess — no IsSuccess property; use result.ResultCollection.Count > 0.",
            "FORBIDDEN: for Html plugin: using input.pdf as input — Html plugin requires an HTML file as input.",
            "FORBIDDEN: for Html plugin: using HtmlLoadOptions or new Document(htmlPath) — use HtmlToPdfOptions with the LowCode Html plugin.",
        ],
        "required_patterns": [
            "REQUIRED: use the concrete options class for the target type (PdfToDocOptions, PdfToXlsOptions, HtmlToPdfOptions, etc.).",
            "REQUIRED: options.AddInput(new FileDataSource(path)) — add input via AddInput with FileDataSource.",
            "REQUIRED: options.AddOutput(new FileDataSource(path)) — add output via AddOutput with FileDataSource.",
            "REQUIRED: result.ResultCollection.Count > 0 to verify success.",
            "REQUIRED: for DocConverter: set options.SaveFormat = SaveFormat.DocX for OOXML .docx output.",
            "REQUIRED: for XlsConverter: set options.Format = PdfToXlsOptions.ExcelFormat.XLSX for OOXML .xlsx output.",
            "REQUIRED: for Html plugin: create HTML input file with System.IO.File.WriteAllText before calling Process.",
        ],
    },
}


def _build_programmatic_fixture_guidance(
    family: str,
    type_short: str,
    input_strategy: str,
) -> tuple[list[str], str]:
    """Build family-specific fixture creation guidance for programmatic_input scenarios.

    Returns:
        Tuple of (constraints_to_add, fixture_instruction_appendix).
    """
    if input_strategy != "programmatic_input":
        return [], ""
    guidance = _PROGRAMMATIC_FIXTURE_GUIDANCE.get(family)
    if not guidance:
        return [], ""

    constraints: list[str] = []
    constraints.extend(guidance.get("forbidden_patterns", []))
    constraints.extend(guidance.get("required_patterns", []))

    # Build fixture instruction with code example
    parts: list[str] = []

    # Add type-specific operation example first (may contain self-sufficient fixture)
    op_examples = guidance.get("operation_examples", {})
    op_code = op_examples.get(type_short.lower(), "")

    # Types whose operation example is self-sufficient (no separate fixture needed)
    self_sufficient_op_types = guidance.get("self_sufficient_op_types", set())
    skip_default_fixture = type_short.lower() in self_sufficient_op_types

    fixture_code = guidance.get("fixture_code", "")
    if fixture_code and not skip_default_fixture:
        parts.append(
            "\nPROGRAMMATIC INPUT FIXTURE — REFERENCE PATTERN (use this exact approach):\n"
            "```csharp\n"
            f"{fixture_code}\n"
            "```"
        )

    if op_code:
        label = (
            "\nCOMPLETE EXAMPLE — REFERENCE PATTERN (this type uses its own input creation, not the PDF fixture above):\n"
            if skip_default_fixture
            else "\nLOWCODE OPERATION — REFERENCE PATTERN:\n"
        )
        parts.append(f"{label}" "```csharp\n" f"{op_code}\n" "```")

    return constraints, "\n".join(parts)


def _build_user_prompt(
    scenario: dict,
    type_details: dict,
    template: str | None,
    fixture_instruction: str = "",
) -> str:
    """Build user prompt from scenario and type details."""
    if template:
        return template

    title = scenario.get("title", "")
    target = scenario.get("target_type", "")
    methods = scenario.get("target_methods", [])
    output_plan = scenario.get("output_plan", "")
    input_strategy = scenario.get("input_strategy", "none")
    input_files = scenario.get("input_files", [])

    prompt_parts = [
        f"Generate a C# console application example: {title}",
        f"\nTarget type: {target}",
        f"Methods to demonstrate: {', '.join(methods)}",
    ]

    if output_plan:
        prompt_parts.append(f"Expected output: {output_plan}")

    if fixture_instruction:
        prompt_parts.append(fixture_instruction)

    # Add few-shot pattern from verified examples
    fewshot = _build_fewshot_snippet(input_strategy, input_files)
    if fewshot:
        prompt_parts.append(fewshot)

    if type_details:
        prompt_parts.append(f"\nType details: {type_details.get('name', '')} ({type_details.get('kind', 'class')})")
        # Constructors
        constructors = type_details.get("constructors", [])
        if constructors:
            for ctor in constructors:
                ctor_params = ", ".join(f"{p['type']} {p['name']}" for p in ctor.get("parameters", []))
                prompt_parts.append(f"  Constructor: new {type_details.get('name', '')}({ctor_params})")
        else:
            prompt_parts.append(f"  No public constructors (may be abstract or static-only)")
        # Properties
        for prop in type_details.get("properties", [])[:10]:
            access = []
            if prop.get("can_read"):
                access.append("get")
            if prop.get("can_write"):
                access.append("set")
            prompt_parts.append(f"  Property: {prop.get('type', '')} {prop['name']} {{ {'; '.join(access)} }}")
        # Methods
        for m in type_details.get("methods", []):
            params = ", ".join(f"{p['type']} {p['name']}" for p in m.get("parameters", []))
            static = "static " if m.get("is_static") else ""
            prompt_parts.append(f"  Method: {static}{m.get('return_type', 'void')} {m['name']}({params})")

    prompt_parts.append(
        "\nIMPORTANT: Demonstrate ONLY the FIRST method listed in 'Methods to demonstrate' "
        "above. Use its simplest string-path overload. Do NOT call other methods from "
        "the list — they are shown for catalog context only. Do NOT pass null for "
        "LowCodeLoadOptions or LowCodeSaveOptions. Only use the constructors, methods, "
        "and properties listed above. Use valid output file extensions recognised by "
        "Aspose (e.g. '.docx', '.pdf', '.xlsx') — never use '.out' or other ambiguous extensions."
    )

    return "\n".join(prompt_parts)
