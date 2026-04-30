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


def build_packet(
    scenario: dict,
    catalog: dict,
    *,
    prompt_template: str | None = None,
    template_hints: dict | None = None,
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
            f"Scenario {scenario.get('scenario_id')} references unknown symbols: "
            f"{', '.join(unknown)}"
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
        "Print a deterministic success line like: Console.WriteLine(\"Done. Output: \" + outputPath);",
        "Validate that the input file exists before calling the plugin API: "
        "if (!File.Exists(inputPath)) throw new FileNotFoundException(inputPath);",
        "Call ONLY ONE overload of each LowCode API — the simplest string-path overload. "
        "Do NOT demonstrate multiple overloads in a single example.",
        "NEVER pass null for LowCodeLoadOptions or LowCodeSaveOptions parameters.",
        "If you use LowCodeLoadOptions, you MUST set its InputFile property before passing it to Process().",
        "If you use LowCodeSaveOptions, you MUST set its OutputFile property before passing it to Process().",
    ]

    # Add input-strategy-specific constraints
    fixture_instruction = _build_fixture_instruction(input_strategy, input_files)

    system_prompt = (
        "You are an expert C# developer. Generate a complete, runnable SDK-style "
        "console application example that demonstrates the specified API. "
        "Use only the symbols provided in the API catalog. "
        "The example must compile and run without errors in a headless CI environment. "
        "FORBIDDEN patterns: Console.ReadKey(), Console.ReadLine(), TODO, NotImplementedException, "
        "passing null for LowCodeLoadOptions/LowCodeSaveOptions. "
        "REQUIRED: validate input file exists before API call, validate output exists after, "
        "print deterministic success output. "
        "CRITICAL: Call only ONE overload of each API — the simplest string-path overload. "
        "Do NOT demonstrate multiple overloads. "
        "Return ONLY the C# source code inside a single ```csharp code block. "
        "Do not include any markdown, explanations, or text outside the code block."
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
            f"Use Path.Combine(AppContext.BaseDirectory, \"{input_files[0]}\") to reference them.\n"
            f"Do NOT create these files in code — they already exist.\n"
            f"Do NOT reference any other input files not listed here."
        )
    elif input_strategy == "existing_fixture" and input_files:
        files_list = ", ".join(input_files)
        return (
            f"\nINPUT FILES: The following fixture files are provided in the project directory: {files_list}\n"
            f"Use Path.Combine(AppContext.BaseDirectory, \"{input_files[0]}\") to reference them.\n"
            f"Do NOT create these files in code — they already exist.\n"
            f"Do NOT reference any other input files not listed here."
        )
    elif input_strategy == "programmatic_input":
        return (
            "\nINPUT STRATEGY: Create any required input data programmatically before "
            "calling the plugin API. Use the Aspose API (e.g., new Workbook()) to create "
            "input files. Verify the file exists and is non-empty before passing it to the "
            "plugin API. Do NOT reference files that are not created in the code."
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
        'if (!File.Exists(inputPath))\n'
        '    throw new FileNotFoundException("Input fixture not found", inputPath);\n'
        "\n"
        '// Define output path\n'
        'string outputPath = Path.Combine(AppContext.BaseDirectory, "output.xlsx");\n'
        "\n"
        "// Call the plugin API\n"
        "// TypeName.Process(inputPath, outputPath);\n"
        "\n"
        "// Validate output\n"
        'if (File.Exists(outputPath))\n'
        '    Console.WriteLine($"Done. Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");\n'
        "else\n"
        '    throw new InvalidOperationException("Output file was not created");\n'
        "```\n"
    )


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
            if prop.get("can_read"): access.append("get")
            if prop.get("can_write"): access.append("set")
            prompt_parts.append(f"  Property: {prop.get('type', '')} {prop['name']} {{ {'; '.join(access)} }}")
        # Methods
        for m in type_details.get("methods", []):
            params = ", ".join(f"{p['type']} {p['name']}" for p in m.get("parameters", []))
            static = "static " if m.get("is_static") else ""
            prompt_parts.append(f"  Method: {static}{m.get('return_type', 'void')} {m['name']}({params})")

    prompt_parts.append("\nIMPORTANT: Call ONLY ONE overload of each method — the simplest string-path "
                       "overload. Do NOT demonstrate multiple overloads. Do NOT pass null for "
                       "LowCodeLoadOptions or LowCodeSaveOptions. If the simplest overload has "
                       "only string parameters, use that one. Only use the constructors, methods, "
                       "and properties listed above.")

    return "\n".join(prompt_parts)
