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
    """Generate a template example without LLM."""
    methods_code = []
    for method in packet.target_methods[:3]:
        methods_code.append(f"    // Demonstrate {packet.target_type}.{method}")
        methods_code.append(f"    {packet.target_type}.{method}();")

    methods_str = "\n".join(methods_code) if methods_code else "    // No methods to demonstrate"

    return f"""using System;
using {packet.target_namespace};

namespace PluginExample
{{
    class Program
    {{
        static void Main(string[] args)
        {{
            Console.WriteLine("Example: {packet.scenario_id}");

{methods_str}

            Console.WriteLine("Done.");
        }}
    }}
}}
"""


def _extract_code(response: str) -> str:
    """Extract C# code from LLM response."""
    # Try to find code block
    match = re.search(r'```(?:csharp|cs)?\s*\n(.*?)```', response, re.DOTALL)
    if match:
        return match.group(1).strip()
    # If no code block, return entire response
    return response.strip()


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

    return issues
