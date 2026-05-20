"""Validate generated Program.cs against FormatContract authority."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ContractValidationResult:
    """Result of validating generated code against a FormatContract."""

    valid: bool = True
    checks: list[dict] = field(default_factory=list)

    def add_check(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append({"check": name, "passed": passed, "detail": detail})
        if not passed:
            self.valid = False


_OUTPUT_PATTERN = re.compile(r'"output\.(\w+)"')
_INPUT_PATTERN = re.compile(r'"input\.(\w+)"')


def validate_code_against_contract(
    code: str,
    contract: dict,
) -> ContractValidationResult:
    """Validate generated C# code against a FormatContract.

    Args:
        code: Program.cs source code.
        contract: FormatContract as dict (from contract.to_dict()).

    Returns:
        ContractValidationResult with individual check results.
    """
    result = ContractValidationResult()
    canonical_output = contract.get("canonical_output_format", "")
    expected_input = contract.get("input_format", "")
    output_kind = contract.get("output_kind", "file")

    # Check 1: No .out in code
    if '"output.out"' in code or "'output.out'" in code:
        result.add_check("no_dot_out", False, "Code contains output.out — fallback format detected")
    else:
        result.add_check("no_dot_out", True)

    # Check 2: Output extension matches contract (for file output types)
    if output_kind == "file" and canonical_output:
        output_matches = _OUTPUT_PATTERN.findall(code)
        if output_matches:
            # Check if canonical output extension (without dot) appears in output filenames
            expected_ext = canonical_output.lstrip(".")
            found_correct = any(ext == expected_ext for ext in output_matches)
            if found_correct:
                result.add_check("output_extension_match", True,
                                 f"Found output.{expected_ext} matching contract")
            else:
                result.add_check("output_extension_match", False,
                                 f"Expected output.{expected_ext}, found output.{output_matches[0]}")
        else:
            # Some types don't have explicit output.ext (e.g., directory output)
            result.add_check("output_extension_match", True,
                             "No explicit output filename pattern found — skipped")

    elif output_kind == "stdout":
        # stdout types should NOT have AddOutput or output file creation
        if "AddOutput" in code:
            result.add_check("stdout_no_output", False,
                             "stdout type should not call AddOutput()")
        else:
            result.add_check("stdout_no_output", True)

    elif output_kind == "directory":
        result.add_check("directory_output", True, "Directory output type — format check skipped")

    # Check 3: Input extension matches contract
    if expected_input:
        input_matches = _INPUT_PATTERN.findall(code)
        if input_matches:
            expected_in_ext = expected_input.lstrip(".")
            found_correct = any(ext == expected_in_ext for ext in input_matches)
            if found_correct:
                result.add_check("input_extension_match", True,
                                 f"Found input.{expected_in_ext} matching contract")
            else:
                result.add_check("input_extension_match", False,
                                 f"Expected input.{expected_in_ext}, found input.{input_matches[0]}")
        else:
            result.add_check("input_extension_match", True,
                             "No explicit input filename pattern — skipped")

    # Check 4: Same-format converter guard
    op_kind = contract.get("operation_kind", "")
    if op_kind == "converter" and canonical_output and expected_input:
        if canonical_output == expected_input:
            # Same-format converter is suspicious — check contract explicitly allows it
            result.add_check("same_format_converter_guard", False,
                             f"Converter has same input ({expected_input}) and output ({canonical_output}) — contract mismatch")
        else:
            result.add_check("same_format_converter_guard", True)

    return result
